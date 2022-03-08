# -*- coding: utf-8 -*-
"""
Spyder Editor

Pupil data for Eastbourne College project
This file contains functions to set up a dataframe containing all relevant information.
Cross referencing of multiple csv files in order to extract the names of pupils and courses based on numerical codes

"""

import pandas as pd
#import csv
from numbers import Number
#import random 
import numpy as np
#import openpyxl

# source data directory from onedrive
SOURCE_DATA_DIR = "C:/Users/owen/OneDrive - Eastbourne College/School analytics project"

# MidYIS excel files are imported as multi-level column dataframes.
# Decide which data to analyse
USE_NUMERICAL_GRADING_DATA = True
USE_OLD_GRADING_DATA = True
REMOVE_CAGS_TAGS = False
#print(TUPLES)

"""
list of excel sheet titles (keys for extracted dictionary)
['Yr 9 2012_13', 'Yr 9 2013_14',  ***all subjects graded 1-8 on CEM scale***
 'Yr 9 2014_15', 'Yr 9 2014_15 (9-1)', ***all except English graded 1-8)***
'Yr 9 2015_16', 'Yr 9 2015_16 (9-1)', ***just a few pupils in maths, history and DT graded 1-8 still*** 
'Yr 9 2016_17 (9-1)', 'Yr 9 2017_18 (9-1)', 'Yr 9 2018_19 (9-1)'  ***all subjects graded 1-9***  
]
"""
SHEET_TITLES_OLD = ['Yr 9 2012_13', 'Yr 9 2013_14', 'Yr 9 2014_15', 'Yr 9 2015_16']
if REMOVE_CAGS_TAGS:
    SHEET_TITLES_NEW = ['Yr 9 2014_15 (9-1)', 'Yr 9 2015_16 (9-1)','Yr 9 2016_17 (9-1)']
else:
    SHEET_TITLES_NEW =  ['Yr 9 2014_15 (9-1)', 'Yr 9 2015_16 (9-1)','Yr 9 2016_17 (9-1)', 
                     'Yr 9 2017_18 (9-1)', 'Yr 9 2018_19 (9-1)']

SHEETS = SHEET_TITLES_OLD

if USE_NUMERICAL_GRADING_DATA:
    if USE_OLD_GRADING_DATA:
        SHEETS = SHEET_TITLES_OLD + SHEET_TITLES_NEW
    else:
        SHEETS = SHEET_TITLES_NEW

# struture of original midYIS datafiles
SUBJECTS = ['Art & Design', 'Biology', 'Chemistry', 'Classical Civilisation', 
            'Design & Technology', 'Drama', 'English', 'English Literature', 
            'French', 'Geography', 'German', 'History', 'Latin', 'Mathematics', 
            'Music', 'Physical Education', 'Physics', 'Religious Studies', 'Science (Double)', 'Spanish']

SUBJECT_OPTIONS = ['Actual GCSE Points', 'Cemid', 'Cust', 
                   'Overall Band', 'Overall Score', 'Predicted GCSE Points', 
                   'Raw Residual', 'Standardised Residual',]

MIDYIS_OPTIONS = ['Overall Score', 'Overall Band']

PUPIL_INFO_OPTIONS = ['Forename', 'Predicted GCSE Points', 'Sex', 'Surname']

def select_frames(dict_of_dfs, keys, tuples): 
    
    valid_sheets = []
    for key in keys:
        try:
            dict_of_dfs[key][tuples]
            valid_sheets.append(key)
        except KeyError:
            pass
    return valid_sheets

#def is_number(entry):
#    if type(entry) == int:
#        return True
#    if type(entry) == float:
#        return True
#    if type(entry) == 'numpy.float64':
#        return True
#    
#    return False#
#
#def find_numeric_entries(series):
#    return [is_number(s) for s in series]    

def clean_data(data, subject,  criteria, remove_non_numeric_values = True,
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
                                        #"After removing U grades" : [U_removed_length],
                                        "After removing other non-numeric values" : [only_numeric_length],
                                        "Removed entries other than NaN" : [removed_entries]
                                        }
    summary_df = pd.DataFrame.from_dict(summary_dict, orient = 'index')#.columns = ['Length']
    summary_df.columns = ['length']
        
    return data, summary_df
 


def extract_GCSE_and_midYIS_data(subject = 'Mathematics', criteria = 'Actual GCSE Points',
                                 remove_non_numeric_values = True, verbose = False):
    
    # load all excel sheets from 2012 to 2018
    midyis_and_GCSE_data = pd.read_excel(SOURCE_DATA_DIR + "/MidYIS_average_and_GCSE_scores.xlsm",
                                 sheetname = None,
                            header = [0,1]) 

    
    tuples = [('MidYIS', 'Overall Score'), ('Pupil Information', 'Surname'), (subject, criteria)]
    # add (subject, criteria) tuple to multicolumn tuples to extract relevant data

    # pull out specific columns for a dataframe (relates to constants above) and concatenate
    valid_sheets = select_frames(dict_of_dfs = midyis_and_GCSE_data, keys = SHEETS, 
                                 tuples = tuples)
    
    if verbose:
        print("The valid sheet titles for this analysis are :{0}\n".format(valid_sheets))
    
    # extract and combine all relevant data into one dataframe   
    data = pd.concat([midyis_and_GCSE_data[sheet][tuples] for sheet in valid_sheets],
                  ignore_index = True)
    
    # clean data - if verbose is true, summary of removed items is printed
    data, removed_rows_summary = clean_data(data, subject = subject, criteria = criteria,
                                            remove_non_numeric_values = remove_non_numeric_values,
                                            verbose = verbose)
    
    return data, removed_rows_summary



"""
Code below is used for collating information about EC pupils from the spreadsheets 
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
        display(sampled_df)
        keys = df_to_append[lookup_col_heading].loc[random_indices]
        #print("Keys are: {0}".format(keys))
        df_mask = df_source.where(df_source[keys_col_heading].isin(keys))
        print("Matching rows from source dataframe")
        df_to_display = df_mask[[keys_col_heading, values_col_heading]].dropna().sort_values(by = keys_col_heading)
        display(df_to_display)
    
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
