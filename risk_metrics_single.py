# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 18:37:26 2017

@author: ankifor
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

def stddev(rets):
    return np.std(rets)

def val_at_risk(rets, conf, bootstrap=False,n_days=1):
    #conf is normally 0.05
    assert conf > 0 and conf < 1
    assert len(rets) > n_days
    assert n_days > 0
    res = 0
    if not bootstrap:
        s = np.std(rets)
        q = norm.ppf(conf)
        res = q * s * np.sqrt(n_days)
    else:
        n_bootstrap = 10**4
        if n_days == 1:
            simulated = np.random.choice(rets,n_bootstrap,replace=True)
        else:
            simulated = []
            for _ in range(n_bootstrap):
                sample = np.random.choice(rets,n_days,replace=False)
                simulated.append((1+sample).prod()-1)
        res = np.percentile(simulated, q=conf*100)
    return abs(res)

