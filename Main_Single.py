
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
from scipy.stats import norm
import datetime


# In[2]:

xl = pd.ExcelFile('/Users/sergey/Documents/TUM/IDP/prepared_instruments.xlsx')


# In[3]:

x2 = pd.ExcelFile('/Users/sergey/Documents/TUM/IDP/indices_MODIF.xlsx')


# In[4]:

dfTMP = xl.parse("TS", skiprows = 0, skip_footer =False)
#print(dfTMP.ix[1:,0:5].head(4))


# In[6]:

dfBCM = x2.parse("TS_MODIF", skiprows = 0, skip_footer =False)
#print(dfBCM.ix[1:,0:5].head(4))


# In[226]:

#print(dfTMP)
#[2779 rows x 853 columns]
#246 Inv
#print(dfBCM)
#[2859 rows x 47 columns]


# In[261]:

def InitTargetMatrix(param = None):
    colListInvestm = list(dfTMP.columns.values)
    del colListInvestm[0]
    colListPrime = colListInvestm[::2]
    #print(colListPrime)
    TargetMatrix = pd.DataFrame(index=colListPrime)
    TargetMatrix.index.name = 'InvestmentName'
    #print(TargetMatrix)
    
    VaRInvestm = pd.DataFrame(Single_VaR(dfTMP.ix[1:,0:403] , 21, '2015-11-20','2016-12-01' ))
    Single_stddev = absSingle_stddev(dfTMP.ix[1:,0:403], startDt = '2015-11-20', endDt ='2016-12-01' )
    Single_RiskofLoss = absSingle_Risk_of_Loss(pd.DataFrame(dfTMP.ix[1:,0:403]), 21, 1000, '2015-11-20','2016-12-01' )
    Beta = relSingle_Beta(pd.DataFrame(dfTMP.ix[1:,0:403]), 21, 1000, '2015-11-20','2016-12-01' )
    Sharpe = relSingle_Sharpe(pd.DataFrame(dfTMP.ix[1:,0:403]), 21, 1000, '2015-11-20','2016-12-01' )
    
    
    TargetMatrix = pd.concat([TargetMatrix, VaRInvestm], axis=1, join_axes=[VaRInvestm.index])
    TargetMatrix = pd.concat([TargetMatrix, Single_stddev], axis=1, join_axes=[Single_stddev.index])
    TargetMatrix = pd.concat([TargetMatrix, Single_RiskofLoss], axis=1, join_axes=[Single_RiskofLoss.index])
    TargetMatrix = pd.concat([TargetMatrix, Beta], axis=1, join_axes=[Beta.index])
    TargetMatrix = pd.concat([TargetMatrix, Sharpe], axis=1, join_axes=[Sharpe.index])
    
    TargetMatrix.to_csv('/Users/sergey/Documents/TUM/IDP/Clustering/K-Means/TargetMatrix.csv', sep='\t', float_format='%.7f', encoding='utf-8', decimal = ',')

    return TargetMatrix
print(InitTargetMatrix().head(3))


# In[246]:

def PrepareCDAX(CDAX, startDt, endDt):
    
    tmp = pd.DataFrame(FormDataforGivenDates(CDAX,startDt,endDt))
    #print(tmp.head(3))
    tmp[tmp.columns[1]] = (tmp[tmp.columns[2]].astype(float)) - (tmp[tmp.columns[1]].astype(float))
    tmp = tmp.drop('.CDAX.1', 1)
    #print(tmp.head(10))
    #CDAX = (tmp[tmp.columns[2]].astype(float)) - (tmp[tmp.columns[1]].astype(float))
    CDAX = pd.DataFrame(tmp)

    CDAX.set_index('Date', inplace=True)

    #print(CDAX.index.name)
    '''
    1. filter by dates
    2. find rets
    3. cmp final DS with each stock(discard NaN when at least in one row ).
    '''
    return CDAX
PrepareCDAX(dfBCM.ix[1:,0:3], '2016-09-28','2016-10-10')


# In[220]:

