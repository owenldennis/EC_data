# -*- coding: utf-8 -*-
"""
Spyder Editor

FUnctions for extracting data from CEM excel files for Eastbourne College project
This file contains functions to set up a dataframe containing all relevant information.

Below, there are (obsolete) functions for cross referencing of multiple csv files in order to extract the names of pupils and courses based on numerical codes

"""

import pandas as pd
#import csv
from numbers import Number
#import random 
import numpy as np
#import tabula
#import re
import name_disambiguation as name_dis

# source data directory from onedrive
SOURCE_DATA_DIR = "C:/Users/owen/OneDrive - Eastbourne College/School analytics project"
RESULTS_DIR = "{0}/Results".format(SOURCE_DATA_DIR)
EXTRACTED_DATA_DIR = "{0}/Extracted data files".format(SOURCE_DATA_DIR)
MidYIS_GCSE_DATA_FILE = "{0}/MidYIS_average_and_GCSE_scores.xlsm".format(SOURCE_DATA_DIR)
TEMP_DIR = "{0}/Temp".format(SOURCE_DATA_DIR)
# MidYIS excel files are imported as multi-level column dataframes.


"""
list of excel sheet titles (keys for extracted dictionary)
['Yr 9 2012_13', 'Yr 9 2013_14',  ***all subjects graded 1-8 on CEM scale***
 'Yr 9 2014_15', 'Yr 9 2014_15 (9-1)', ***all except English graded 1-8)***
'Yr 9 2015_16', 'Yr 9 2015_16 (9-1)', ***just a few pupils in maths, history and DT graded 1-8 still*** 
'Yr 9 2016_17 (9-1)', 'Yr 9 2017_18 (9-1)', 'Yr 9 2018_19 (9-1)'  ***all subjects graded 1-9***  
]
"""


ALL_YEARS = ['Yr 9 2012_13', 'Yr 9 2013_14',  #***all subjects graded 1-8 on CEM scale***
             'Yr 9 2014_15', 'Yr 9 2014_15 (9-1)', #***all except English graded 1-8)***
             'Yr 9 2015_16', 'Yr 9 2015_16 (9-1)', #***just a few pupils in maths, history and DT graded 1-8 still*** 
             'Yr 9 2016_17 (9-1)', 'Yr 9 2017_18 (9-1)', 'Yr 9 2018_19 (9-1)' # ***all subjects graded 1-9***  
             ]
# structure of original midYIS datafiles
SUBJECTS = ['Art & Design', 'Biology', 'Chemistry', 'Classical Civilisation', 
            'Design & Technology', 'Drama', 'English', 'English Literature', 
            'French', 'Geography', 'German', 'History', 'Latin', 'Mathematics', 
            'Music', 'Physical Education', 'Physics', 'Religious Studies', 'Science (Double)', 'Spanish']

SUBJECT_OPTIONS = ['Actual GCSE Points', 
                   'Overall Band', 'Overall Score', 'Predicted GCSE Points', 
                   'Raw Residual', 'Standardised Residual',]

MIDYIS_OPTIONS = ['Overall Score', 'Overall Band']

PUPIL_INFO_OPTIONS = ['Forename', 'Sex', 'Surname', 'Cemid', 'Cust',]

PUPIL_TUPLES = [('Pupil Information', h) for h in PUPIL_INFO_OPTIONS[:4]]
MidYIS_TUPLES = [('MidYIS', 'Overall Score')]
SUBJECT_TUPLES = [(subject, 'Actual GCSE Points') for subject in SUBJECTS]
COLUMN_TUPLES = PUPIL_TUPLES + MidYIS_TUPLES + SUBJECT_TUPLES

def select_frames(dict_of_dfs, keys, tuples): 
    
    valid_years = []
    for key in keys:
        try:
            dict_of_dfs[key][tuples]
            valid_years.append(key)
        except KeyError:
            pass
    return valid_years


