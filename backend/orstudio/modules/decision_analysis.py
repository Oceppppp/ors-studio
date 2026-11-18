from __future__ import annotations
import numpy as np
from .common import require, rounded


def solve_decision_analysis(payoffs, probabilities=None) -> dict:
    a = np.asarray(payoffs, dtype=float)
    require(a.ndim == 2 and a.shape[0] > 0 and a.shape[1] > 0 and np.isfinite(a).all(), "payoffs must be a finite non-empty 2D matrix")
    criteria = {"maximax": int(np.argmax(a.max(axis=1))), "maximin": int(np.argmax(a.min(axis=1))), "minimax_regret": int(np.argmin((a.max(axis=0)-a).max(axis=1)))}
    regrets = a.max(axis=0)-a
    result = {"criteria_best_alternative_index": criteria, "regret_matrix": rounded(regrets.tolist()), "best_worst_case_payoff": float(a.min(axis=1).max()), "best_case_payoff": float(a.max(axis=1).max())}
    if probabilities is not None:
        p = np.asarray(probabilities, dtype=float)
        require(p.ndim == 1 and len(p) == a.shape[1] and np.isfinite(p).all() and (p >= 0).all() and abs(p.sum()-1) < 1e-8, "probabilities must be a finite 1D vector, non-negative, and sum to 1")
        emv = a @ p; eol = regrets @ p
        result.update({"probabilities": rounded(p.tolist()), "EMV": rounded(emv.tolist()), "EOL": rounded(eol.tolist()), "best_EMV_alternative_index": int(np.argmax(emv)), "minimum_EOL_alternative_index": int(np.argmin(eol)), "EVPI": float(np.dot(p,a.max(axis=0))-emv.max())})
    result["assumptions"] = ["Rows are alternatives, columns are states of nature; larger payoff is better.", "Alternative indices are zero-based in the API; the UI labels them starting at 1."]
    return result
