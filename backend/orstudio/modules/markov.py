from __future__ import annotations
import numpy as np
from .common import require, rounded


def solve_markov(transition_matrix, initial_state, periods=1):
    P=np.asarray(transition_matrix,dtype=float); p=np.asarray(initial_state,dtype=float)
    require(P.ndim==2 and P.shape[0]==P.shape[1] and P.shape[0]>0,"transition_matrix must be square")
    require(np.isfinite(P).all() and (P>=0).all(),"transition probabilities must be finite and non-negative")
    require(np.allclose(P.sum(axis=1),1,atol=1e-8),"each transition matrix row must sum to 1")
    require(p.ndim==1 and len(p)==P.shape[0] and np.isfinite(p).all() and (p>=0).all() and abs(p.sum()-1)<1e-8,"initial_state must be a finite 1D probability vector summing to 1")
    require(np.isfinite(periods) and float(periods).is_integer() and 0<=int(periods)<=100000,"periods must be a whole number between 0 and 100000")
    state=p @ np.linalg.matrix_power(P,int(periods))
    # Solve stationary distribution by least squares with normalization.
    A=np.vstack([P.T-np.eye(len(p)),np.ones(len(p))]); b=np.append(np.zeros(len(p)),1)
    stationary=np.linalg.lstsq(A,b,rcond=None)[0]
    if (stationary < -1e-8).any(): stationary=None
    return {"state_after_periods":rounded(state.tolist()),"periods":int(periods),"stationary_distribution":rounded(np.maximum(stationary,0).tolist()) if stationary is not None else None,"assumptions":["Row-stochastic transition matrix; state distribution is represented as a row vector.","A single stationary vector may not describe periodic/non-ergodic chains uniquely; interpret with chain structure."]}
