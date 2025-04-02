

# Calculates granger causality matrix for a time series of e.g. dataframes of metrics extracted from a set of MD simulations, and then groups the matrices using K-means clustering

# Usage 

# python grangerkmeansgpcrcsv.py folder


import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
import sys
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import ccf

from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import *

import sys, os, time


starttime = time.time()

def get_accepted_idx(correlation_matrix, thresh, N_vars):
    rejected_idx = set()
    accepted_idx = set()
    for r in range(0, N_vars):
        if r not in rejected_idx:
            accepted_idx.add(r)

        for c in range(r + 1, N_vars):
            if np.abs(correlation_matrix[r, c]) > thresh or np.isnan(correlation_matrix[r, c]):
                rejected_idx.add(c)
    return accepted_idx


def get_columns(data):

    N_vars = data.shape[1]
    nlags = [1]#,2,3, 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

    results = []
    for i in range(0, len(nlags)):
        results.append(np.zeros((N_vars, N_vars)))

    for r in range(0, N_vars):
        for c in range(r, N_vars):
            cross_corr = ccf(data[:,r], data[:,c], adjusted=True, nlags=max(nlags))
            
            for i in range(0, len(nlags)):
                results[i][r,c] = cross_corr[nlags[i] - 1]


    low_thresh = 1e-3
    high_thresh = 1.0

    lag = 1

    while low_thresh < high_thresh and np.abs(low_thresh - high_thresh) > 1e-3:
        
        mid_thresh = (low_thresh + high_thresh) / 2
        print(lag, mid_thresh)
        
        accepted_idx = get_accepted_idx(results[lag -1], mid_thresh, N_vars)
        accepted_column_names = [column_names[i] for i in accepted_idx]
        try:
            model = VAR(stationary_df[accepted_column_names])
            var_results = model.fit(maxlags=lag)
            var_results.summary()
            low_thresh = mid_thresh
        except:
            high_thresh = mid_thresh
            continue
    
    print(mid_thresh)
    
    accepted_idx = get_accepted_idx(results[lag-1], mid_thresh - 1e-3, N_vars)
    accepted_column_names = [column_names[i] for i in accepted_idx]

    return accepted_column_names


def grangers_causation_matrix(data, variables, test='ssr_chi2test', maxlag=12):    
    """Check Granger Causality of all possible combinations of the Time series.
    The rows are the response variable, columns are predictors. The values in the table are the P-Values. P-Values lesser than the significance level (0.05), implies  the Null Hypothesis that the coefficients of the corresponding past values is zero, that is, the X does not cause Y can be rejected.

    data      : pandas dataframe containing the time series variables
    variables : list containing names of the time series variables.
    """
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    for c in df.columns:
        for r in df.index:
            test_result = grangercausalitytests(data[[r, c]], maxlag=maxlag, verbose=False)
            p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
            #if verbose: print(f'Y = {r}, X = {c}, P Values = {p_values}')
            min_p_value = np.min(p_values)
            df.loc[r, c] = min_p_value
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    return df







cwd = os.getcwd()

folder = sys.argv[1]


path = cwd+'/'+folder

grangerdfs = []

donecolns = False
test = 'ssr_chi2test'
maxlag = 1

names = []

# OBTAIN GRANGER DFS FOR EACH FILE IN FOLDER
for i, file in enumerate(os.listdir(path)):
    if "summary_" not in file or "csv" not in file:
        continue
    namebegin = file.split('_x')[0]
    names.append(namebegin.split('_')[1])
    print(i, file)
    fulldf = pd.read_csv(path+'/'+file)


    df = fulldf._get_numeric_data()
    nondif = [c for c in df.columns if 'dif' not in c]
    df = df[nondif]
    # eliminating colns with nans 
    nonull = [ c for c in df.columns if c not in df.columns[df.isnull().any()].tolist()+['Unnamed: 0']]
    df = df[nonull]
    column_names = df.columns

    stationary_df = np.log(df + 1e-6).diff().dropna()
    data = stationary_df.to_numpy()

    if donecolns==False:
        # only for 1st
        print('getting columns')
        accepted_column_names = get_columns(data)
        donecolns = True
        print('Got columns')

    print('Doing granger \n \n')
    granger = grangers_causation_matrix(df[accepted_column_names], variables = accepted_column_names, test=test,maxlag=maxlag)  
  

    grangersub0p05 = granger.apply(lambda x: x < 0.05)
    sub0 = granger[grangersub0p05]
    filled = filled=sub0.replace(to_replace=np.NaN, value=1)

    nocoln = filled.reset_index()
    nocoln=nocoln.drop(columns=['index'])
    inv = filled.T.reset_index().drop(columns=['index'])
    bidirectional = pd.concat([nocoln, inv], axis=1)

    grangerdfs.append(bidirectional)

    print('Done granger')

results = pd.DataFrame(columns=names)

for coln in grangerdfs[0]:
    colnlist = []
    for df in grangerdfs:
        colnlist.append(df[coln])
    arr = np.array(colnlist)
    print(arr.shape)
    kmeans = KMeans(n_clusters=4, random_state=0, n_init='auto').fit(arr)
    print('Kmeans based on {} granger'.format(coln))
    results[coln] = kmeans.labels_
    print(names)
    print(kmeans.labels_)

print(results)

print('Took ', (time.time()-starttime)/60, 'minutes')

