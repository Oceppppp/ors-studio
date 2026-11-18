from __future__ import annotations
import numpy as np
from scipy.stats import norm
from .common import require


def xbar_r_chart(subgroups, A2=None, D3=None, D4=None):
    x=np.asarray(subgroups,dtype=float)
    require(x.ndim==2 and x.shape[0]>=2 and x.shape[1]>=2 and np.isfinite(x).all(),"subgroups must be a finite 2D array with >=2 subgroups and >=2 observations each")
    sizes=x.shape[1]; means=x.mean(axis=1); ranges=np.ptp(x,axis=1); xb=means.mean(); rb=ranges.mean()
    # Standard constants table for subgroup sizes 2..10.
    constants={2:(1.880,0,3.267),3:(1.023,0,2.574),4:(.729,0,2.282),5:(.577,0,2.114),6:(.483,0,2.004),7:(.419,.076,1.924),8:(.373,.136,1.864),9:(.337,.184,1.816),10:(.308,.223,1.777)}
    if A2 is None or D3 is None or D4 is None:
        require(sizes in constants,"provide A2, D3 and D4 for subgroup sizes outside 2..10")
        A2,D3,D4=constants[sizes]
    constants_values=[float(A2),float(D3),float(D4)]
    require(np.isfinite(constants_values).all() and constants_values[0]>=0 and constants_values[1]>=0 and constants_values[2]>=0, "control chart constants must be finite and non-negative")
    x_limits=[xb-constants_values[0]*rb,xb,xb+constants_values[0]*rb];r_limits=[constants_values[1]*rb,rb,constants_values[2]*rb]
    return {"xbar":{"center":xb,"LCL":x_limits[0],"UCL":x_limits[2],"points":means.tolist(),"out_of_control_indices":[i for i,v in enumerate(means) if v<x_limits[0] or v>x_limits[2]]},"R":{"center":rb,"LCL":r_limits[0],"UCL":r_limits[2],"points":ranges.tolist(),"out_of_control_indices":[i for i,v in enumerate(ranges) if v<r_limits[0] or v>r_limits[2]]},"assumptions":["Subgroup size is constant; standard 3-sigma constants; limits assume a stable process and rational subgroups."]}


def p_chart(defectives, sample_sizes, sigma=3):
    d=np.asarray(defectives,dtype=float); n=np.asarray(sample_sizes,dtype=float)
    require(d.ndim==1 and len(d)==len(n) and len(d)>0 and np.isfinite(d).all() and np.isfinite(n).all() and (n>0).all() and (d>=0).all() and (d<=n).all(),"defectives and sample_sizes must be finite, have equal lengths, and satisfy 0 <= defectives <= sample_sizes")
    require(np.isfinite(sigma) and sigma>0, "sigma must be finite and > 0")
    pbar=d.sum()/n.sum(); points=d/n; limits=[]
    for ni in n:
        sd=(pbar*(1-pbar)/ni)**.5;limits.append([max(0,pbar-sigma*sd),min(1,pbar+sigma*sd)])
    return {"p_bar":pbar,"points":points.tolist(),"limits":[{"LCL":a,"UCL":b} for a,b in limits],"out_of_control_indices":[i for i,p in enumerate(points) if p<limits[i][0] or p>limits[i][1]],"assumptions":["Binomial model; sample size may vary; limits are calculated separately for each sample size."]}
