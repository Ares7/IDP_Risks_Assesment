# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re as re
import risk_metrics_single as sr
import fy_constants as FY
import fy_ratios as fyr
#from datetime import datetime
#from scipy.stats import norm



   

def getTS(xl, startDt = '1900-01-01', endDt = '2200-01-01'):
    rawData = xl.parse('TS', header = None)
    startDt = np.datetime64(startDt)
    endDt   = np.datetime64(endDt)
    
    #only close prices
    columnMask = (rawData.iloc[1] == 'Trade Close') 
    invNames = rawData.ix[0,columnMask]
    columnMask.iat[0] = True #also dates
    #filter dates
    dates = pd.to_datetime(rawData.iloc[2:,0], format='%Y-%m-%d')
    datesMask = (dates >= startDt) & (dates <= endDt) 
    
    rowMask = pd.Series([False,False],index=[0,1]).append(datesMask)
    
    newData = rawData.ix[rowMask,columnMask]
    newData.iloc[:,0] = dates
    newData.set_index([0],inplace=True)
    #dates from Thompson are only business days,
    #but keep in mind
    #newData = newData[newData.index.dayofweek < 5]
    newData.columns = invNames
    newData.index.name = 'Date'
    newData.sort_index(ascending=True,inplace=True)
    return newData

def getReturns_SingleInv(dfPricesSingle):
    #dfPricesSingle should contain only one column
    return dfPricesSingle.fillna(method='ffill').pct_change().iloc[1:]

def getDictOfReturns(dfPrices):
    myDict = dict()
    for column in dfPrices:
        myDict[column] = getReturns_SingleInv(dfPrices[column])
    return myDict

def getFYData_SingleYear(xl, wsName = 'FY0'):
    rawData = xl.parse(wsName, header = 0, na_values = ['NULL'])
    
    remapCols = dict()
    remapCols['ID'] = FY.ID
    remapCols['Year'] = FY.YEAR
    remapCols['ISIN'] = FY.ISIN
    remapCols['Normalized EBITDA'] = FY.EBITDA
    remapCols['Normalized EBIT'] = FY.EBIT
    remapCols['Normalized Income Before Taxes'] = FY.EBT
    remapCols['Normalized Income After Taxes'] = FY.NET_INCOME
    remapCols['Total Revenue'] = FY.TOT_REVENUE
    remapCols['Total Debt'] = FY.TOT_DEBT
    remapCols['Accounts Receivable - Trade, Net'] = FY.ACC_RECEIVABLE
    remapCols['Accounts Payable'] = FY.ACC_PAYABLE
    remapCols['Total Inventory'] = FY.TOT_INVENTORY
    remapCols['Cost Of Goods Sold - Actual'] = FY.COGS
    remapCols['Enterprise Value (Daily Time Series)'] = FY.ENTERPR_VALUE
    remapCols['Net Debt - Mean'] = FY.NET_DEBT
    remapCols['Total Current Assets'] = FY.TOT_CURR_ASSETS
    remapCols['Total Current Liabilities'] = FY.TOT_CURR_LIABILITIES
    remapCols['Total Liabilities'] = FY.TOT_LIABILITIES
    remapCols['Total Equity'] = FY.TOT_EQUITY
    remapCols['Common Stock, Total'] = FY.TOT_COMMON_STOCK
    remapCols['Shares Out - Common Stock Primary Issue'] = FY.SHARES_OUT
    remapCols['Cash and Equivalents'] = FY.CASH_N_EQUIVALENTS
    remapCols['Number of Employees'] = FY.NUM_EMPLOYEES

    rawData.rename(columns=remapCols, inplace=True)
 
    rawData.set_index([FY.ID],inplace=True)
    return rawData      
        
def getFYData_Multiple(xl, endYear):
    #get FY-data for all available years
    dfRes = pd.DataFrame()
    for sheet in xl.sheet_names:
        m = re.match(r"FY(-?\d+)",sheet)
        if m != None and m.group(1) != None:
            offset = int(m.group(1))
            currentYear = endYear + offset
            dfTmp = getFYData_SingleYear(xl, sheet)
            dfTmp[FY.YEAR] = currentYear
            dfTmp.set_index([FY.YEAR], append=True,inplace=True)
            dfRes = dfRes.append(dfTmp)
    return dfRes  

def getRiskMatrix(dictTS, dfFY, begDate, endDate):
    date_beg = pd.to_datetime(begDate)
    date_end = pd.to_datetime(endDate)
    date_1M = date_end - np.timedelta64(30,'D')    

    dfRes = pd.DataFrame()
    #calculate items from TS
    for currentID, dfRet in dictTS.items():
        dates = dfRet.index
        mask_period = (dates >= date_beg) & (dates <= date_end)
        mask_1M = (dates >= date_1M) & (dates <= date_end)
        mask_beforeEnd = (dates <= date_end)
        
        dfRes.loc[currentID,'stddev'] = sr.stddev(dfRet[mask_period])
        dfRes.loc[currentID,'stddev_1M'] = sr.stddev(dfRet[mask_1M])        
        dfRes.loc[currentID,'VaR95_daily'] = sr.val_at_risk(dfRet[mask_beforeEnd],0.05)
    #calculate items from FY
    for currentID in dfFY.index.get_level_values(FY.ID):
        dfTmp = dfFY.ix[currentID]
        dfRes.loc[currentID,'current_ratio'] = fyr.current_ratio(dfTmp, date_end.year)
        dfRes.loc[currentID,'quick_ratio'] = fyr.quick_ratio(dfTmp, date_end.year)
        dfRes.loc[currentID,'debt_ratio'] = fyr.debt_ratio(dfTmp, date_end.year)
        dfRes.loc[currentID,'gearing'] = fyr.gearing(dfTmp, date_end.year)
        dfRes.loc[currentID,'leverage'] = fyr.leverage(dfTmp, date_end.year)
        dfRes.loc[currentID,'net_leverage'] = fyr.net_leverage(dfTmp, date_end.year)    
        
    return dfRes
inputDir = '/Users/sergey/Documents/TUM/IDP'
#inputDir = 'C:\\Users\\ankifor\\Desktop\\IDP\\IDP_Risks_Assesment'
rawDataPath = inputDir + '\\' + 'prepared_instruments1.xlsx'
rawDataPath = inputDir + '/' + 'prepared_instruments.xlsx'

xl = pd.ExcelFile(rawDataPath)
dfFY = getFYData_Multiple(xl, 2016)
dfTS = getTS(xl)
dictTS = getDictOfReturns(dfTS)
xl.close()

dfRiskM = getRiskMatrix(dictTS,dfFY,'2015-12-31','2016-09-30')

#dfRiskM.to_csv('/Users/sergey/Documents/TUM/IDP/Clustering/TargetMatrixFY.csv', sep='\t', float_format='%.7f', encoding='utf-8', decimal = ',')
print(dfRiskM.head())

#begDate = np.datetime64('2015-12-31')
#endDate = np.datetime64('2016-09-30')

#for currentID, df in dictRet.items():
#    vals = [sr.stddev(df), 
#            sr.val_at_risk(df,0.05),
#            sr.val_at_risk(df,0.05,True)]
#    print(vals)



#x = pd.DataFrame(np.random.rand(10))*0.1

