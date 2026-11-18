from __future__ import annotations

import math

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

from .common import require, rounded


def _matrix(constraints, variable_count):
    a_ub, b_ub, a_eq, b_eq = [], [], [], []
    for index, item in enumerate(constraints or []):
        coefficients = np.asarray(item.get("coefficients", []), dtype=float)
        require(
            coefficients.ndim == 1 and len(coefficients) == variable_count and np.isfinite(coefficients).all(),
            f"constraint {index + 1} must have {variable_count} finite coefficients",
        )
        rhs = float(item.get("rhs", 0))
        require(math.isfinite(rhs), f"constraint {index + 1} RHS must be finite")
        sense = item.get("sense", "<=")
        if sense == "<=":
            a_ub.append(coefficients.tolist())
            b_ub.append(rhs)
        elif sense == ">=":
            a_ub.append((-coefficients).tolist())
            b_ub.append(-rhs)
        elif sense == "=":
            a_eq.append(coefficients.tolist())
            b_eq.append(rhs)
        else:
            raise ValueError(f"Invalid constraint sense: {sense}")
    return (
        np.asarray(a_ub, dtype=float) if a_ub else None,
        np.asarray(b_ub, dtype=float) if b_ub else None,
        np.asarray(a_eq, dtype=float) if a_eq else None,
        np.asarray(b_eq, dtype=float) if b_eq else None,
    )


def _validated_bounds(bounds, variable_count, *, default_nonnegative=True):
    if bounds is None:
        if default_nonnegative:
            return [(0.0, None)] * variable_count
        return [(None, None)] * variable_count
    require(len(bounds) == variable_count, "bounds must have one entry per variable")
    validated = []
    for index, pair in enumerate(bounds):
        require(isinstance(pair, (list, tuple)) and len(pair) == 2, f"bounds[{index}] must be [lower, upper]")
        lower = None if pair[0] is None else float(pair[0])
        upper = None if pair[1] is None else float(pair[1])
        require(lower is None or math.isfinite(lower), f"lower bound for variable {index + 1} must be finite or null")
        require(upper is None or math.isfinite(upper), f"upper bound for variable {index + 1} must be finite or null")
        require(lower is None or upper is None or lower <= upper, f"lower bound exceeds upper bound for variable {index + 1}")
        validated.append((lower, upper))
    return validated


def solve_linear_program(objective, constraints, sense="min", bounds=None) -> dict:
    c = np.asarray(objective, dtype=float)
    require(c.ndim == 1 and len(c) > 0 and np.isfinite(c).all(), "objective must be a non-empty finite vector")
    require(sense in {"min", "max"}, "sense must be 'min' or 'max'")
    a_ub, b_ub, a_eq, b_eq = _matrix(constraints, len(c))
    model_bounds = _validated_bounds(bounds, len(c))
    result = linprog(c if sense == "min" else -c, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=model_bounds, method="highs")
    statuses = {0: "optimal", 1: "iteration_limit", 2: "infeasible", 3: "unbounded", 4: "solver_error"}
    output = {"status": statuses.get(result.status, "solver_error"), "message": result.message, "sense": sense}
    if result.success:
        objective_value = float(np.dot(c, result.x))
        output.update({
            "variables": rounded(result.x.tolist()),
            "objective": round(objective_value, 6),
            "inequality_slacks": rounded(result.ineqlin.residual.tolist() if a_ub is not None else []),
            "equality_residuals": rounded(result.eqlin.residual.tolist() if a_eq is not None else []),
            "inequality_marginals": rounded(result.ineqlin.marginals.tolist() if a_ub is not None else []),
            "equality_marginals": rounded(result.eqlin.marginals.tolist() if a_eq is not None else []),
        })
    output["assumptions"] = [
        "Continuous linear programming solved with SciPy HiGHS.",
        "Variable bounds default to non-negativity when omitted.",
        "Dual values are solver marginals under SciPy/HiGHS sign conventions.",
    ]
    return output