def relSingle_Sharpe(Inv, numDays= 2, MoneyVol = 1000, startDt = '2016-11-25', endDt ='2016-11-30' ):
    """
        Measures how much return is being
        obtained for each theoretical unit of risk. 
        Indicates the historic average differential return per unit of 
        historic variability of the differential return.
    """
        
    '''
        0. bc it might be the case that 
            (a) stocks and BM have NaNs in different days, as well as 
            (b) stocks have more dates in data subset
        1. calc rets of BM
        2. calc rets of Inv
        3. join by date to one DS        
        4. get rid of rows where at least one has NaN
        5. calc cov
    '''
    ## columns from 0 to 2 correspond to the DAX BM
    CDAX = PrepareCDAX(dfBCM.ix[1:,0:3], startDt,endDt)
    colListPrime = FormColumns(Inv)
    
    setInvBM=pd.DataFrame()
    #print(colListPrime)
    listSharpe = []

    listofInv = FormDataforGivenDates(Inv,startDt,endDt)
    #print(listofInv)
    
    ##drop column from the Data frame
    #listofInv = listofInv.drop('Date', 1)  
    colListFull  = list(listofInv.columns.values)    
    #print(listofInv.head(4))
    
    listofInv = pd.DataFrame(listofInv)
    listofInv.set_index('Date', inplace=True)
    
    listofInv = listofInv.dropna(how='all')
    #print(listofInv)

    
    #print(listofInv.tail(5))
    
    ## len()-1 bc index is counted in names, but, not in the # of columns
    for i in range(0, len(colListFull) - 1, 2):

        #print(listofInv[listofInv.columns[i+1]].astype(float))
        
        tmp =  (listofInv[listofInv.columns[i+1]].astype(float)) - (listofInv[listofInv.columns[i]].astype(float))
        tmp = pd.DataFrame(tmp, columns=[listofInv.columns[i]])
        
        setInvBM = pd.concat([tmp, CDAX], axis=1, join_axes=[CDAX.index])
        
        # drop a row if there is any NaN value in the row.
        setInvBM = setInvBM.dropna(how='any')
        #print(setInvBM)
        
        '''1. Step: Calculate the diff bw returns of Inv and BM'''
        setSharpe = (setInvBM[setInvBM.columns[0]].astype(float)) - (setInvBM[setInvBM.columns[1]].astype(float))
        #print(setSharpe)
        '''2. Step: Calculate mean of the diffs'''
        mu = setSharpe.mean(axis=0)
        #print(mu)
        '''3. Step: Calculate STDDEV of the diffs (div by (N-1))'''
        StdDevInv = setSharpe.std(axis=0)
        #print(StdDevInv)
        '''4. Step: Calculate Sharpe Ratio'''
        Sharpe = mu / StdDevInv
        #print(StdDevInv)
        
        
        listSharpe.append(Sharpe)
        del setInvBM
        del tmp
        del StdDevInv
        del Sharpe

    
    listSharpe = pd.DataFrame(listSharpe).T
    listSharpe.columns = [colListPrime]
    listSharpe = listSharpe.T   
    
    listSharpe.columns = ['Sharpe'] 
    listSharpe.index.name = 'InvetmentName'
    
    return listSharpe

relSingle_Sharpe(pd.DataFrame(dfTMP.ix[1:,0:5]), 21, 1000, '2016-09-28','2016-10-10' )
#.sort(['Sharpe'], ascending=False)


# In[197]:

def relSingle_Beta(Inv, numDays= 2, MoneyVol = 1000, startDt = '2016-11-25', endDt ='2016-11-30' ):
    """
    Beta measures the volatility, or systematic risk, of a stock or portfolio 
    relative to a market benchmark, which has a beta of one. 
    """
        
    '''
        0. bc it might be the case that 
            (a) stocks and BM have NaNs in different days, as well as 
            (b) stocks have more dates in data subset
        1. calc rets of BM
        2. calc rets of Inv
        3. join by date to one DS        
        4. get rid of rows where at least one has NaN
        5. calc cov
    '''
    
    ## columns from 0 to 2 correspond to the DAX BM
    CDAX = PrepareCDAX(dfBCM.ix[1:,0:3], startDt,endDt)
    colListPrime = FormColumns(Inv)
    
    setInvBM=pd.DataFrame()
    #print(colListPrime)
    listBeta = []

    listofInv = FormDataforGivenDates(Inv,startDt,endDt)
    #print(listofInv)
    
    ##drop column from the Data frame
    #listofInv = listofInv.drop('Date', 1)  
    colListFull  = list(listofInv.columns.values)    
    #print(listofInv.head(4))
    
    listofInv = pd.DataFrame(listofInv)
    listofInv.set_index('Date', inplace=True)
    
    listofInv = listofInv.dropna(how='all')
    #print(listofInv)
    
    #print(listofInv.tail(5))
    
    ## len()-1 bc index is counted in names, but, not in the # of columns
    for i in range(0, len(colListFull) - 1, 2):

        #print(listofInv[listofInv.columns[i+1]].astype(float))
        
        tmp =  (listofInv[listofInv.columns[i+1]].astype(float)) - (listofInv[listofInv.columns[i]].astype(float))
        tmp = pd.DataFrame(tmp, columns=[listofInv.columns[i]])
        
        setInvBM = pd.concat([tmp, CDAX], axis=1, join_axes=[CDAX.index])
        
        # drop a row if there is any NaN value in the row.
        setInvBM = setInvBM.dropna(how='any')
        #print(setInvBM)
        #print(setInvBM[setInvBM.columns[1]].astype(float))
        CorInvBM = setInvBM.corr().ix[0,1]
        StdDevInv = (np.std(setInvBM[setInvBM.columns[0]], axis=0))
        StdDevBM = (np.std(setInvBM[setInvBM.columns[1]], axis=0))
        Beta = CorInvBM * StdDevInv / StdDevBM
        #print(StdDevInv)
        
        
        listBeta.append(Beta)
        del setInvBM
        del tmp
        del StdDevInv
        del StdDevBM

    
    listBeta = pd.DataFrame(listBeta).T
    listBeta.columns = [colListPrime]
    listBeta = listBeta.T   
    
    listBeta.columns = ['Beta'] 
    listBeta.index.name = 'InvetmentName'
    
    return listBeta

