from __future__ import annotations

import math
from collections import defaultdict, deque

from .common import require


def solve_mrp(mps, bom, inventory=None, scheduled_receipts=None, lead_times=None, lot_sizes=None):
    inventory = inventory or {}
    scheduled_receipts = scheduled_receipts or {}
    lead_times = lead_times or {}
    lot_sizes = lot_sizes or {}
    normalized_mps = {str(item): series for item, series in mps.items()}
    require(normalized_mps and len(normalized_mps) == len(mps), "MPS must contain unique item identifiers")
    normalized_bom = {str(parent): children for parent, children in bom.items()}
    require(len(normalized_bom) == len(bom), "BOM must contain unique parent item identifiers")

    items = set(normalized_mps)
    for parent, children in normalized_bom.items():
        items.add(parent)
        for child in children:
            items.add(str(child["item"]))

    periods = max((len(series) for series in normalized_mps.values()), default=0)
    require(periods > 0, "MPS must contain at least one period")

    # Validate BOM structure and create a topological item order.
    children_map = {parent: children for parent, children in normalized_bom.items()}
    indegree = {item: 0 for item in items}
    for parent, children in children_map.items():
        for child in children:
            child_name = str(child["item"])
            require(child_name in indegree, "BOM references an invalid child item")
            indegree[child_name] += 1
    queue = deque(item for item, degree in indegree.items() if degree == 0)
    order = []
    while queue:
        item = queue.popleft()
        order.append(item)
        for child in children_map.get(item, []):
            child_name = str(child["item"])
            indegree[child_name] -= 1
            if indegree[child_name] == 0:
                queue.append(child_name)
    require(len(order) == len(items), "BOM contains a cycle")

    gross = defaultdict(lambda: [0.0] * periods)
    for item, series in normalized_mps.items():
        require(len(series) == periods, "all MPS items must have the same number of periods")
        values = [float(value) for value in series]
        require(all(math.isfinite(value) and value >= 0 for value in values), "MPS values must be finite and non-negative")
        gross[item] = values

    normalized_inventory = {str(item): value for item, value in inventory.items()}
    normalized_receipts = {str(item): value for item, value in scheduled_receipts.items()}
    normalized_leads = {str(item): value for item, value in lead_times.items()}
    normalized_lot_sizes = {str(item): value for item, value in lot_sizes.items()}

    results = {}
    for item in order:
        requirements = gross[item]
        on_hand = float(normalized_inventory.get(item, 0))
        receipts = [float(value) for value in normalized_receipts.get(item, [0] * periods)]
        require(
            len(receipts) == periods
            and math.isfinite(on_hand)
            and on_hand >= 0
            and all(math.isfinite(value) and value >= 0 for value in receipts),
            "scheduled receipts must be finite, non-negative, and match the planning periods; inventory must be finite and non-negative",
        )
        lead_raw = normalized_leads.get(item, 0)
        lead = int(lead_raw)
        require(lead >= 0 and float(lead_raw) == lead, "lead time must be a non-negative whole number")
        rule = normalized_lot_sizes.get(item, {"rule": "LFL"})
        rule_name = str(rule.get("rule", "LFL")).upper()
        fixed = float(rule.get("quantity", 0))
        require(math.isfinite(fixed), "fixed lot quantity must be finite")

        projected = []
        net = []
        planned_receipt = [0.0] * periods
        planned_release = [0.0] * periods
        available = on_hand
        for period in range(periods):
            available += receipts[period] - requirements[period]
            need = max(0.0, -available)
            if need > 1e-9:
                if rule_name in {"LFL", "LOT_FOR_LOT"}:
                    quantity = need
                elif rule_name in {"FOQ", "FIXED"} and fixed > 0:
                    quantity = math.ceil(need / fixed) * fixed
                else:
                    quantity = None
                require(quantity is not None, "lot size must be LFL or FOQ with positive quantity")
                planned_receipt[period] = quantity
                available += quantity
                release_period = period - lead
                if release_period >= 0:
                    planned_release[release_period] += quantity
            net.append(need)
            projected.append(available)

        results[item] = {
            "gross_requirements": requirements,
            "scheduled_receipts": receipts,
            "projected_available": projected,
            "net_requirements": net,
            "planned_order_receipts": planned_receipt,
            "planned_order_releases": planned_release,
            "lead_time": lead,
        }
        for child in children_map.get(item, []):
            child_name = str(child["item"])
            usage = float(child["quantity"])
            require(math.isfinite(usage) and usage > 0, "BOM quantities must be finite and > 0")
            for period, quantity in enumerate(planned_release):
                gross[child_name][period] += quantity * usage

    return {
        "periods": periods,
        "items": results,
        "assumptions": [
            "Time-phased BOM explosion; parent planned order releases generate child gross requirements in the same period.",
            "Orders released before period 1 are not shifted into the planning horizon; they are visible as missing lead-time offset and should be expedited outside this horizon.",
            "Only lot-for-lot (LFL) and fixed order quantity (FOQ) are supported.",
        ],
    }
