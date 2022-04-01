# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 13:38:23 2022

This file contains functions to read in, clean and merge excel spreadsheets containing test and end of year exam marks
The data is from the Eastbourne College maths department.

@author: owen
"""

import pandas as pd
import re
import name_disambiguation as name_dis
import data_extraction as de
import os
"""
Code for reading maths department spreadsheets.

Names are split into forename and surname and relevant marks are selected

Sheets are merged based on excatly matching forename and surnames

Missing grades 
- in merged files, there are different numbers of tests in some years to others so could remove these columns?
- correspondence between tests is not necessarily exact - different tests possilby, or tests not aligning due to issue above
- could be some 0 marks due to missing marks which are then added in excel formula etc.
- give average of nearby marks - nice as setted, though careful if fully merged (boundary issues eg set 7 next to set 1)
- Implement random forest which deals with empty cells? 
- impute using linear regression on nearby columns - like this one especially if only using start and end of each year tests.
"""


USABLE_YEARS = ['Yr 9 2013_14',  #***all subjects graded 1-8 on CEM scale***
                'Yr 9 2014_15', #***all except English graded 1-8)***
                'Yr 9 2015_16',
                'Yr 9 2016_17'
                ]

def name_formatting(name_string, return_key = 'Surname'):
    # use name_disambiguation function to split name string if suitable
    # return one of the names found depending on key passed
    if type(name_string) == str:
        name_dict = name_dis.split_name(name_string, surname_first = True)
        
        return name_dict[return_key]
    else:
        return None

def read_in_spreadsheet(year, sheets = ['Yr 9', 'Yr 10', 'Yr 11'], subject = 'maths'):
    year = re.sub(" ", "_", year)
    year += "_{0}".format(subject)
        
    internal_data_by_year = {sheet : pd.read_excel("{0}/Tests_and_mock_scores/{1}.xlsx".format(de.SOURCE_DATA_DIR, year),
                                 sheet_name = sheet, header = [0,1]) for sheet in sheets}
    
    return internal_data_by_year

def flatten_multi_cols(df):
    df.columns = [' '.join([str(c) for c in [m for m in multi_col if m]]) for multi_col in df.columns]
     
def make_rename_columns_dict(df, yeargroup, rename_all_tests = False):
    # multi-column dfs must be flattened - all headings must be unique once flattened

    # identify test headings
    percent_headings = [c for c in df.columns if isinstance(c, str) and '%' in c]   
    # setup renaming dictionary
    rename_dict = {}
    
    if rename_all_tests:
        # create dict for all tests to be renamed
        rename_dict = {t : 'Test {0} {1}'.format(i, yeargroup) for i, t in enumerate(percent_headings)}
    
    # make sure final test of the year is labelled as such
    rename_dict[percent_headings[-1]] = 'Final test {0}'.format(yeargroup)
    
    # add names columns to be renamed
    rename_dict['Name Surname'] = 'Surname'
    rename_dict['Name Forename'] = 'Forename'
    rename_dict['Name Middle names'] = 'Middle names'

    return rename_dict


def clean_dataframe(df, column, verbose = False):
    dodgy_indices = df[df[column] == '%'].index
    #print(dodgy_indices)
    #print("*"*10)
    if verbose:
        print("The following entries are dropped\n {0}".format(df.loc[dodgy_indices]))
    df.drop(dodgy_indices, axis = 'index', inplace = True)
    return len(dodgy_indices)
    
       
    
def select_columns(df, name_keys = ['Surname', 'Forename']):#, 'Middle names']):  
    # select the relevant columns containing names or test percentage scores
    
    # find multi-column headings that are % scores
    headings = [c for c in df.columns if isinstance(c[1], str) and '%' in c[1]]
    
    # split names into surname, forename and middle names columns and append relevant multi-column headings to headings
    # must use numerical indexing to locate name data (sub-level of multicolumn heading is not helpful here)
    for name_key in name_keys:
        df[('Name', name_key)] = df['Name'].iloc[ :, 0].map(
            lambda x: name_formatting(x, return_key = name_key))
        headings = [('Name', name_key)] + headings
     
    return df[headings]



def combine_across_dfs(dict_of_dfs, keys_to_combine = ['Yr 9', 'Yr 10', 'Yr 11'],
                       test_run = False, verbose = False):
    """
    * dict of dfs contains data to merge across dataframes given by keys_to_combine
    * each dataframe is analysed:
        - relevant columns are selected using select_columns function
        - multi-column headings are flattened
        - column headings are renamed (uses make_rename_columns_dict function) 
        - dataframe is cleaned using clean_dataframe function
    * if test_run is True the dataframes will be merged with how = 'left' and missing entries will be flagged
    * if test_run is False the dataframes will be merged with how = 'inner' 
    * and only the overall length at each stage will be output (if verbose is True)
    * 
    """
    dfs = []
    dodgy_count = 0
    if test_run:
        verbose = True
    
    
    for i, yeargroup in enumerate(keys_to_combine):
        df = select_columns(dict_of_dfs[yeargroup]).copy()
        flatten_multi_cols(df)

        df.rename(columns = make_rename_columns_dict(df, yeargroup = yeargroup, 
              rename_all_tests = True), inplace = True) 
        
        dodgy_count += clean_dataframe(df, column = 'Final test {0}'.format(yeargroup), verbose = verbose)
        dodgy_count += clean_dataframe(df, column = 'Test 0 {0}'.format(yeargroup), verbose = verbose)
        
        dfs.append(df)
        
        if test_run:
            indicator = '{0}_indicator'.format(yeargroup)
            how = 'left'
        else:
            indicator = False
            how = 'inner'
            
        if i > 0 :
            dfs[0] = pd.merge(dfs[0], dfs[-1], how = how, 
                              left_on = ['Surname', 'Forename'], right_on = ['Surname', 'Forename'], 
                              indicator = indicator, validate = "1:1")
            if verbose:
                print("Merged dataframe after combining with {1} has {0} entries\n".format(len(dfs[0].index), yeargroup))
            
            if test_run:
                print("The following rows of the stored dataframe could not be matched in the {0} dataframe\n {1}\n\n"
                     .format(yeargroup, dfs[0].loc[dfs[0][indicator] == 'left_only']['Surname']))
                print("The following rows for {0} could not be matched in the stored dataframe\n {1}"
                      .format(yeargroup, dfs[0].loc[dfs[0][indicator] == 'right_only']['Surname']))
               
        else:
            original_length = len(df.index)
            total_dodgy = dodgy_count
            if verbose:
                print("There are {1} entries for {0}\n".format(yeargroup, len(df.index)))
    
    return dfs[0], original_length - len(dfs[0].index), total_dodgy


def merge_sheets_for_each_excel_file(excel_titles = USABLE_YEARS, sheet_names = ['Yr 9', 'Yr 10', 'Yr 11'], 
                                     save_each_merged_file = True, test_run = False, verbose = False):
    
    """
    * Iterates through each excel title passed (note these must be in the correct format)
    * Format required is that in USABLE_YEARS and matches the filenames in 'Tests and mock scores' directory
    * NOTE: some dodgy things here, title is formatted to add underscores in function read_in_spreadsheet above
    * 
    * Sheets are merged by cross-referencing against the surname and forename on a 1-1 basis
    * To view removed entries, run with test_run = True (though the summary data will be misleading)
    * To join using 'inner', run with test_run = False (this will also output accurate summary data)
    *
    """

    
    summary_dict = {}
    
    ### iterate through each excel file and merge all related data by names
    ### these are stored in the results dir if store = True
    ### summary of dropped data is printed at the end
    for excel_title in excel_titles:
        summary_dict[excel_title] = {}
        data = read_in_spreadsheet(excel_title, sheets = sheet_names)
        combined_df, lost_good_data_count, removed_total = combine_across_dfs(dict_of_dfs = data, keys_to_combine = sheet_names,
                                                            test_run = test_run, verbose = verbose)
        
        summary_dict[excel_title]['Rows lost when merging'] = lost_good_data_count
        summary_dict[excel_title]['Rows removed in cleaning'] = removed_total
        
        if verbose:
            print("There were {0} entries that could not be merged".format(lost_good_data_count))
            print("There were {0} entries removed from the original dataframe".format(removed_total))
        if save_each_merged_file:
            combined_df.to_csv("{0}/Maths_scores_time_series/{1}.csv"
                               .format(de.RESULTS_DIR, excel_title))
        
    if verbose:
        print(pd.DataFrame.from_dict(summary_dict, orient = 'index'))    


def concat_all_csv_files(path, join = 'outer', save = False):
    
    """
    * Tries to convert every file in the given path to a dataframe (must be csv files or directories or an exception will be thrown)
    * Files are concatenated and stored in subdirectory 'Combined_years' of the original directory
    * The concatenated dataframe is returned
    *
    """

    dfs = []
    files = ""
    for file in os.listdir(path):
        try:
            dfs.append(pd.read_csv("{0}/{1}".format(path, file), index_col = 0))
            dfs[-1]['Source file'] = file
            files = files + '_' + file[5:12]
        except PermissionError:
            print("No permission to access {0} in directory {1}".format(file, path))
        
    df = pd.concat(dfs, join = join, ignore_index = True)
    
    if save:
        df.to_csv("{0}/Combined_years/years{1}.csv".format(path, files[1:]))
    
    return df




if __name__ == '__main__':
    ### merge sheets from the excel files passed (via 'excel_titles, slightly dodgy!, see note on function)
    ### sheets are merged based on matching surname and forename
    ### files are saved into the results directory, subdirectory Maths_scores_time_series
    merge_sheets_for_each_excel_file(excel_titles = USABLE_YEARS, sheet_names = ['Yr 9', 'Yr 10', 'Yr 11'], 
                                         save_each_merged_file = True, test_run = False, verbose = True)
         
    
    
    ### concatenate the csv files in the directory passed and save in the subdirectory Combined_years
    df = concat_all_csv_files(path = "{0}/Maths_scores_time_series".format(de.RESULTS_DIR),
                              join = 'outer', save = True)    

    
    