# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 16:52:02 2022

@author: owen
"""
### Do we create one big GCSE and MidYIS dataframe?  Or merge individually within each year.
### Need to sort out names again to standardise between ALIS and MidYIS files.
### Need to sort out multiple names occuring in ALIS data! (multiple A levels and multiple AS levels for each)


import ALIS_data_extraction as ALIS_ext
import data_extraction as de
import pandas as pd
import numpy as np

ALL_ALIS_FILE = "{0}/all_years.csv".format(ALIS_ext.ALIS_DATA_DIR)

# link from GCSE and MidYIS filenames to matching (hopefully) ALIS data filenames
YEAR_MATCH = {'Yr 9 2012_13' : '2017.csv',
              'Yr 9 2013_14' : '2018.csv',
              'Yr 9 2014_15' : '2019.csv',
              'Yr 9 2015_16' : '2020.csv',
              'Yr 9 2016_17 (9-1)' : '2021.csv'}

midYIS_data_years = de.ALL_YEARS

def pivot_dataframe(df, pivot_index = ['Surname', 'Forename'], 
                    pivot_columns = 'Subject Title ', 
                    pivot_values = 'A level Grade', 
                    columns_to_drop = ["Subject Title ", 'A level Grade','Exam Type',  'A level Points',
                                         'Syllabus Title', 'Exam Board', 'Syllabus Code'],
                    check_for_errors = True, verbose = False):
    
    # pivots passed dataframe according to the parameters passed
    # checks for consistency with original if check_for_errors is True
    
    #df = pd.read_csv("{0}/{1}".format(ALIS_ext.ALIS_DATA_DIR, '2017.csv'))
    if check_for_errors:
        df_ref = df.copy()

    
    # pivot
    new_df = df.pivot(index = pivot_index, columns = pivot_columns, values = pivot_values)
    new_df.reset_index(inplace = True)
       
    # drop columns that are now irrelevant from original df
    df.drop(columns = columns_to_drop, inplace = True)
    
    # join back to original dataframe with duplicates removed
    new_df = new_df.join(other = 
                         df.drop_duplicates(subset = pivot_index).set_index(pivot_index), 
                                            on = pivot_index, how = 'left')
    
    # test to confirm that grades are correctly allocated
    if check_for_errors:
        for row_index in df_ref.index:
            surname = df_ref.loc[row_index,['Surname']]['Surname']
            forename = df_ref.loc[row_index,['Forename']]['Forename']
            subject_title = df_ref.loc[row_index, ['Subject Title ']]['Subject Title ']
            grade = df_ref.loc[row_index, ['A level Grade']]['A level Grade']
            
            matching = new_df[new_df['Surname'] == surname]
            matching = matching[matching.Forename == forename]
            matching = matching[subject_title].copy()
            #matching.dropna(inplace = True)
            try:
                assert(len(matching.index) == 1)
            except AssertionError:
                print("Multiple matches for name {0} and subject {1}.".format(forename + " " + surname, subject_title))
                print("Dataframe of matching entries is {0}\n".format(matching))
                    
            try:
                assert(matching.iloc[0] == grade)
            except AssertionError:
                print("Mismatch between grade stored in original dataframe and pivoted dataframe.")
                print("Row of original dataframe for {1} is \n{0}\n".format(forename + " " + surname + " " + subject_title,
                                                                            df_ref.loc[row_index]))
            if verbose:
                print("Confirming pivot operation for {0} {1} {2}".format(forename, surname, subject_title))
                print("Grade stored in pivoted dataframe : {0}".format(matching.iloc[0]))
                print("Grade stored in original dataframe : {0}".format(grade))
    
        new_df.to_csv("{0}/test_join.csv".format(de.TEMP_DIR))
    
    return new_df


def merge_GCSE_and_ALIS_results(year, MidYIS_file = de.MidYIS_GCSE_DATA_FILE,
                                remove_AS_results = True, use_points = True, verbose = False):
    
    dfs = {}
    
    # read in MidYIS and GCSE data for year passed
    # check if the year is one where numeric and alpha grades need to be combined into one dataframe
    if year in ['Yr 9 2014_15', 'Yr 9 2015_16']:
        dfs["MidYIS data for " + year] = de.merge_years_wrapper(years = [year, year +' (9-1)'], test_run = False)
    else:
        dfs["MidYIS data for " + year] = de.get_columns_and_flatten(year)
    
    # read in ALIS data for corresponding year
    ALIS_df = pd.read_csv("{0}/{1}".format(ALIS_ext.ALIS_DATA_DIR, YEAR_MATCH[year]))
    
    # remove AS results if required
    if remove_AS_results:
        ALIS_df = ALIS_df[ALIS_df['Exam Type'] == 'A-Level (A2)']
        if verbose:
            print("AS results removed from ALIS datafile for year {0}".format(YEAR_MATCH[year]))
    
    # pivot ALIS data so subjects are column headings with grade/point values
    dfs["ALIS data for " + YEAR_MATCH[year]] = pivot_dataframe(ALIS_df,
                                                    pivot_index = ['Surname', 'Forename'], 
                                                    pivot_columns = 'Subject Title ', 
                                                    pivot_values = 'A level Grade', 
                                                    columns_to_drop = ["Subject Title ", 'A level Grade','Exam Type',  'A level Points',
                                                                         'Syllabus Title', 'Exam Board', 'Syllabus Code'],
                                                    check_for_errors = True, verbose = verbose)
                                
   # print(dfs["MidYIS data for " + year]['Surname'].sort_values())
    #print(dfs["ALIS data for " + YEAR_MATCH[year]]['Surname'].sort_values())
    #print(dfs["ALIS data"].head())
    
    merged_data = de.merge_wrapper(dfs, on = 'Surname', test_run = True)
    
    merged_data.to_csv("{0}/merged_MidYIS_ALIS.csv".format(de.TEMP_DIR))
    
    return merged_data

if __name__ == '__main__':
    year = list(YEAR_MATCH.keys())[1]
    merge_GCSE_and_ALIS_results(year, verbose = False)
