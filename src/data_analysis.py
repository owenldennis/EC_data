# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 12:34:21 2022

@author: owen
"""

import data_extraction as de
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def GCSE_on_midYIS_regression(subject = 'Mathematics', criteria = 'Actual GCSE Points', verbose = False):
    
    # extract relevant data
    data, removed_rows_summary = de.extract_GCSE_and_midYIS_data(subject = subject, criteria = criteria,
                                            remove_non_numeric_values = True,
                                            verbose = verbose)
    
    # display scattergraph of data

    plt.scatter(data[('MidYIS', 'Overall Score')], data[subject, criteria])
    display(removed_rows_summary)
    plt.show()
    
    # linear regression
    X = data['MidYIS', 'Overall Score'].values.reshape(-1,1)
    y = data[subject, criteria].values
    if len(X) > 1:
        linreg = LinearRegression().fit(X, y)
        #predictions = linreg.predict(X).round()
        #Sxy = ((y - predictions)** 2).sum()
        #Syy = ((y - y.mean()) ** 2).sum()
        #print("Rounded predictions gives R^2 score of {0:.2f}".format(1-Sxy/Syy))
        print("Standard Regression gives R^2 score of {0:.2f}".format(linreg.score(X, y)))
    else:
        print("Insufficint data for linear regression : {0} datapoints found".format(len(X)))
        
if __name__ == "__main__":
    
    
    for subject in de.SUBJECTS:



        GCSE_on_midYIS_regression(subject = subject, verbose = False)
        
