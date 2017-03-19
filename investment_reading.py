# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re as re
#from datetime import datetime
#from scipy.stats import norm

FY_ID = 'ID'
FY_YEAR = 'Year'
FY_ISIN = 'ISIN'
FY_EBITDA = 'EBITDA'
FY_EBIT = 'EBIT'
FY_EBT = 'EBT'
FY_NET_INCOME = 'Net Income'
FY_TOT_REVENUE = 'Tot Revenue'
FY_TOT_DEBT = 'Tot Debt'
FY_ACC_RECEIVABLE = 'Acc Receivable'
FY_ACC_PAYABLE = 'Acc Payable'
FY_TOT_INVENTORY = 'Tot Inventory'
FY_COGS = 'COGS'
FY_ENTERPR_VALUE = 'Enterpr Value'
FY_NET_DEBT = 'Net Debt'
FY_TOT_CURR_ASSETS = 'Tot Curr Assets'
FY_TOT_CURR_LIABILITIES = 'Tot Curr Liabilities'
FY_TOT_LIABILITIES = 'Tot Liabilities'
FY_TOT_EQUITY = 'Tot Equity'
FY_TOT_COMMON_STOCK = 'Tot Common Stock'
FY_SHARES_OUT = 'Shares Out'
FY_CASH_N_EQUIVALENTS = 'Cash & Equivalents'
FY_NUM_EMPLOYEES = 'Number of Employees'

   

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
    remapCols['ID'] = FY_ID
    remapCols['Year'] = FY_YEAR
    remapCols['ISIN'] = FY_ISIN
    remapCols['Normalized EBITDA'] = FY_EBITDA
    remapCols['Normalized EBIT'] = FY_EBIT
    remapCols['Normalized Income Before Taxes'] = FY_EBT
    remapCols['Normalized Income After Taxes'] = FY_NET_INCOME
    remapCols['Total Revenue'] = FY_TOT_REVENUE
    remapCols['Total Debt'] = FY_TOT_DEBT
    remapCols['Accounts Receivable - Trade, Net'] = FY_ACC_RECEIVABLE
    remapCols['Accounts Payable'] = FY_ACC_PAYABLE
    remapCols['Total Inventory'] = FY_TOT_INVENTORY
    remapCols['Cost Of Goods Sold - Actual'] = FY_COGS
    remapCols['Enterprise Value (Daily Time Series)'] = FY_ENTERPR_VALUE
    remapCols['Net Debt - Mean'] = FY_NET_DEBT
    remapCols['Total Current Assets'] = FY_TOT_CURR_ASSETS
    remapCols['Total Current Liabilities'] = FY_TOT_CURR_LIABILITIES
    remapCols['Total Liabilities'] = FY_TOT_LIABILITIES
    remapCols['Total Equity'] = FY_TOT_EQUITY
    remapCols['Common Stock, Total'] = FY_TOT_COMMON_STOCK
    remapCols['Shares Out - Common Stock Primary Issue'] = FY_SHARES_OUT
    remapCols['Cash and Equivalents'] = FY_CASH_N_EQUIVALENTS
    remapCols['Number of Employees'] = FY_NUM_EMPLOYEES

    rawData.rename(columns=remapCols, inplace=True)
 
    rawData.set_index([FY_ID],inplace=True)
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
            dfTmp[FY_YEAR] = currentYear
            dfTmp.set_index([FY_YEAR], append=True,inplace=True)
            dfRes = dfRes.append(dfTmp)
    return dfRes  

inputDir = 'C:\\Users\\ankifor\\Desktop\\IDP\\IDP_Risks_Assesment'
rawDataPath = inputDir + '\\' + 'prepared_instruments1.xlsx'


#print(dictRet)
xl = pd.ExcelFile(rawDataPath)
dfFY = getFYData_Multiple(xl, 2016)
dfTS = getTS(xl,'2015-12-31','2016-09-30')
dictRet = getDictOfReturns(dfTS)
xl.close()
#x = pd.DataFrame(np.random.rand(10))
#x.iloc[np.random.randint(0,9,3),0] = None
#print(x.fillna(method='ffill'))