def clean_data(data, subject, criteria, remove_non_numeric_values = True,
               verbose = False):
    
    raw_length = len(data.index)
    data = data.dropna()
    nan_removed_length = len(data.index)
    
    if remove_non_numeric_values:
        selected = data[(subject, criteria)]
        number_match = [isinstance(s, Number) for s in selected]
        not_number = [not n for n in number_match]
        data = data[number_match]
        only_numeric_length = len(data.index)
        removed_entries = list(set(selected[not_number]))
    else:
        only_numeric_length = "Not done"
        removed_entries = "Not done"
    

    summary_dict = {"Initial dataset length" : [raw_length],
                                        "After removing NaN entries" : [nan_removed_length],
                                        "After removing other non-numeric values" : [only_numeric_length],
                                        "Removed entries other than NaN" : [removed_entries]
                                        }
    summary_df = pd.DataFrame.from_dict(summary_dict, orient = 'index')#.columns = ['Length']
    summary_df.columns = ['length']
        
    return data, summary_df
 


def extract_GCSE_and_midYIS_data(years = ALL_YEARS, subject = 'Mathematics', criteria = 'Actual GCSE Points', 
                                 regression_tuple = ('MidYIS', 'Overall Score'),                              
                                 remove_non_numeric_values = True, verbose = False):
    
    # load all excel sheets from 2012 to 2018
    midyis_and_GCSE_data = {year : pd.read_excel(SOURCE_DATA_DIR + "/MidYIS_average_and_GCSE_scores.xlsm",
                                 sheet_name = year,
                            header = [0,1]) for year in ALL_YEARS 
                            }

    
    tuples = [('Pupil Information', 'Surname'),('Pupil Information', 'Forename'),('Pupil Information', 'Sex'),              
              regression_tuple, (subject, criteria)
              ]
    # add (subject, criteria) tuple to multicolumn tuples to extract relevant data
    #if verbose:
    #    print("years are {0}".format(years))
    #    print("Possible keys are {0}".format(midyis_and_GCSE_data.keys()))
    
    
    # pull out specific columns for a dataframe (relates to constants above) and concatenate
    valid_years = select_frames(dict_of_dfs = midyis_and_GCSE_data, keys = years, 
                                 tuples = tuples)
    
    if verbose:
        print("The valid sheet titles for this analysis are :{0}\n".format(valid_years))
    
    # extract and combine all relevant data into one dataframe   
    try:
        data = pd.concat([midyis_and_GCSE_data[year][tuples] for year in valid_years],
                  ignore_index = True)
        # clean data - if verbose is true, summary of removed items is printed
        data, removed_rows_summary = clean_data(data, subject = subject, criteria = criteria,
                                            remove_non_numeric_values = remove_non_numeric_values,
                                            verbose = verbose)
    except ValueError:
        if not valid_years:
            print("No matching data found")
            return pd.DataFrame(), None
        else:
            print("Not sure what's gone wrong!")
    
    return data, removed_rows_summary


def get_columns_and_flatten(year, column_tuples = COLUMN_TUPLES, excel_file = MidYIS_GCSE_DATA_FILE):
    # open passed excel file, extract relevant columns and flatten multi-column headings
    
    df = pd.read_excel(excel_file, sheet_name = year, header = [0,1])
    #print("After reading in:")
    #print(df['Pupil Information', 'Surname'][0])
    # remove any columns not appearing in the spreadsheet
    column_tuples = [c for c in column_tuples if c in df.columns]
    # extract desired columns
    df = df[column_tuples]

    #df.columns = df.columns.to_flat_index() 
    #df.columns = [' & '.join(col).rstrip('_') for col in df.columns.values]
    df.columns = [col[1] if col[0] == 'Pupil Information' else col[0] for col in df.columns.values]
    df[['Surname', 'Forename', 'Initial']] = df.apply(lambda x: name_dis.split_name_wrapper(x), axis = 1)
    #print("After tidying:")
    #print(df['Surname'][0])
    return df