relSingle_Beta(pd.DataFrame(dfTMP.ix[1:,0:5]), 21, 1000, '2016-09-28','2016-10-10' )
#.sort(['Beta'], ascending=False)


# In[ ]:




# In[16]:

def absSingle_Risk_of_Loss(Inv, numDays= 2, MoneyVol = 1000, startDt = '2016-11-25', endDt ='2016-11-30' ):
    """
    Measures the percentage of outcomes below a certain totalreturn level, usually 0%. 
    """
    
    #print(listofInv.head(9))
    
    colListPrime = FormColumns(Inv)
    
    set1=pd.DataFrame()
    #print(colListPrime)
    listRiskofLoss = []

    listofInv = FormDataforGivenDates(Inv,startDt,endDt)

    
    ##drop column from the Data frame
    listofInv = listofInv.drop('Date', 1)  
    colListFull  = list(listofInv.columns.values)
    
    #print(colListFull)
    #print(listofInv)
    
    
    for i in range(0, len(colListFull), 2):
        #listofInv = listofInv[pd.notnull(listofInv[listofInv.columns[(i)]])]
        #listofInv = listofInv[pd.notnull(listofInv[listofInv.columns[(i+1)]])]
        
        #print(listofInv)
        set2=pd.DataFrame()
        set2 = pd.concat([set2, (listofInv[listofInv.columns[i+1]].astype(float)) - (listofInv[listofInv.columns[i]].astype(float))] , axis=1)
        #set2 =(listofInv[listofInv.columns[i+1]].astype(float)) - (listofInv[listofInv.columns[i]].astype(float))
        set1 = pd.concat([set1, set2] , axis=1)
        
        
        numRows = set2.dropna().shape[0]
        #print(set2.head(19))
        Risk_of_loss = round( 100*((set2 < 0).sum(1)).sum()/numRows , 2)
        listRiskofLoss.append(Risk_of_loss)
        del set2
        del Risk_of_loss

    set1.columns = [colListPrime]
    #print(set1.head(19))
    #print(listRiskofLoss)
    #print(set1[set1.columns[1]].shape[0])
    
    setRisk_of_loss = pd.DataFrame(listRiskofLoss)
    setRisk_of_loss = setRisk_of_loss.T
    setRisk_of_loss.columns = [colListPrime]
    setRisk_of_loss = setRisk_of_loss.T
    
    
    setRisk_of_loss.columns = ['Risk_of_Loss (%)'] 
    setRisk_of_loss.index.name = 'InvetmentName'
    #print(setRisk_of_loss.index.name)
    '''
    calculate # of times Value in SumSet was below 0, nad divide it by total number of rows in the set.
    '''
    #Risk_of_loss = round( ((SumSet < 0).sum(1)).sum()/SumSet.shape[0]*100 , 2)
    #print("Risk of Loss is: " + str(Risk_of_loss) + "%")
    
    return setRisk_of_loss
##call for 4 Stocks:
absSingle_Risk_of_Loss(pd.DataFrame(dfTMP.ix[1:,0:5]), 21, 1000, '2015-11-20','2016-11-30' )


# In[ ]:




# In[ ]:




# In[15]:

