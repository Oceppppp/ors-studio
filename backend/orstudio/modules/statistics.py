from __future__ import annotations
import numpy as np
from scipy import stats
from .common import number_list


def describe(values):
    x=np.asarray(number_list(values,"values",1),dtype=float); n=len(x)
    return {"count":n,"sum":float(x.sum()),"mean":float(x.mean()),"median":float(np.median(x)),"mode":float(stats.mode(x,keepdims=False).mode),"minimum":float(x.min()),"maximum":float(x.max()),"range":float(np.ptp(x)),"variance_population":float(x.var(ddof=0)),"variance_sample":float(x.var(ddof=1)) if n>1 else None,"std_population":float(x.std(ddof=0)),"std_sample":float(x.std(ddof=1)) if n>1 else None,"q1":float(np.quantile(x,.25)),"q3":float(np.quantile(x,.75)),"skewness":float(stats.skew(x,bias=False)) if n>2 else None,"kurtosis_excess":float(stats.kurtosis(x,bias=False)) if n>3 else None,"assumptions":["Missing/non-numeric observations must be cleaned or excluded before submission; sample variance uses n-1."]}
