from __future__ import annotations
import math
from scipy.stats import norm
from .common import require


def solve_inventory(params: dict) -> dict:
    model = params.get("model", "eoq").lower()
    D = float(params.get("annual_demand", params.get("demand", 0)))
    S = float(params.get("ordering_cost", params.get("setup_cost", 0)))
    H = float(params.get("holding_cost", 0))
    require(all(math.isfinite(x) for x in (D, S, H)), "demand and inventory cost inputs must be finite")
    require(D > 0, "annual_demand must be > 0")
    require(S >= 0 and H > 0, "ordering_cost must be >= 0 and holding_cost must be > 0")
    if model in {"eoq", "basic_eoq"}:
        require(S > 0, "ordering_cost must be > 0 for a finite EOQ and order frequency")
        Q = math.sqrt(2*D*S/H)
        price = float(params.get("unit_cost", 0))
        require(math.isfinite(price) and price >= 0, "unit_cost must be finite and non-negative")
        return {"model":"EOQ", "EOQ":Q, "orders_per_year":D/Q, "cycle_days":365/(D/Q), "annual_ordering_cost":D/Q*S, "annual_holding_cost":Q/2*H, "annual_relevant_cost":D/Q*S+Q/2*H, "annual_purchase_cost":D*price, "assumptions":["Deterministic constant demand; instantaneous replenishment; no shortages; constant lead time; no quantity discounts."]}
    if model == "epq":
        require(S > 0, "ordering_cost must be > 0 for a finite EPQ and setup frequency")
        P = float(params.get("production_rate", 0))
        require(math.isfinite(P) and P > D, "production_rate must be finite and exceed demand rate")
        Q = math.sqrt((2*D*S/H)*(P/(P-D)))
        return {"model":"EPQ", "EPQ":Q, "maximum_inventory":Q*(1-D/P), "annual_setup_cost":D/Q*S, "annual_holding_cost":Q*(1-D/P)/2*H, "assumptions":["Constant finite production rate greater than demand rate."]}
    if model in {"reorder_point", "rop", "safety_stock"}:
        lead = float(params.get("lead_time_days", 0)); days = float(params.get("working_days", 365))
        require(math.isfinite(lead) and math.isfinite(days) and lead >= 0 and days > 0, "lead_time_days must be finite and >= 0; working_days must be finite and > 0")
        daily = D/days
        mean_lt = float(params.get("mean_demand_during_lead_time", daily*lead))
        sd_lt = float(params.get("sd_demand_during_lead_time", 0))
        if "service_z" in params:
            z = float(params["service_z"])
        else:
            service_level=float(params.get("service_level", .95))
            require(math.isfinite(service_level) and 0 < service_level < 1, "service_level must be finite and between 0 and 1")
            z=float(norm.ppf(service_level))
        require(math.isfinite(mean_lt) and mean_lt >= 0 and math.isfinite(sd_lt) and sd_lt >= 0, "lead-time demand mean and standard deviation must be finite and non-negative")
        ss = z*sd_lt
        return {"model":"Reorder Point", "daily_demand":daily, "safety_stock":ss, "reorder_point":mean_lt+ss, "assumptions":["Safety stock uses a normal approximation for demand during lead time; provide its standard deviation directly."]}
    raise ValueError("model must be eoq, epq, or reorder_point")
