# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 16:52:02 2022

@author: owen
"""
### Lots of data for either only GCSE or only ALIS (mainly the latter).
### So could merge all ALIS files (all pupils have av GCSE score I think).
### Once all successfully merged pupil are concatenated can use the GCSE/ALIS data for MidYIS and av GCSE score comparison
### 




import ALIS_data_extraction as ALIS_ext
import data_extraction as de
import pandas as pd
import numpy as np

ALL_ALIS_FILE = "{0}/all_years.csv".format(ALIS_ext.ALIS_DATA_DIR)
EXTRACTED_DATA_DIR = "{0}/Extracted data files/Merged_ALIS_and_GCSE_data".format(de.SOURCE_DATA_DIR)

# link from GCSE and MidYIS filenames to matching (hopefully) ALIS data filenames
YEAR_MATCH = {'Yr 9 2012_13' : '2017.csv',
              'Yr 9 2013_14' : '2018.csv',
              'Yr 9 2014_15' : '2019.csv',
              'Yr 9 2015_16' : '2020.csv',
              'Yr 9 2016_17 (9-1)' : '2021.csv'}

midYIS_data_years = de.ALL_YEARS

def pivot_dataframe(df, pivot_index = ['Surname', 'Forename'], 
                    pivot_columns = 'Subject Title ', 
                    pivot_values = 'A level Points', 
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
            grade = df_ref.loc[row_index, [pivot_values]][pivot_values]
            
            matching = new_df[new_df['Surname'] == surname]
            matching = matching[matching.Forename == forename]
            matching = matching[subject_title].copy()
            #matching.dropna(inplace = True)
            try:
                assert(len(matching.index) == 1)
            except AssertionError:
                print("Multiple matches for name {0} and subject {1}.".format(str(forename) + " " + str(surname), subject_title))
                print("Dataframe of matching entries is {0}\n".format(matching))
                    
            try:
                assert(matching.iloc[0] == grade)
            except AssertionError:
                print("Mismatch between grade stored in original dataframe and pivoted dataframe.")
                print("Row of original dataframe for {1} is \n{0}\n".format(str(forename) + " " + str(surname) + " " + subject_title,
                                                                            df_ref.loc[row_index]))
            if verbose:
                print("Confirming pivot operation for {0} {1} {2}".format(forename, surname, subject_title))
                print("Grade stored in pivoted dataframe : {0}".format(matching.iloc[0]))
                print("Grade stored in original dataframe : {0}".format(grade))
    
        new_df.to_csv("{0}/test_join.csv".format(de.TEMP_DIR))
    
    return new_df


def merge_GCSE_and_ALIS_results(year, MidYIS_file = de.MidYIS_GCSE_DATA_FILE, use_all_ALIS_years = False,
                                remove_AS_results = True, grading_type = 'A level Points', 
                                test_run = True, store_failed_matches = True, verbose = False):
    
    try:
        assert(not store_failed_matches or test_run)
    except AssertionError:
        print("Dataframes of failed matches are only created if test_run is set to True")
    
    dfs = {}
    
    # read in MidYIS and GCSE data for year passed
    # check if the year is one where numeric and alpha grades need to be combined into one dataframe
    if year in ['Yr 9 2014_15', 'Yr 9 2015_16']:
        dfs["MidYIS data for " + year] = de.merge_years_wrapper(years = [year, year +' (9-1)'], test_run = False)[0]
    else:
        dfs["MidYIS data for " + year] = de.get_columns_and_flatten(year)
    
    # read in ALIS data for corresponding year
    if use_all_ALIS_years:
        ALIS_df = pd.read_csv(ALL_ALIS_FILE)
    else:
        ALIS_df = pd.read_csv("{0}/{1}".format(ALIS_ext.ALIS_DATA_DIR, YEAR_MATCH[year]))
    
    #print(ALIS_df.loc[[40,111,345], ['Surname', 'Forename', 'Initial']])
    # remove AS results if required
    if remove_AS_results:
        ALIS_df = ALIS_df[ALIS_df['Exam Type'] == 'A-Level (A2)']
        if verbose:
            print("AS results removed from ALIS datafile for year {0}".format(YEAR_MATCH[year]))
    
    # remove NaN entries in pivot columns
    original_length = len(ALIS_df.index)
    ALIS_df.dropna(subset = ['Surname', 'Forename', 'Initial'], inplace = True)
    print("{0} rows dropped for year {1} due to NaN entry in one or other name column".
          format(len(ALIS_df.index) - original_length, year))
    
    
    # pivot ALIS data so subjects are column headings with grade/point values

    dfs["ALIS data for " + YEAR_MATCH[year]] = pivot_dataframe(ALIS_df,
                                                    pivot_index = ['Surname', 'Forename', 'Initial'], 
                                                    pivot_columns = 'Subject Title ', 
                                                    pivot_values = grading_type, 
                                                    columns_to_drop = ["Subject Title ", 'A level Grade','Exam Type',  'A level Points',
                                                                         'Syllabus Title', 'Exam Board', 'Syllabus Code'],
                                                    check_for_errors = True, verbose = verbose)
   # print(dfs["MidYIS data for " + year]['Surname'].sort_values())
    #print(dfs["ALIS data for " + YEAR_MATCH[year]]['Surname'].sort_values())
    #print(dfs["ALIS data"].head())

    [dfs[key].to_csv("{0}/{1}.csv".format(de.TEMP_DIR, key)) for key in dfs.keys()]
    merged_data, MidYIS_only, ALIS_only = de.merge_wrapper(dfs, keys_in_order = ["MidYIS data for " + year, "ALIS data for " + YEAR_MATCH[year]],
                                   on = ['Surname', 'Initial'], test_run = test_run)
    
    merged_data.drop(columns = ['Forename_y'], inplace = True)
    merged_data.rename(columns = {'Forename_x' : 'Forename'}, inplace = True)
    
    if store_failed_matches:
        MidYIS_only.to_csv("{0}/MidYIS_with_no_ALIS_match_{1}".format(EXTRACTED_DATA_DIR, YEAR_MATCH[year]))
        ALIS_only.to_csv("{0}/ALIS_with_no_MidYIS_match_{1}".format(EXTRACTED_DATA_DIR, YEAR_MATCH[year]))
    
    merged_data.to_csv("{0}/merged_MidYIS_ALIS_{1}".format(EXTRACTED_DATA_DIR, YEAR_MATCH[year]))
    
    dfs['merged_data'] = merged_data
    dfs['MidYIS_only'] = MidYIS_only
    dfs['ALIS_only'] = ALIS_only
    return dfs

if __name__ == '__main__':
    
    # to extract, merge and store the data with accurate details of failed merging printed:
    # first run the code with test_run = True
    # then run again with test_run = False
    test_run = True
    
    summary_results = {}

    for year in YEAR_MATCH.keys():
        dataframes = merge_GCSE_and_ALIS_results(year, MidYIS_file = de.MidYIS_GCSE_DATA_FILE, use_all_ALIS_years = False,
                                    remove_AS_results = True, grading_type = 'A level Points', 
                                    test_run = test_run, store_failed_matches = test_run, verbose = False)
        if test_run:
            merged_df = dataframes['merged_data']
            number_merged = len(merged_df[merged_df['_merge'] == 'both'].index)
            summary_results[year] = {'MidYIS only' : len(dataframes['MidYIS_only'].index),
                                 'ALIS_only' : len(dataframes['ALIS_only'].index),
                                 'Succesfully merged' : number_merged}
    
    
    if test_run:
        print(pd.DataFrame.from_dict(summary_results))
        pd.DataFrame.from_dict(summary_results).to_csv("{0}/summary_for_all_years.csv".format(EXTRACTED_DATA_DIR))