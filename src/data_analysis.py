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
from numbers import Number

import numpy as np


def lin_reg_wrapper(X, y, display_results = False):
    
    # reshape if X represents one feature only (1 dimensional)
    if isinstance(X[0], Number):
        one_feature = True
        X = X.reshape(-1,1)
    else:
        one_feature = False
        X = np.array(X)

    # display scattergraph of data
    if display_results:
        if one_feature:
            plt.scatter(X,y)
            plt.show()
        else:
            pass
    
    if len(X) > 1:
        linreg = LinearRegression().fit(X, y)
        score = linreg.score(X,y)
        if one_feature:
            r, p = None, None #pearsonr(X.reshape(1,-1),y)
            pass
        else:
            r, p = None, None
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
    
    return score, r, p
    
    
def GCSE_on_midYIS_regression(years = de.ALL_YEARS, subject = 'Mathematics', criteria = 'Actual GCSE Points', 
                              display_results = False, verbose = False):
    """
    

    Parameters
    ----------
    years : TYPE list, optional 
        DESCRIPTION. The default is de.ALL_YEARS. Must be a subset of this list.
    subject : TYPE string, optional
        DESCRIPTION. The default is 'Mathematics'. Must be one of de.SUBJECTS
    criteria : TYPE string, optional
        DESCRIPTION. The default is 'Actual GCSE Points'. Alternatively use 'Predicted GCSE Points'
    display_results : TYPE boolean, optional
        DESCRIPTION. The default is False.
    verbose : TYPE boolean, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    dict
        DESCRIPTION. Dictionary containing results of correlation analysis and linear regression, or containing null values
                    if insufficient data is found.

    """
    
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
    
    score, r, p = lin_reg_wrapper(X, y, display_results = display_results)
        
    return {'Raw data' : data, 'Data clean summary' : removed_rows_summary, 'R2 score' : score, 'R' : r, 'p value' : p}
 
def do_ttest(results_dict, 
            keys_to_compare = ['Numeric (only TAGS/CAGS years)', 'Numeric (excluding TAGS/CAGS)']):
    
    """
    Carry out t-test on dictionary containing correlation results 
    """
    
    df = pd.DataFrame.from_dict(results_dict)

    df_test = df.loc[keys_to_compare]
    df_test.dropna(axis = 1, inplace = True)
    vals = (df_test.iloc[1, :] - df_test.iloc[0,:]).values
    
    return ttest_1samp(vals, popmean = 0)  

def test_lin_reg_on_MidYIS():
    ### code below carries out a random sample of subjects and outputs results of linear regression and correlation analysis here.  
    ### Jupyter notebook code uses the same function to create results for all subjects and save results
    n = random.randint(1,len(de.SUBJECTS)- 2)
    for subject in de.SUBJECTS[n:n+2]:
        #subject = 'Mathematics'
        GCSE_on_midYIS_regression(years = de.ALL_YEARS, subject = subject, 
                                   display_results = True, verbose = True)
    

def lin_reg_from_maths_data(df, dep_col = 'Average GCSE score', ind_cols = ['Final test Yr 10'], 
                            display_plots = False, verbose = False):
    
    cols = np.append(ind_cols, dep_col) 
    # get rid of NaN values in the relevant columns
    total_rows = 0
    for col in cols:
        mask = df[col].isna()
        if len(df[mask].index):
            if verbose:
                print("These rows to be dropped due to column {1}:\n {0}".format(df[mask], col)) 
            total_rows += len(df[mask].index)
            df = df[mask == False]

    # deal with regression on just one independent variable
    if len(ind_cols) == 1:
        ind_cols = ind_cols[0]
        
    y = df[dep_col].values
    X = df[ind_cols].values
    
    score, r, p = lin_reg_wrapper(X, y, display_results = display_plots)
    
    return score

def get_UMS(mark, grade, all_boundaries, year_key):
    """
    

    Parameters
    ----------
    mark : TYPE float
        DESCRIPTION. represents a score, must be within the limits of the values in the boundaries dictionary
    grade : TYPE integer grade, 
        DESCRIPTION. must be one of the boundaries keys
    boundaries : TYPE dictionary
        DESCRIPTION. keys are integers representing grades, values are floats representing lower boundary of each grade
                     key 0 must represent lowest grade and maximum key is a dummy grade with boundary of the max possible score

    Returns
    -------
    TYPE float
        DESCRIPTION. percentage adjusted for the different sizes of the grade boundaries

    """
    # deduce grade matching mark from boundaries dictionary
    boundaries = all_boundaries[year_key]
    # initialise deduced_grade as top grade in case mark is 100%
    deduced_grade = max(boundaries.keys()) - 1
    # iterate through grade boundaries
    ordered_grades = list(boundaries.keys())
    ordered_grades.sort()
    for level in ordered_grades:
        if mark < boundaries[level]:
            deduced_grade = level-1
            break
    
    # the level found should match the grade passed
    try:
        assert(deduced_grade == grade)
    except AssertionError:
        print("Mark passed is {0}".format(mark))
        print("Deduced grade is {0}".format(deduced_grade))
        print("Passed grade is {0}".format(grade))
        print("Boundaries dict is {0}".format(boundaries))
    
    # boundaries dict inculdes dummy grade at 100%
    UMS_grade_gap = 100/(max(boundaries.keys()) - 1)
    UMS_start = UMS_grade_gap*grade
    boundary_gap = boundaries[grade+1] - boundaries[grade]
    
    #print(UMS_grade_gap)
    #print(boundary_gap)
    return UMS_start + (mark-boundaries[grade])*UMS_grade_gap/boundary_gap

