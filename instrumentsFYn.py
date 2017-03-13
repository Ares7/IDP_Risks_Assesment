
# coding: utf-8

# In[235]:

import pandas as pd
import numpy as np
from scipy.stats import norm
import datetime

get_ipython().magic('config IPCompleter.greedy=True')


# In[2]:

xl = pd.ExcelFile('/Users/sergey/Documents/TUM/IDP/prepared_instruments.xlsx')



# In[33]:

##df = xl.parse("FY0")
#dfTime = xl.parse("TS")
dfTime = xl.parse("TS", skiprows = 0, skip_footer =False)
dfTime.replace(np.NaN,0 , inplace =True)
df = dfTime

print(dfTime.head())


# In[4]:

df = df.drop(df.index[[0]])#dropping 2nd row that contains "open", "close"
df.drop('Date', axis=1, inplace=True)


# In[5]:

df_mean = df
df_mean= df_mean.astype(float)


# In[6]:


df_mean = df_mean.groupby((np.arange(len(df_mean.columns)) // 2) + 1, axis=1).mean().add_prefix('s')



# In[7]:

#print(df.columns[2])
collist = list(df.columns.values)
collist = collist[::2]
df_mean.columns = [collist]


# In[269]:

#print(xl.sheet_names)
#print(dfTime.head())


# In[270]:

'''for i in range(0,5,2):

        dfAvg =df.ix[1:2,i:(i+2)].T.sum()
        df_sum=pd.DataFrame(dfAvg)

        df_sum.columns = [df.columns[i]]
        print (df_sum)
        dat1 = dat1.join(df_sum )

        del dfAvg
'''


# In[271]:

#df_mean.ix[0:,:].std()
#k =df_mean.ix[0:,:].std()
#print( k[66] )


# In[8]:

print(len(df_mean.corr()))
print(len(df_mean.corr().columns))


# In[9]:

lCorr = df_mean.corr().ix[0:,:1]
#print(lCorr)


# In[76]:

def absPortf_stddev(listofInv):
 
    #A_rank=[2,4,4,4,5,5,7,9]
    #arr = np.array([A_rank])
    #print(np.mean(arr))
    #print(np.std(arr))
    ##print(np.std(arr, axis=0))
    #print(np.correlate([0.686,0.702], [0.646,0.68]))
    #print(len(collist))
    weight = 1/len(collist)
    lStdDev = df_mean.ix[0:,:].std()
    lCorr = df_mean.corr().ix[0:,:1]
    ## can now access: lStdDev[66]
    
    #PART 1:
    sum1 = 0
    for i in range(1, len(collist), 1):
        sum1 = sum1 + weight * lStdDev[i]
    #print(sum1)
    
    #PART 2:
    sum2 = 0
    for i in range(1, len(collist), 1):
        #print("Current i= " + str(i))
        for j in range(1, len(collist), 1):
            #print("Current j= " + str(j))
            sum2 = sum2 + weight * weight * lStdDev[i] * lStdDev[j]
    #print(sum2)
    
    Portf_stddev = (sum1+2*sum2) ** (0.5)
    print("Portfolio Standart Deviation is: " + str(Portf_stddev))
   
    
    ##print(dfTime.head())
    #avgVal = (dfTime.ix[1:3,1:2] + dfTime.ix[1:3,2:3])/2
    #print(lStdDev)
    
absPortf_stddev(None)


# In[77]:

#dfTime


# In[37]:

#print(dfTime.ix[1:,0:])


# In[163]:

print (dfTime.columns)

print (collistPrime[::2])
# In[309]:

tdf.columns[2]


# In[312]:

##print((tdf[tdf.columns[2]].astype(float)) - (tdf[tdf.columns[1]].astype(float)))


# In[229]:

#removing 1 row:
##print(dfTime.ix[1:,0:])


# In[62]:

##dfTMP = xl.parse("TS", skiprows = 0, skip_footer =False)


# In[73]:

colListPrime = list(dfTime.columns.values)

del colListPrime[0]
colListPrime = colListPrime[::2]
colListFull  = list(dfTime.columns.values)
del colListFull[0]
#print(colListFull)


# In[240]:

#pd.DataFrame(dfTMP.ix[1:,2:3])
print(np.random.choice(np.arange(100), size=21, replace=False))


# In[302]:

startDate = np.datetime64( '2016-11-25')
endDate= np.datetime64( '2016-11-30')

listofInv = dfTMP
listofInv=pd.DataFrame(listofInv.ix[1:,0:])

listofInv=pd.DataFrame(listofInv)
#listofInv['Date'] = [time.date() for time in listofInv['Date']]

listofInv['Date'] =  pd.to_datetime(listofInv['Date'], format='%Y-%m-%d')
listofInv['Date'] = pd.to_datetime(listofInv['Date'])  

mask = (listofInv['Date'] > startDate) & (listofInv['Date'] <= endDate)
#print (mask)
listofInv = listofInv.loc[mask]
#print(listofInv.loc[mask].head(8))

#listofInv[(listofInv['Date'] >= startDate) ]
print(listofInv.head(8))

#print(listofInv.head(9))
#df['time'] = [time.date() for time in df['time']]
#df['column'].dt.date
#raw_data['Mycol'] =  pd.to_datetime(raw_data['Mycol'], format='%d%b%Y:%H:%M:%S.%f')
#df['time'] = pd.to_datetime(df['time'])


# In[307]:

def absPortf_VC_spec_VaR(listofInv = dfTMP, numDays= 2, MoneyVol = 1000, startDt = '2016-11-25', endDt ='2016-11-30' ):
    """
    Variance-Covariance Method of computing VaR of specific 
    Stocks(separately, not as a Portfolio) over time frame.
    """
    #print(listofInv.head(9))
    colListFull  = list(listofInv.columns.values)
    colListPrime = list(listofInv.columns.values)    
    listRisk_95 = []
    listRisk_99 = []
    
    ##startDate = pd.to_datetime('22/11/2016' )
    startDate = np.datetime64( startDt)
    endDate= np.datetime64( endDt)
    
    ##remove Timestamp, Trade Open, Trade Close
    listofInv=pd.DataFrame(listofInv.ix[1:,0:])

    listofInv=pd.DataFrame(listofInv)
    #listofInv['Date'] = [time.date() for time in listofInv['Date']]

    listofInv['Date'] =  pd.to_datetime(listofInv['Date'], format='%Y-%m-%d')
    listofInv['Date'] = pd.to_datetime(listofInv['Date'])  

    mask = (listofInv['Date'] >= startDate) & (listofInv['Date'] <= endDate)
    #print (mask)
    listofInv = listofInv.loc[mask]   
    
    del colListFull[0]
    del colListPrime[0]
    #drop column from the Data frame
    listofInv = listofInv.drop('Date', 1)
    colListPrime = colListPrime[::2]
    
    #print(listofInv.head(10))
    #print(len(colListFull))
    
    for i in range(1, len(colListFull), 2):##changed to 1 from 2
        #print("i= " + str(i))
        #print("NOW col" + str(listofInv.ix[1:,(i):(i+1)].head(8)))
        
        tmp=pd.DataFrame(listofInv.ix[1:,(i):(i+1)])
        tmp = tmp[pd.notnull(tmp[tmp.columns[(0)]])]
        #print("curr col name is :" + tmp.columns[0])
        ##tmp.columns[0]
        #print(tmp.head(7))

        tmp["rets" + str(tmp.columns[0])] = tmp[tmp.columns[0]].pct_change()
        
        mu = np.mean(tmp["rets" + str(tmp.columns[0])])
        sigma = np.std(tmp["rets" + str(tmp.columns[0])])
        #print(tmp.head(7))
        #print(mu)
        #print(sigma)        
        valueAtRisk_95 = MoneyVol - MoneyVol*(norm.ppf(0.05, mu, sigma) + 1)     
        valueAtRisk_99 = MoneyVol - MoneyVol*(norm.ppf(0.01, mu, sigma) + 1) 
        
        listRisk_95.append(valueAtRisk_95)       
        listRisk_99.append(valueAtRisk_99)
        
        #valueAtRisk_95 = MoneyVol - MoneyVol*(norm.ppf(0.05, mu, sigma) + 1)
        #valueAtRisk_99 = MoneyVol - MoneyVol*(norm.ppf(0.01, mu, sigma) + 1)   
       
        #Portf_stddev = (sum1+2*sum2) ** (0.5)
        #print("Portfolio Historical Value at Risk with 95% confidence is: " + str(valueAtRisk_95))
        #print("Portfolio Historical Value at Risk with 99% confidence is: " + str(valueAtRisk_99))
        
        
        
        del tmp    
    ##set1.columns = [colListPrime]
    ##print(set1.head())
    #print("VaR for a particular Investments:" + str(listRisk_95))
    setRisk_95 = pd.DataFrame(listRisk_95).T
    setRisk_99 = pd.DataFrame(listRisk_99).T
    
    setRisk_95.columns = [colListPrime]
    setRisk_99.columns = [colListPrime]
    
    setRisk_95 = setRisk_95 **2
    setRisk_99 = setRisk_99 **2
    #print(setRisk_95)
    
    setRisk_95['FINAL_95'] = setRisk_95.groupby((np.arange(len(setRisk_95.columns)) //len(setRisk_95.columns)*10 ) + 1, axis=1).sum().add_prefix('sum')
    setRisk_95['FINAL_95'] = setRisk_95['FINAL_95'] **0.5
    
    setRisk_99['FINAL_99'] = setRisk_99.groupby((np.arange(len(setRisk_99.columns)) //len(setRisk_99.columns)*10 ) + 1, axis=1).sum().add_prefix('sum')
    setRisk_99['FINAL_99'] = setRisk_99['FINAL_99'] **0.5
    
    setPortfVaR = pd.DataFrame()
    

    print(setRisk_95)
    print(setRisk_99)

dfTMP = xl.parse("TS", skiprows = 0, skip_footer =False)
##call for 4 Stocks:
absPortf_VC_spec_VaR(pd.DataFrame(dfTMP.ix[1:,0:9]), 21, 1000, '2015-11-20','2016-11-30' )


# In[308]:

def absPortf_HistVaR(listofInv =dfTime, numDays= 2, MoneyVol =1000, startDt = '22/11/2016', endDt ='01/12/2016' ):
 
    """
    Variance-Covariance calculation of daily Value-at-Risk
    using confidence level c, with mean of returns mu
    and standard deviation of returns sigma, on a portfolio
    of value P.
    """
    ##startDate = pd.to_datetime('22/11/2016' )
    startDate = np.datetime64( datetime.datetime.strptime(startDt, '%d/%m/%Y'))
    endDate= np.datetime64( datetime.datetime.strptime(endDt, '%d/%m/%Y'))
    
    ##remove Timestamp, Trade Open, Trade Close
    listofInv=pd.DataFrame(listofInv.ix[1:,0:])
    
    listofInv['Date'] =  pd.to_datetime(listofInv['Date'])
    listofInv=pd.DataFrame(listofInv)
    listofInv[(listofInv.Date >= startDate) & (listofInv.Date <= endDate )]
    
    
    set1=pd.DataFrame()

    colListPrime = list(dfTime.columns.values)
    del colListPrime[0]
    colListPrime = colListPrime[::2]

    for i in range(1, len(colListFull), 2):
        set2 =(listofInv[listofInv.columns[i+1]].astype(float)) - (listofInv[listofInv.columns[i]].astype(float))
        set1 = pd.concat([set1, set2] , axis=1)
        del set2

    set1.columns = [colListPrime]
    #print(set1.head())


    SumSet = set1.groupby((np.arange(len(set1.columns)) //len(set1.columns)*10 ) + 1, axis=1).sum().add_prefix('sum')
    SumSet["rets"] = SumSet["sum1"].pct_change()
    
    SumSet.replace(np.NaN,0 , inplace =True) 
    SumSet = SumSet.replace([np.inf, -np.inf], 0)
    SumSet = SumSet.astype(float)

    
    mu = np.mean(SumSet["rets"])
    sigma = np.std(SumSet["rets"])

    print(mu)
    print(sigma)
    #print "Value-at-Risk: $%0.2f" % var
    
    valueAtRisk_95 = MoneyVol - MoneyVol*(norm.ppf(0.05, mu, sigma) + 1)
    valueAtRisk_99 = MoneyVol - MoneyVol*(norm.ppf(0.01, mu, sigma) + 1)

    
       
    #Portf_stddev = (sum1+2*sum2) ** (0.5)
    print("Portfolio Historical Value at Risk with 95% confidence is: " + str(valueAtRisk_95))
    print("Portfolio Historical Value at Risk with 99% confidence is: " + str(valueAtRisk_99))
    
    #print(lStdDev)
    
absPortf_HistVaR(dfTime, 21, 1000, '22/11/2016','24/11/2016' )


# In[8]:

numcols = len(dfTime.ix[:, 2::2])
numcols


# In[47]:

#print(df.head())


# In[10]:

np.std([1,3,4,6], ddof=1)


# In[11]:

np.std(df['Normalized Income After Taxes'], ddof=1)


# In[22]:

lister = ['mmds', 'kmkd', 'algs', 'idp']


# In[27]:

print (lister)


# In[24]:

lister.insert(2, 'finm')


# In[26]:

lister.sort()


# In[28]:

fun = ['swm', 'film', 'music']


# In[29]:

act = fun + lister
print(act)


# In[32]:

act2 = [[fun], [lister]]
print(act2)


# In[ ]:



