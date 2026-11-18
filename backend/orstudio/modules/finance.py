from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from .common import require


def solve_breakeven(fixed_cost, variable_cost_per_unit, selling_price_per_unit, target_profit=0):
    f, v, p, t = map(float, (fixed_cost, variable_cost_per_unit, selling_price_per_unit, target_profit))
    require(np.isfinite([f, v, p, t]).all(), "all break-even inputs must be finite")
    require(f >= 0 and v >= 0 and p > v, "Require fixed_cost >= 0, variable_cost >= 0, and selling_price > variable_cost")
    q = (f + t) / (p - v)
    return {
        "contribution_margin_per_unit": p - v,
        "break_even_units": f / (p - v),
        "break_even_revenue": (f / (p - v)) * p,
        "target_profit_units": q,
        "target_profit_revenue": q * p,
        "assumptions": ["Single product, constant unit price and variable cost, and fixed total fixed cost."],
    }


def solve_capital_investment(initial_investment, cash_flows, discount_rate):
    initial = float(initial_investment)
    flows = [float(x) for x in cash_flows]
    rate = float(discount_rate)
    require(np.isfinite([initial, rate, *flows]).all(), "investment, cash flows, and discount rate must be finite")
    require(initial >= 0 and len(flows) > 0 and rate > -1, "Initial investment must be >= 0, cash_flows required, and discount_rate must be > -100%")
    all_flows = [-initial] + flows
    npv = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(all_flows))

    def f(r):
        return sum(cf / ((1 + r) ** t) for t, cf in enumerate(all_flows))

    # IRR is searched on a documented finite grid. This detects sign-changing
    # roots in the range, but is not a proof that all mathematical roots exist there.
    grid = np.concatenate([np.linspace(-0.9, -0.01, 60), np.linspace(0, 1, 100), np.linspace(1.05, 10, 80)])
    roots = []
    for a, b in zip(grid[:-1], grid[1:]):
        try:
            fa, fb = f(a), f(b)
            if np.isfinite([fa, fb]).all() and fa * fb < 0:
                root = float(brentq(f, a, b))
                if not roots or abs(root - roots[-1]) > 1e-7:
                    roots.append(root)
        except (ValueError, OverflowError, ZeroDivisionError):
            continue

    cumulative = -initial
    payback = None
    discounted_cumulative = -initial
    discounted_payback = None
    for i, cf in enumerate(flows, 1):
        prev = cumulative
        cumulative += cf
        if payback is None and cumulative >= 0 and cf > 0:
            payback = (i - 1) + (-prev / cf)
        discounted_cf = cf / ((1 + rate) ** i)
        prevd = discounted_cumulative
        discounted_cumulative += discounted_cf
        if discounted_payback is None and discounted_cumulative >= 0 and discounted_cf > 0:
            discounted_payback = (i - 1) + (-prevd / discounted_cf)

    return {
        "NPV": npv,
        "IRR_roots": roots,
        "IRR": roots[0] if len(roots) == 1 else None,
        "payback_period": payback,
        "discounted_payback_period": discounted_payback,
        "assumptions": [
            "Cash flows occur at period-end.",
            "IRR sign-changing roots are searched numerically from -90% to 1000%; roots outside this range or roots without a sign change may not be detected.",
            "Multiple detected IRRs are reported as multiple roots; no single IRR is returned unless exactly one root is detected.",
            "Payback is linearly interpolated within the recovery period and assumes recovery occurs during a positive cash flow.",
        ],
    }
