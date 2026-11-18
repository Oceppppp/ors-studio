from __future__ import annotations
import numpy as np
from scipy.optimize import linear_sum_assignment
from .common import require, rounded


def solve_assignment(cost_matrix, sense: str = "min") -> dict:
    matrix = np.asarray(cost_matrix, dtype=float)
    require(matrix.ndim == 2 and matrix.size > 0, "cost_matrix must be a non-empty 2D matrix")
    require(np.isfinite(matrix).all(), "cost_matrix must contain finite numbers")
    require(sense in {"min", "max"}, "sense must be 'min' or 'max'")
    working = -matrix if sense == "max" else matrix
    rows, cols = linear_sum_assignment(working)
    assignments = [[int(r), int(c)] for r, c in zip(rows, cols)]
    total = float(matrix[rows, cols].sum())
    return {"sense": sense, "assignments": assignments, "objective": round(total, 6), "unassigned_rows": sorted(set(range(matrix.shape[0])) - set(rows.tolist())), "unassigned_columns": sorted(set(range(matrix.shape[1])) - set(cols.tolist())), "assumptions": ["Rectangular problems assign the smaller side completely; dummy rows/columns are not added automatically."]}
