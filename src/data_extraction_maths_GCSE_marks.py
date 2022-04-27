# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 08:37:48 2022

Functions for reading in excel files (converted from pdfs via word!)
These files contain the marks for GCSE papers from 2016 to 2019, one file per year

The functions below tidy up the resultant dataframes and carry out various checks 
to ensure the data is accurately transcribed

The dataframes are then merged with the corresponding year from the maths department data extraction

@author: owen
"""

import data_extraction as de
import name_disambiguation as name_dis
import data_extraction_maths_dept as demaths
import pandas as pd


MATHS_TIME_SERIES_PATH = "{0}/Maths_scores_time_series".format(de.RESULTS_DIR)
GCSE_MARKS_PATH = "{0}/Extracted data files/GCSE_marks_csvs_from_pdfs".format(de.SOURCE_DATA_DIR)
GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT = {'GCSE_scores_2016.csv' : 'Yr 9 2013_14.csv',
                                                  'GCSE_scores_2017.csv' : 'Yr 9 2014_15.csv',
                                                  'GCSE_scores_2018.csv' : 'Yr 9 2015_16.csv',
                                                  'GCSE_scores_2019.csv' : 'Yr 9 2016_17.csv'
                                                  }

#GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT.values()

#YEARS = [year for year in de.ALL_YEARS if year in ]

CSV_FILES_WITH_TOTAL_MARKS = ['GCSE_scores_2018.csv', 'GCSE_scores_2019.csv']
    
FOUNDATION_PUPILS = [('lucy', 'george'), ('thomas', 'warwick-smith')]


### Given a dataframe and an index, iterates through the rows from that point
### Data matching all initialised fields must be located before the iteration ends
### Keeps track of the number of rows iterated to avoid errors
def find_next_data(df, i):
    name_found = False
    av_scores_found = False
    paper3_score_found = False
    paper4_score_found = False
    grade_found = False
    loops = 0
    
    av, p3, p4, name, grade, ind = None, None, None, None, None, None
    
    while not (name_found and av_scores_found and paper3_score_found and paper4_score_found and grade_found) and  i < len(df.index):
        if isinstance(df.loc[i, 'Average Score'], int):
            av = df.loc[i, 'Average Score']
            av_scores_found = True
        if isinstance(df.loc[i, 'Paper 3H'], str) and '100' in df.loc[i, 'Paper 3H']:
            p3 = df.loc[i, 'Paper 3H'][:3].strip("/")
            paper3_score_found = True
        if isinstance(df.loc[i, 'Paper 4H'], str) and '100' in df.loc[i, 'Paper 4H']:
            p4 = df.loc[i, 'Paper 4H'][:3].strip("/")
            paper4_score_found = True
        if isinstance(df.loc[i, 'Name'], str):
            name = df.loc[i, 'Name']
            ind = df.loc[i, 'Original index']
            name_found = True
        if isinstance(df.loc[i, 'Grade'], str):
            grade = df.loc[i, 'Grade']
            grade_found = True
        i += 1
        loops += 1
    
    return ind, name, av, p3, p4, grade, i, loops


### Locates data that should be in the same row
### If too many rows are iterated a warning and information is printed
### All rows with complete data are stored in a new dataframe and returned
def extract_relevant_maths_scores(df, max_loops = 3):
    """
    * This function is only used for the excel GCSE marks files (from pdf converted to word, then copied into excel)
    * Due to data protection issues this is not used at the moment.
    *
    """
    
    #Ensure index is integers in order, store original index within dataframe
    df['Original index'] = df.index
    df.index = list(range(len(df.index))) 

    i = 0
    data = {}
    while i < len(df.index):
        ind, name, av, p3, p4, grade, i, loops = find_next_data(df, i)
        
        if not name or not p3 or not p4 or not grade or not av:
            print("Missing data on this loop")
            print("The data extracted is: {0}, {1}, {2}, {3}".format(name, av, p3, p4))
            print("The nearby rows of the dataframe are \n{0}".format(df.loc[i-3: i]))
        
        else:
            data[ind] = {'Name' : name,
                         'Average mark' : av,
                         'Grade' : grade,
                         'Paper 3H' : p3, 
                         'Paper 4H' : p4
                         }
            
            if not loops <= max_loops:
                print("Looped {0} times to extract that data".format(loops))
                print("The data extracted is: {0}, {1}, {2}, {3}".format(name, av, p3, p4))
                print("The nearby rows of the dataframe are \n{0}".format(df.loc[i-3: i]))
            
            if not abs((float(p3)+float(p4))/2 - float(av)) < 1:
                print("Averaging marks problem around row {0}".format(i))
                print("The data extracted is: {0}, {1}, {2}, {3}".format(name, av, p3, p4))
                print("The nearby rows of the dataframe are \n{0}".format(df.loc[i-3: i]))
    
    
    return pd.DataFrame.from_dict(data, orient = 'index')


def name_dis_wrapper(name_string, key, surname_first = True):
    name_dict = name_dis.split_name(name_string, surname_first = surname_first)
    return name_dict[key]


### Uses the functions above to create a new dataframe with one row for each name
### Name is split into Surname, Forename and Middle names with a separate column for each                 
def format_maths_GCSE_marks_into_dataframes(csv_filename, excel_filename = "", path = GCSE_MARKS_PATH):
    
    if len(excel_filename):       
        # extract the data from the excel file containing raw GCSE maths marks data
        # this is not currently the chosen route due to data protection issues with pdf file conversion online
        marks_df = pd.read_excel("{0}/{1}".format(path, excel_filename), header = None)                          
        
        # create tidy dataframe with one row per pupil and rename columns
        marks_df.columns = ['Name', 'Average score', 'Grade', 'Paper 3H', 'Paper 4H']
        tidied_marks_df = extract_relevant_maths_scores(marks_df, max_loops = 3) 
        
    else:
        # csv files are being used - these have already been partially tidied
        # however, marks in 2018 and 2019 are given as a total of two papers not the average - these must be adjusted
        # Also, marks are stored as strings - these are changed to integers
        tidied_marks_df = pd.read_csv("{0}/{1}".format(path, csv_filename), index_col = 0)
        if csv_filename in CSV_FILES_WITH_TOTAL_MARKS:
            tidied_marks_df['Average GCSE score'] = tidied_marks_df['Mark'].map(lambda x: int(round(x/2)))
        else:
            tidied_marks_df['Average GCSE score'] = tidied_marks_df['Mark'].map(lambda x: int(x))
            
    # split name into forename, surname and middle names    
    for key in ['Surname', 'Forename']:
        tidied_marks_df[key] = tidied_marks_df['Name'].apply(lambda x: name_dis_wrapper(x, key))
        
    return tidied_marks_df[['Surname', 'Forename', 'Average GCSE score']]
    
    


def merge_two_dataframes(df1, df2, how = 'inner', merging_on_cols = ['Surname, Forename'],
                         test_run = False, verbose = False):
    """
    Parameters
    ----------
    df1 : TYPE dataframe
        DESCRIPTION.
    df2 : TYPE dataframe containing data to merge into df1
        DESCRIPTION.
    how : TYPE string, optional
        DESCRIPTION. The default is 'inner'.
    test_run : TYPE, optional
        DESCRIPTION. The default is False.
    verbose : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    merged_df : TYPE merged dataframe
        DESCRIPTION.

    """
    if test_run:
        indicator = 'Indicator'
        how = 'left'
    else:
        indicator = False
        how = how
    
    #df1['index'] = df1.index
    merged_df = pd.merge(df1, df2, how = how, 
                          left_on = ['Surname', 'Forename'], right_on = ['Surname', 'Forename'], 
                          indicator = indicator, validate = "1:1")
    #merged_df.index = merged_df['index']
    #merged_df.drop('index', inplace = True, axis = 1)
    
    if verbose:
        print("After merging, the first 10 rows of the dataframe are {0}".format(merged_df.head(10)))
                             
    if test_run:
        print("The following names from the first dataframe could not be found in the second dataframe\n {0}\n\n"
                  .format(merged_df.loc[merged_df[indicator] == 'left_only']['Surname']))
        print("The following names in the second dataframe could not be found in the first dataframe\n {0}"
                  .format(merged_df.loc[merged_df[indicator] == 'right_only']['Surname']))
                                
    else:
        #orig#inal_length = len(df.index)
        #total_dodgy = dodgy_count
        if verbose:
            print("Original length of first dataframe was {0}".format(len(df1.index)))
            print("After merging there are {0} entries\n".format(len(merged_df.index)))
                     
    return merged_df


def merge_maths_dept_csv_with_GCSE_marks():
    """
    * Loads up csv files (converted from pdf using ptesseract etc) and merges with matching maths dept time series file
    * If 'TEST_RUN' is True, no data is lost and the numbers of entries that do not match up are displayed for each file
    """
    
    TEST_RUN = False
    
    for i, csv_marks_filename in enumerate(GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT.keys()):
        
        # tidy GCSE marks in readiness for merging
        GCSE_marks_df = format_maths_GCSE_marks_into_dataframes(csv_marks_filename)
        
        # read in time series data for the relevant year
        csv_year_filename = GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT[csv_marks_filename]
        time_series_df = pd.read_csv("{0}/{1}".format(MATHS_TIME_SERIES_PATH, csv_year_filename), index_col = 0)

        # merge on surname and forename (one to one basis, can do a test_run to see how much data will be lost)
        merged_df = merge_two_dataframes(time_series_df, GCSE_marks_df, test_run = TEST_RUN, verbose = True)
        
        # store in 'Extracted data files' directory
        if TEST_RUN:
            merged_df.to_csv("{0}/Extracted data files/test_merge{1}.csv".format(de.SOURCE_DATA_DIR, i+2016))
        else:
            merged_df.to_csv("{0}/Extracted data files/GCSE_marks_merged_with_maths_dept_marks/tests_and_{1}".
                             format(de.SOURCE_DATA_DIR, csv_marks_filename))


def concat_wrapper():
    # use demaths function to concatenate all GCSE maths dataframes into one csv
    # will be saved to 'Combined_years' subdirectory of path passed
    path = "{0}/GCSE_marks_merged_with_maths_dept_marks".format(de.EXTRACTED_DATA_DIR)
    # load maths test scores and GCSE marks and concatenate
    filenames = GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT.keys()
    filenames = ["tests_and_" + f for f in filenames]
    
    demaths.concat_all_csv_files(path, filenames, save = True)
    
    
    
def merge_all_maths_data():  
    """
    relevant CEM years maths data is extracted; all maths scores are loaded; these dataframes are merged
    results are stored in csv file in the main directory for the project (de.SOURCE_DATA_DIR)

    Returns
    -------
    None.

    """
    
    verbose = True
    
    # years paramater can be related to constants at the head of this file
    relevant_yeargroups = [r.replace(".csv", "") for r in GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT.values()]
    years = [year for year in de.ALL_YEARS if len([group for group in relevant_yeargroups if group in year])]
    
    
    # load all GCSE CEM maths grades and predictions for the relevant years 
    cem_data, removed_rows_summary = de.extract_GCSE_and_midYIS_data(years = years, subject = 'Mathematics', criteria = 'Actual GCSE Points',
                                            remove_non_numeric_values = True,
                                            verbose = verbose)
    
    # flatten multicolumns
    cem_data.columns = [d[1] for d in cem_data.columns]
    cem_data.rename({"Forename" : "Forenames", 
                     "Surname" : "Surname caps",
                     "Overall Score" : "MidYIS overall score"
                     }, axis = 1, inplace = True)

    # remove middle names from forename column and store as lower case for merging
    cem_data['Forename'] = cem_data['Forenames'].map(lambda x: x.split()[0].strip().rstrip().lower())
    
    # rewrite surname as lower case for merging
    cem_data['Surname'] = cem_data['Surname caps'].map(lambda x: x.strip().rstrip().lower())
    cem_data.drop(['Surname caps', 'Forenames'], axis = 1, inplace = True)
    
    # load csv file containing all maths dept marks for all years into dataframe
    maths_data = pd.read_csv("{0}/GCSE_marks_merged_with_maths_dept_marks/Combined_years/GCSE_years_2016_2017_2018_2019.csv".format(de.EXTRACTED_DATA_DIR),
                             index_col = 0)
    
    
    length_with_duplicates = len(maths_data.index)
    # remove pupils with matching forenames and surnames (benjamin walker)
    maths_data.drop_duplicates(['Surname', 'Forename'], keep = False, inplace = True)
    length_no_duplicates = len(maths_data.index)
    removed_names = int((length_with_duplicates - length_no_duplicates)/2)
    print("{0} name(s) have been completely removed from the maths data since both first and surname were duplicated".format(removed_names))
    
    # remove foundation pupils whose results may skew the data: Lucy George and Thomas Warwick-Smith
    for forename, surname in FOUNDATION_PUPILS:
        match = maths_data[maths_data['Surname'] == surname.lower()]
        match = match[match['Forename'] == forename.lower()]
        maths_data.drop(match.index, inplace = True)
    
    # remove 'abs as an indication of absent for a test
    
    
    merged_df = merge_two_dataframes(maths_data, cem_data, merging_on_cols = ['Surname', 'Forename'], test_run = False, verbose = True)
    
    merged_df.to_csv("{0}/all_maths_data_2016_to_2019.csv".format(de.SOURCE_DATA_DIR))
    
#merge_all_maths_data()        
        
        