#boundaries = {0: 0, 1: 10, 2: 30, 3: 50, 4:80, 5: 100}

#print(get_UMS(20, 1, boundaries))
       
def estimate_boundaries(df):
    # 'Source file' is a proxy for the GCSE year
    year_groups = df.groupby(['Source file'])
    all_boundaries = {}
    for year in year_groups:
        # Group into grades
        grade_groups = year[1].groupby('Actual GCSE Points')
        # Find lowest and highest marks matching each grade
        low = {g[0] : min(g[1]['Average GCSE score']) for g in grade_groups}
        high = {g[0] : max(g[1]['Average GCSE score']) for g in grade_groups}
        
        #print(low)
        #print(high)
        all_boundaries[year[0]] = {}
        ordered_grades = [g[0] for g in grade_groups]
        ordered_grades.sort()
        
        for grade in ordered_grades:
    
            if high.get(grade - 1):
                # choose random boundary between the two grades based on the available data
                diff = low[grade] - high[grade - 1]
                
                all_boundaries[year[0]][grade] = max(random.randint(0,diff), 1) + high[grade - 1]
     
            else:
                # lowest grade in data - no further inference can be done on lower boundary
                all_boundaries[year[0]][grade] = low[grade]
        
        # ensure there is a dummy grade representing full marks
        all_boundaries[year[0]][grade + 1] = 100
        
    return all_boundaries
    
def do_linear_regression_for_maths_data():
#if __name__ == "__main__":
    data = pd.read_csv("{0}/all_maths_data_2016_to_2019.csv".format(de.SOURCE_DATA_DIR))
    
    # estimate the grade boundaries from the data
    all_boundaries = estimate_boundaries(data)
    # create UMS column based on these boundaries
    data['UMS'] = data.apply(lambda x: get_UMS(x['Average GCSE score'], x['Actual GCSE Points'], 
                                               all_boundaries, x['Source file']), axis = 1)
    
    dep_col = ['UMS']
    independent_cols = ['Test 0 Yr 9', 'MidYIS overall score', 'Test 1 Yr 9',
           'Test 2 Yr 9', 'Final test Yr 9', 'Test 0 Yr 10',
           'Test 1 Yr 10', 'Test 2 Yr 10', 'Final test Yr 10',
           'Test 0 Yr 11', 'Test 1 Yr 11','Final test Yr 11' ,
           ]
    dodgy_cols = ['Test 3 Yr 9','Test 2 Yr 11','Test 3 Yr 10']
    
    selected_cols = independent_cols#['Final test Yr 9' ,'Final test Yr 10', 'Final test Yr 11']
    
    scores = {}
    collinearity_scores = {}
    cols = []
    for i, col in enumerate(selected_cols):
        cols.append(col)
        scores[cols[-1]] = {'R2 score for single test' : lin_reg_from_maths_data(data, dep_col = dep_col, ind_cols = cols[-1]),
                            'R2 score using all tests to this point' : lin_reg_from_maths_data(data, dep_col = dep_col, ind_cols = cols)
                                       }#['Test 0 Yr 9', 'Final test Yr 9', 'Final test Yr 10', 'Final test Yr 11'])
        collinearity_scores[cols[-1]] = {}
        if i > 0:
            # test for collinearity
            for colj in cols:
                dep_colj = colj
                ind_cols = [c for c in cols if not c == colj]
                #print("Ind {0}".format(ind_cols))
                #print("Dep {0}\n".format(dep_col))
                R2_score = lin_reg_from_maths_data(data, dep_col = dep_colj, ind_cols = ind_cols,
                                                   display_plots = False, verbose = False)
                
                
            
                collinearity_scores[colj][i] = 1/(1-R2_score)
            #print("Test: {0} gives: {1}".format(col, collinearity_scores[cols[-1]]))

            
            
    df = pd.DataFrame.from_dict(scores, orient = 'index')
    print(df)
    df_collin = pd.DataFrame.from_dict(collinearity_scores, orient = 'index')
    #print(df_collin)
    df_collin.to_csv("{0}/Collinearity_test for maths dept tests.csv".format(de.RESULTS_DIR))
    #df.columns = ['R2 score','Datapoints']
do_linear_regression_for_maths_data()
        