def absSingle_stddev(Inv, numDays= 2, startDt = '2016-11-25', endDt ='2016-11-30' ):  
    '''
    Calculating VaR of a single stock/bond one by one for a given Time Period.
    '''

    colListPrime = FormColumns(Inv)
    #print(colListPrime)
    listStdDev = []

    listofInv = FormDataforGivenDates(Inv,startDt,endDt)
    
    #print(listofInv.head(10))
    
    listofInv = listofInv.set_index('Date',drop = True).diff()
    '''
    diff() shifts 1st row to the position of the 2nd, now we have to reset the index to turn it back.
    '''
    listofInv = listofInv.reset_index()
    
    #remove 1st row containing NaNs (there is no diff)
    listofInv.drop(listofInv.index[[0]], inplace = True)

    
    listofInv = listofInv[listofInv.columns[::2]]
    
    ##drop column from the Data frame
    listofInv = listofInv.drop('Date', 1)  
    #listofInv = ColumnNicer(listofInv)
    listofInv.columns = colListPrime
    #print(listofInv)
    
    
    for i in range(0, len(colListPrime), 1):

        # drop a row if all values in the row are nan
        listofInv = listofInv.dropna(how='all')

        Inv_stddev = np.std(listofInv[str(listofInv.columns[i])])

        listStdDev.append(Inv_stddev) 
    
    listStdDev=pd.DataFrame(listStdDev).T
    listStdDev.columns= colListPrime
    listStdDev = listStdDev.T
    

    listStdDev.columns = ['StdDev'] 
    listStdDev.index.name = 'InvetmentName'
    
    #listofInv.columns = colListPrime
    #print(setVaR)
   

    return listStdDev

    '''
    Passing dataframe that contains columns: Date, 
    names of stocks(2nd column of same stock contains the closing price).
    '''
    #print("Stocks Standart Deviations are: " + str(Inv_stddev))
   
absSingle_stddev(dfTMP.ix[1:,0:5] , 21, '2016-11-20','2016-11-30' )


# In[ ]:




# In[14]:

def Single_VaR(Inv, numDays= 2, startDt = '2016-11-25', endDt ='2016-11-30' ):
    '''
    Calculating VaR of a single stock/bond one by one for a given Time Period.
    '''

    colListPrime = FormColumns(Inv)
    #print(colListPrime)
    listRisk_95 = []

    listofInv = FormDataforGivenDates(Inv,startDt,endDt)
  
    
    #print(listofInv.head(21))
    
    listofInv = listofInv.set_index('Date',drop = True).diff()
    '''
    diff() shifts 1st row to the position of the 2nd, now we have to reset the index to turn it back.
    '''
    listofInv = listofInv.reset_index()
    #print(listofInv.describe())
    #remove 1st row containing NaNs (there is no diff)
    listofInv.drop(listofInv.index[[0]], inplace = True)

    
    listofInv = listofInv[listofInv.columns[::2]]
    
    ##drop column from the Data frame
    listofInv = listofInv.drop('Date', 1)  
    #listofInv = ColumnNicer(listofInv)
    listofInv.columns = colListPrime
    #print(listofInv)
    
    
    for i in range(0, len(colListPrime), 1):

        # drop a row if all values in the row are nan
        listofInv = listofInv.dropna(how='all')

        mu = np.mean(listofInv[str(listofInv.columns[i])])
        sigma = np.std(listofInv[str(listofInv.columns[i])])

        valueAtRisk_95 = round(norm.ppf(0.05, mu, sigma)*100,2)

        listRisk_95.append(valueAtRisk_95) 
    
    setVaR=pd.DataFrame(listRisk_95).T
    setVaR.columns= colListPrime
    setVaR = setVaR.T
    

    setVaR.columns = ['VaR_95(%)'] 
    setVaR.index.name = 'InvetmentName'
    
    #listofInv.columns = colListPrime
    #print(setVaR)
   

    return setVaR
'''
Passing dataframe that contains columns: Date, 
names of stocks(2nd column of same stock contains the closing price).
'''
Single_VaR(dfTMP.ix[1:,0:5] , 21, '2015-11-20','2016-11-30' )


## one-way 5% quantile, critical value is 1.64
#VaR_21 = returns.std() * np.sqrt(21) * 1.645


# In[ ]:




# In[11]:

def FormDataforGivenDates(listofInv, startDt, endDt):
    
    #print(listofInv.head(21))
    startDate = np.datetime64( startDt)
    endDate= np.datetime64( endDt)
    
    ##remove Timestamp, Trade Open, Trade Close
    listofInv=pd.DataFrame(listofInv.ix[1:,0:])


    listofInv['Date'] =  pd.to_datetime(listofInv['Date'], format='%Y-%m-%d')
    listofInv['Date'] = pd.to_datetime(listofInv['Date'])  

    mask = (listofInv['Date'] >= startDate) & (listofInv['Date'] <= endDate)
    #print (mask)
    listofInv = listofInv.loc[mask]
    #print(listofInv.head(12))
 

    return listofInv
FormDataforGivenDates(dfBCM.ix[1:,0:5],'2016-09-28','2016-10-10')


# In[13]:

def FormColumns(listofInv):
    
    colListFull  = list(listofInv.columns.values)    
    colListInvestm  = list(listofInv.columns.values)
    if 'Date' in colListInvestm:
        del colListInvestm[0]
    #print(colListFull)
    colListPrime = colListInvestm[::2] 
    #print(colListPrime)
    
    return colListPrime
#FormColumns(dfTMP.ix[1:,1:5])


# In[ ]:



