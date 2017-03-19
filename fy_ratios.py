# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from scipy.stats import norm
import fy_constants as FY


def current_ratio(dfFY_SingleID, year):
    curr_assets = dfFY_SingleID.at[year, FY.TOT_CURR_ASSETS]
    curr_liab = dfFY_SingleID.at[year, FY.TOT_CURR_LIABILITIES]
    if curr_liab == 0:
        return None
    else:
        return curr_assets/curr_liab

def quick_ratio(dfFY_SingleID, year):
    curr_assets = dfFY_SingleID.at[year, FY.TOT_CURR_ASSETS]
    curr_inventory = dfFY_SingleID.at[year, FY.TOT_INVENTORY]
    curr_liab = dfFY_SingleID.at[year, FY.TOT_CURR_LIABILITIES]
    if curr_liab == 0:
        return None
    else:
        return (curr_assets+curr_inventory)/curr_liab

def debt_ratio(dfFY_SingleID, year):
    tot_debt = dfFY_SingleID.at[year, FY.TOT_DEBT]
    tot_liab = dfFY_SingleID.at[year, FY.TOT_LIABILITIES]
    tot_equity = dfFY_SingleID.at[year, FY.TOT_EQUITY]
    tot_assets = tot_liab  + tot_equity
    if tot_assets == 0:
        return None
    else:
        return tot_debt/tot_assets

def gearing(dfFY_SingleID, year):
    tot_debt = dfFY_SingleID.at[year, FY.TOT_DEBT]
    tot_equity = dfFY_SingleID.at[year, FY.TOT_EQUITY]
    if tot_equity == 0:
        return None
    else:
        return tot_debt/tot_equity

def leverage(dfFY_SingleID, year):
    tot_debt = dfFY_SingleID.at[year, FY.TOT_DEBT]
    ebitda = dfFY_SingleID.at[year, FY.EBITDA]
    if ebitda == 0:
        return None
    else:
        return tot_debt/ebitda

def net_leverage(dfFY_SingleID, year):
    net_debt = dfFY_SingleID.at[year, FY.NET_DEBT]
    ebitda = dfFY_SingleID.at[year, FY.EBITDA]
    if ebitda == 0:
        return None
    else:
        return net_debt/ebitda