from __future__ import annotations
import numpy as np
from scipy.optimize import linprog
from .common import require, rounded


def _validate(costs, supply, demand):
    c = np.asarray(costs, dtype=float); s = np.asarray(supply, dtype=float); d = np.asarray(demand, dtype=float)
    require(c.ndim == 2 and c.size > 0 and len(s) > 0 and len(d) > 0 and c.shape == (len(s), len(d)), "cost matrix, supply, and demand must be non-empty and dimensions must match")
    require((s >= 0).all() and (d >= 0).all(), "supply and demand must be non-negative")
    require(np.isfinite(c).all() and np.isfinite(s).all() and np.isfinite(d).all(), "all inputs must be finite")
    if s.sum() > d.sum():
        c = np.column_stack([c, np.zeros(len(s))]); d = np.append(d, s.sum()-d.sum())
    elif d.sum() > s.sum():
        c = np.row_stack([c, np.zeros(len(d))]); s = np.append(s, d.sum()-s.sum())
    return c, s, d


def _initial(costs, supply, demand, method):
    c, s, d = costs.copy(), supply.copy(), demand.copy()
    m, n = c.shape; alloc = np.zeros((m, n)); active_rows, active_cols = set(range(m)), set(range(n))
    while active_rows and active_cols:
        if method == "northwest":
            i, j = min(active_rows), min(active_cols)
        else:
            candidates = []
            for i0 in active_rows:
                for j0 in active_cols:
                    candidates.append((c[i0,j0], i0, j0))
            if method == "least_cost":
                _, i, j = min(candidates)
            elif method == "vogel":
                penalties = []
                for i0 in active_rows:
                    vals = sorted(c[i0, list(active_cols)])
                    penalty = vals[1]-vals[0] if len(vals)>1 else vals[0]
                    penalties.append((penalty, "r", i0, min(active_cols, key=lambda j0:c[i0,j0])))
                for j0 in active_cols:
                    vals = sorted(c[list(active_rows), j0])
                    penalty = vals[1]-vals[0] if len(vals)>1 else vals[0]
                    penalties.append((penalty, "c", j0, min(active_rows, key=lambda i0:c[i0,j0])))
                _, axis, index, other = max(penalties)
                i, j = (index, other) if axis == "r" else (other, index)
            else:
                raise ValueError("method must be northwest, least_cost, or vogel")
        q = min(s[i], d[j]); alloc[i,j] = q; s[i] -= q; d[j] -= q
        if s[i] <= 1e-9: active_rows.discard(i)
        if d[j] <= 1e-9: active_cols.discard(j)
        if not active_rows and active_cols:
            break
        if not active_cols and active_rows:
            break
    return alloc


def solve_transportation(costs, supply, demand, method="vogel") -> dict:
    c, s, d = _validate(costs, supply, demand)
    require(method in {"northwest", "least_cost", "vogel", "optimal"}, "unsupported transportation method")
    if method == "optimal":
        m, n = c.shape
        A_eq, b_eq = [], []
        for i in range(m):
            row = np.zeros(m*n); row[i*n:(i+1)*n] = 1; A_eq.append(row); b_eq.append(s[i])
        for j in range(n):
            row = np.zeros(m*n); row[j::n] = 1; A_eq.append(row); b_eq.append(d[j])
        result = linprog(c.flatten(), A_eq=A_eq, b_eq=b_eq, bounds=(0,None), method="highs")
        require(result.success, f"Transportation optimization failed: {result.message}")
        alloc = result.x.reshape(m,n)
    else:
        alloc = _initial(c,s,d,method)
    return {"method": method, "allocation": rounded(alloc.tolist()), "total_cost": round(float((alloc*c).sum()),6), "balanced_supply": rounded(s.tolist()), "balanced_demand": rounded(d.tolist()), "assumptions": ["Unbalanced problems are balanced with a zero-cost dummy destination/source.", "Northwest, Least Cost, and VAM give initial feasible solutions and are not guaranteed optimal.", "Use method='optimal' for an LP-optimal solution."]}
