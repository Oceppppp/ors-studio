from __future__ import annotations
import numpy as np
from scipy.optimize import linprog
from .common import require


def solve_zero_sum(payoff_matrix):
    A=np.asarray(payoff_matrix,dtype=float);require(A.ndim==2 and A.shape[0]>=2 and A.shape[1]>=2 and np.isfinite(A).all(),"payoff_matrix must be a finite matrix of at least 2x2")
    row_mins=A.min(axis=1);col_max=A.max(axis=0);maximin=float(row_mins.max());minimax=float(col_max.min())
    saddle=abs(maximin-minimax)<1e-8
    # Shift payoffs positive and solve the standard reciprocal-value LPs.
    shift=max(0,-float(A.min())+1)
    B=A+shift;m,n=B.shape
    # Row player: minimize sum(y), subject to B.T @ y >= 1. Then p=y/sum(y).
    res=linprog(np.ones(m),A_ub=-B.T,b_ub=-np.ones(n),bounds=(0,None),method="highs")
    require(res.success,f"mixed strategy solve failed: {res.message}")
    p=res.x/res.fun
    payoff=1/res.fun-shift
    # Column player: minimize sum(z), subject to B @ z <= 1. Then q=z/sum(z).
    r=linprog(-np.ones(n),A_ub=B,b_ub=np.ones(m),bounds=(0,None),method="highs")
    require(r.success and r.fun < -1e-12, f"column-player mixed-strategy solve failed: {r.message}")
    q=r.x/(-r.fun)
    return {"maximin":maximin,"minimax":minimax,"has_saddle_point":saddle,"saddle_value":maximin if saddle else None,"row_player_strategy":p.tolist(),"column_player_strategy":q.tolist() if q is not None else None,"game_value":float(payoff),"assumptions":["Two-player zero-sum game; rows maximize the payoff and columns minimize it.","Mixed strategies are solved by linear programming; dominance reduction is not explicitly shown."]}