def merge_wrapper(dfs_dict, keys_in_order = [], on = ['Forename', 'Surname', 'Sex', 'MidYIS', 'Cemid'], 
                  test_run = True, verbose = True):   
    # only merges dataframes created from the first two keys in dfs_dict
    # specifically used to merge across the split years (when some exams were numeric and some still letter grades)
    # if test_run is true, the dataframes will be merged with feedback given about number of matching entries etc
    # if test_run is false, inner merging will happen without checking for lost data


    # merge dataframes passed with names as keys
    if len(keys_in_order):
        names = keys_in_order
    else:
        names = list(dfs_dict.keys())
    if test_run:
        
        if verbose:
            print("The first few ordered entries for each dataframe passed:")
            [print(dfs_dict[key].head(20).loc[ : ,['Surname', 'Forename']].
                   sort_values(by = 'Surname', axis = 0)) for key in dfs_dict.keys()]
            print("Merging on {0}".format(on))
        
        print("The lengths of the two dataframes about to be merged are:")
        print("year {0} : {1}".format(names[0], len(dfs_dict[names[0]].index)))
        print("year {0} : {1}".format(names[1], len(dfs_dict[names[1]].index)))
        
        merged_df = dfs_dict[names[0]].merge(dfs_dict[names[1]], how = 'outer', on = on,
                                 indicator = True)
        
        left_only = merged_df[merged_df['_merge'] == 'left_only']
        right_only = merged_df[merged_df['_merge'] == 'right_only']
        
        print("There were {0} entries for {1} that didn't match entries in {2}".format(
            len(left_only.index),names[0], names[1]))
        print("There were {0} entries for {1} that didn't match entries in {2}".format(
            len(right_only.index),names[1], names[0]))
        
        #print("The column headings after merging are : {0}".format(merged_df.columns))
        print("The length of the merged dataframe is {0}".format(len(merged_df.index)))
        
        return merged_df, left_only, right_only
        
    else:
        #print("Just before merging: {0} and {1}".format(dfs_dict[names[0]]['Surname'][0], dfs_dict[names[1]]['Surname'][0]))
       
        dfs_dict['merged'] = dfs_dict[names[0]].merge(dfs_dict[names[1]], how = 'inner', on = on)
        #print("Immediately after merging: {0}".format(dfs_dict['merged']['Surname'][0]))
        return dfs_dict['merged'], pd.DataFrame(), pd.DataFrame()

    
def merge_years_wrapper(years, column_tuples = COLUMN_TUPLES, excel_file = MidYIS_GCSE_DATA_FILE,
                        test_run = False):
    
    assert(len(years) == 2)
    # extract relevant columns from excel file, flatten 
    
    dfs = {year : get_columns_and_flatten(year, column_tuples, excel_file) for year in years}

    # pass to merge_wrapper to merge entries 
    # only merges dataframes created from the first two year keys passed in years list
    # specifically used to merge across the split years (when some exams were numeric and some still letter grades)
    # if test_run is true, the dataframes will be merged with feedback given about number of matching entries etc
    # if test_run is false, inner merging will happen without checking for lost data
        
    return merge_wrapper(dfs, on = ['Forename', 'Surname', 'Initial','Sex', 'MidYIS', 'Cemid'], 
                         test_run = test_run)
    
    
    
#df = get_columns_and_flatten(year = 'Yr 9 2012_13')
if __name__ == "__main__":
    df = merge_years_wrapper(years = ['Yr 9 2015_16', 'Yr 9 2015_16 (9-1)'], test_run = True)[0]
    df.to_csv("{0}/test_merge.csv".format(TEMP_DIR))
        
        
        
        



"""
Code below is used for collating information about EC pupils from the ECI spreadsheets 
Spreadsheets are cross-referenced based on the unique ID codes
Probably all obsolete as the pd.merge() function does most of it!
And turns out not to be needed as the exam results are stored in CEM data
"""

# rename columns for midyis data
#midyis_2021.rename(columns = {'Unnamed: 6' : 'Score', 'Unnamed: 7' : 'Band'})
# make cross reference dictionary for passed columns (must be aligned)
def make_crossref_dict(df, keys_col_heading, vals_col_heading):
    keys_col = df[keys_col_heading]
    vals_col = df[vals_col_heading]
    return {key:vals_col[i] for i, key in enumerate(keys_col)}
 
# replace whitespace with '_' in all headings in dataframe
def remove_whitespace_in_col_headings(df):
    col_dict = {col : col.replace(' ', '_') for col in df.columns}
    df.rename(columns = col_dict, inplace = True)

# cross reference between two dataframes and append cross-referenced data to the first one passed in
def lookup_and_append_to_df(df_to_append, lookup_col_heading, new_col_heading,
                            df_source, keys_col_heading, values_col_heading, 
                            display_sample = False, verbose = False):

    d = make_crossref_dict(df_source, keys_col_heading, values_col_heading)
    missing_keys = [k for k in df_to_append[lookup_col_heading] if not k in d.keys()]
    for key in missing_keys:
        d[key] = 'Missing data'
    df_to_append[new_col_heading] = df_to_append[lookup_col_heading].map(lambda x : d[x])
    
    if display_sample:
        print("Random sample from appended dataframe:")
        size = 10
        random_indices = np.random.randint(len(df_to_append.index), size = size)
        sampled_df = df_to_append[[lookup_col_heading, new_col_heading]].loc[random_indices, :].sort_values(by = lookup_col_heading)
        print(sampled_df)
        keys = df_to_append[lookup_col_heading].loc[random_indices]
        #print("Keys are: {0}".format(keys))
        df_mask = df_source.where(df_source[keys_col_heading].isin(keys))
        print("Matching rows from source dataframe")
        df_to_display = df_mask[[keys_col_heading, values_col_heading]].dropna().sort_values(by = keys_col_heading)
        print(df_to_display)
    
    if verbose:
        print("There were {0} unique entries in the lookup dataframe which could not be found in the source dataframe".format(len(set(missing_keys))))
        print("The new column contains {0} 'Missing data' entries".
              format(len(df_to_append[df_to_append[new_col_heading] == 'Missing data'].index)))
        
        lookup_series = df_to_append[lookup_col_heading]
        print("Lookup column contained {0} entries, of which {2} were NaN. There were {1} unique entries.".
             format(len(lookup_series.index), len(lookup_series.value_counts().index), lookup_series.isnull().sum()))

def collate_pupil_data_from_EC_files():  
    # import relevant data
    results_dataframe = pd.read_csv(SOURCE_DATA_DIR + "/ECi_External Exams_csv_results.csv")
    programmes_subjects_df = pd.read_csv(SOURCE_DATA_DIR + "/ECi_External Exams_csv_programmes.csv")
    pupil_info_df = pd.read_csv(SOURCE_DATA_DIR + "/ECi_Pupil Data_pupils.csv")     
    # Remove whitespace from column headings   
    remove_whitespace_in_col_headings(results_dataframe)
    remove_whitespace_in_col_headings(programmes_subjects_df)
    remove_whitespace_in_col_headings(pupil_info_df)
    
    # cross reference and append data to results_dataframe
    
    # append exam course names
    lookup_and_append_to_df(results_dataframe, 'Programme_Id', 'Programme_Name',
                            programmes_subjects_df, 'Programme_Id', 'Name',
                            display_sample = False, verbose = False)
    # append pupil initials
    lookup_and_append_to_df(results_dataframe, 'Pupil_Id', 'Initials',
                            pupil_info_df, 'Id', 'Name_Initials',
                            display_sample = False, verbose = False)
    # append pupil surnames
    lookup_and_append_to_df(results_dataframe, 'Pupil_Id', 'Surname',
                            pupil_info_df, 'Id', 'Surname',
                            display_sample = False, verbose = False)
    # append pupil forenames
    lookup_and_append_to_df(results_dataframe, 'Pupil_Id', 'Forename',
                            pupil_info_df, 'Id', 'Forename',
                            display_sample = False, verbose = False)
    # append pupil date of birth
    lookup_and_append_to_df(results_dataframe, 'Pupil_Id', 'DOB',
                            pupil_info_df,'Id', 'DOB',
                            display_sample = False, verbose = False)







#print(results_dataframe[['Programme_Id', 'Programme_Name', 'First_Grade', 'Initials']].head(10))
