# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 18:33:42 2022
obsolete functions

@author: owen
"""
import pandas as pd

def test_with_mini_df():
    mini_df = results_dataframe[['Pupil Id', 'Programme Id']].head(10)   
    display(mini_df)
    print(mini_df.columns)
    remove_whitespace_in_col_headings(mini_df)
    remove_whitespace_in_col_headings(programmes_subjects_df)    
    print(mini_df.columns)
    mini_df['Programme Name'] = mini_df['Programme_Id'].map(lambda x : get_prog_name(x))
    display(mini_df)

def get_prog_name(prog_id):
    for row in programmes_subjects_df.itertuples():
        if row.Programme_Id == prog_id:
            return row.Name
    return np.nan

def new_col_from_crossref(col_to_cross_ref, df_to_read, keys_col_heading, vals_col_heading):
    crossref_dict = make_crossref_dict(df_to_read, keys_col_heading, vals_col_heading)
    return [crossref_dict[col_entry] for col_entry in col_to_cross_ref]

def is_number(entry):
    if type(entry) == 'int':
        return True
    if type(entry) == 'float':
        return True
    
    return False

def find_numeric_entries(series):
    return [is_number(s) for s in series]
    
df = pd.DataFrame(
    [
        [24.3, 75.7, "high"],
        [31, 87.8, "high"],
        [22, 71.6, "medium"],
        [35, 95, "medium"],
    ],
    columns=["temp_celsius", "temp_fahrenheit", "windspeed"])

display(df)

# create cross-ref dictionaries
#codes_to_subjects = make_crossref_dict(programmes_subjects_df, 'Programme_Id', 'Name') 
#ids_to_initials = make_crossref_dict(pupil_info_df, 'Id', 'Name_Initials')
#print(results_dataframe.columns)
#print(pupil_info_df.columns)
#print(results_dataframe[['Programme_Id', 'First_Grade']].head(10))

# add new columns to dataframe using cross-references
#results_dataframe['Programme_name'] = results_dataframe['Programme_Id'].map(lambda x : codes_to_subjects[x])
#results_dataframe['Initials'] = results_dataframe['Pupil_Id'].map(lambda x : ids_to_initials[x])
#display(results_dataframe[['Pupil_Id', 'Programme_Id', 'Programme_name', 'First_Grade']].head(20))