def solve_integer_program(objective, constraints, integrality=None, sense="min", bounds=None) -> dict:
    c = np.asarray(objective, dtype=float)
    require(c.ndim == 1 and len(c) > 0 and np.isfinite(c).all(), "objective must be a non-empty finite vector")
    require(sense in {"min", "max"}, "sense must be 'min' or 'max'")
    a_ub, b_ub, a_eq, b_eq = _matrix(constraints, len(c))
    rows, lower_constraints, upper_constraints = [], [], []
    if a_ub is not None:
        rows.extend(a_ub)
        lower_constraints.extend([-np.inf] * len(a_ub))
        upper_constraints.extend(b_ub)
    if a_eq is not None:
        rows.extend(a_eq)
        lower_constraints.extend(b_eq)
        upper_constraints.extend(b_eq)
    linear_constraint = (
        LinearConstraint(np.asarray(rows), np.asarray(lower_constraints), np.asarray(upper_constraints))
        if rows else None
    )

    validated_bounds = _validated_bounds(bounds, len(c))
    lower = np.array([-np.inf if pair[0] is None else pair[0] for pair in validated_bounds], dtype=float)
    upper = np.array([np.inf if pair[1] is None else pair[1] for pair in validated_bounds], dtype=float)
    raw_integrality = np.asarray(integrality if integrality is not None else [1] * len(c), dtype=float)
    require(
        raw_integrality.ndim == 1 and len(raw_integrality) == len(c)
        and np.isfinite(raw_integrality).all()
        and np.equal(raw_integrality, np.floor(raw_integrality)).all()
        and np.isin(raw_integrality, [0, 1, 2, 3]).all(),
        "integrality must contain one code (0/1/2/3) per variable",
    )
    result = milp(
        c if sense == "min" else -c,
        integrality=raw_integrality.astype(int),
        bounds=Bounds(lower, upper),
        constraints=linear_constraint,
    )
    status = {0: "optimal", 1: "limit", 2: "infeasible", 3: "unbounded", 4: "solver_error"}.get(result.status, "solver_error")
    output = {"status": status, "message": result.message, "sense": sense}
    if result.x is not None:
        output["variables"] = rounded(result.x.tolist())
        output["objective"] = round(float(np.dot(c, result.x)), 6)
    mip_gap = getattr(result, "mip_gap", np.nan)
    output["mip_gap"] = float(mip_gap) if np.isfinite(mip_gap) else None
    output["assumptions"] = [
        "MILP solved using SciPy's HiGHS mixed-integer solver.",
        "integrality=1 means integer; integrality=0 means continuous; integrality=2/3 are semi-continuous/semi-integer.",
    ]
    return output


def solve_goal_programming(objective, goals, constraints=None, weights=None) -> dict:
    """Weighted goal programming via LP with positive/negative deviation variables."""
    base_objective = np.asarray(objective, dtype=float)
    require(base_objective.ndim == 1 and len(base_objective) > 0 and np.isfinite(base_objective).all(), "objective must be a non-empty finite vector")
    variable_count = len(base_objective)
    require(goals, "at least one goal is required")
    normalized_weights = np.asarray(weights if weights is not None else [1.0] * len(goals), dtype=float)
    require(
        normalized_weights.ndim == 1 and len(normalized_weights) == len(goals)
        and np.isfinite(normalized_weights).all() and (normalized_weights >= 0).all(),
        "weights must be finite, non-negative, and match the number of goals",
    )
    target_objective = np.concatenate([np.zeros(variable_count), normalized_weights, normalized_weights])
    equations = []
    for index, goal in enumerate(goals):
        coefficients = np.asarray(goal["coefficients"], dtype=float)
        target = float(goal["target"])
        require(
            coefficients.ndim == 1 and len(coefficients) == variable_count and np.isfinite(coefficients).all() and math.isfinite(target),
            f"goal {index + 1} must have finite coefficients and target with the expected variable count",
        )
        row = np.zeros(variable_count + 2 * len(goals))
        row[:variable_count] = coefficients
        row[variable_count + index] = 1
        row[variable_count + len(goals) + index] = -1
        equations.append({"coefficients": row.tolist(), "sense": "=", "rhs": target})
    for constraint in constraints or []:
        coefficients = np.asarray(constraint["coefficients"], dtype=float)
        require(
            coefficients.ndim == 1 and len(coefficients) == variable_count and np.isfinite(coefficients).all(),
            "goal-programming constraint coefficient count mismatch or non-finite value",
        )
        row = np.zeros(variable_count + 2 * len(goals))
        row[:variable_count] = coefficients
        equations.append({"coefficients": row.tolist(), "sense": constraint["sense"], "rhs": constraint["rhs"]})
    bounds = [(0, None)] * variable_count + [(0, None)] * (2 * len(goals))
    result = solve_linear_program(target_objective, equations, "min", bounds)
    if result.get("status") == "optimal":
        result["decision_variables"] = result["variables"][:variable_count]
        result["goal_deviations"] = [
            {"under": result["variables"][variable_count + index], "over": result["variables"][variable_count + len(goals) + index]}
            for index in range(len(goals))
        ]
    result["assumptions"] = [
        "Weighted sum of underachievement and overachievement deviations.",
        "Preemptive/lexicographic priorities are not implemented in this model.",
    ]
    return result
