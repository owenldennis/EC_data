# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 12:34:21 2022

@author: owen
"""

import data_extraction as de
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import random
from scipy.stats import pearsonr
from scipy.stats import ttest_1samp

import numpy as np


def GCSE_on_midYIS_regression(years = de.ALL_YEARS, subject = 'Mathematics', criteria = 'Actual GCSE Points', 
                              display_results = False, verbose = False):
    
    # extract relevant data
    #if verbose:
    #    print("Years to be extracted are : {0}".format(years))
    data, removed_rows_summary = de.extract_GCSE_and_midYIS_data(years = years, subject = subject, criteria = criteria,
                                            remove_non_numeric_values = True,
                                            verbose = verbose)
    if not len(data.index):
        return {'Raw data' : None, 'Data clean summary' : None, 'R2 score' : np.nan, 'R' : np.nan, 'p value' : np.nan}
        
    # display scattergraph of data
    if display_results:
        plt.scatter(data[('MidYIS', 'Overall Score')], data[subject, criteria])
        print(removed_rows_summary)
        plt.show()
    
        # linear regression
    X = data['MidYIS', 'Overall Score'].values
    y = data[subject, criteria].values
    if len(X) > 1:
        linreg = LinearRegression().fit(X.reshape(-1,1), y)
        #predictions = linreg.predict(X).round()
        #Sxy = ((y - predictions)** 2).sum()
        #Syy = ((y - y.mean()) ** 2).sum()
        #print("Rounded predictions gives R^2 score of {0:.2f}".format(1-Sxy/Syy))
        score = linreg.score(X.reshape(-1,1),y)
        r, p = pearsonr(X,y)
        # could use Kendall-Tau if data is ranked...?
        if display_results:
            print("Standard Regression gives R^2 score of {0:.2f}".format(score))
            print("Correlation analysis gives r = {0:.2f} with p-value {1:.3f}".format(r,p))
    else:
        if display_results:
            print("Insufficient data for linear regression : {0} datapoints found".format(len(X)))
        score = 'Insufficient data'
        r = np.nan
        p = np.nan
        
    return {'Raw data' : data, 'Data clean summary' : removed_rows_summary, 'R2 score' : score, 'R' : r, 'p value' : p}
 
def do_ttest(results_dict, 
            keys_to_compare = ['Numeric (only TAGS/CAGS years)', 'Numeric (excluding TAGS/CAGS)']):
    
    df = pd.DataFrame.from_dict(results_dict)

    df_test = df.loc[keys_to_compare]
    df_test.dropna(axis = 1, inplace = True)
    vals = (df_test.iloc[1, :] - df_test.iloc[0,:]).values
    
    return ttest_1samp(vals, popmean = 0)  
     
if __name__ == "__main__":
    
    ### code below carries out a random sample of subjects and outputs results of linear regression and correlation analysis here.  
    ### Jupyter notebook code uses the same function to create results for all subjects and save results
    n = random.randint(1,len(de.SUBJECTS)- 2)
    for subject in de.SUBJECTS[n:n+2]:
        #subject = 'Mathematics'
        GCSE_on_midYIS_regression(years = de.ALL_YEARS, subject = subject, 
                                   display_results = True, verbose = True)
        
