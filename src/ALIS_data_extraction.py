# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 13:59:00 2022
Reading in ALIS datafiles.  
Looks like only 2020 and 2021 have actual ALIS scores (and most pupils have average GCSE scores as well)
2017, 2018, 2019 only have average GCSE scores
@author: owen
"""
import data_extraction as de

import numpy as np
import pandas as pd
import name_disambiguation as name_dis

ALIS_DATA_DIR = "{0}/Original data files/ALIS data/Value added subject analysis".format(de.SOURCE_DATA_DIR) 
ALL_ALIS_FILES = ['2017.xls', '2018.xls', '2019.xls', '2020.xls', '2021.xls']

def read_in_ALIS_file(ALIS_data_dir, filename, verbose = False):
    #relevant_columns = ["Syllabus Title",	"Exam Board", "Syllabus Code", "GCSE"]
    
    # select relevant columns from original data file and read in
    relevant_columns = list(range(1, 12)) + [18] + [25]    
    
    data = pd.read_excel("{0}/{1}".format(ALIS_data_dir, filename), header = 5,
                       index_col = None, skiprows = [0-4, 6, 7], usecols = relevant_columns)
    
    if verbose:
        print("Loading data from file {0}/nThe summary of entries for this dataframe is as follows:/n".format(filename))
        print(data.count())
        
    # rename unhelpful column names
    data.rename({'Grade.1' : 'A level Points', 
                 'Grade' : 'A level Grade', 
                 'GCSE' : 'Average GCSE Points'
                 },
                axis = 1, inplace = True)
    
    # make surnames and forenames lower case
    data[['Surname', 'Forename', 'Initial']] = data.apply(name_dis.split_name_wrapper, axis = 1)
   # data['Forename'] = data['Forename'].map(lambda x: x.lower())
    
    # check for missing data entries in ALIS tests and GCSE average scores
    test_nans = data[data['Adaptive Test (Computer Based)'].isna()]#.loc[:, ['Surname', 'Adaptive Test (Computer Based)', 'A level Grade', 'Average GCSE Points']]
    gcse_nans = data[data['Average GCSE Points'].isna()]#.loc[:, ['Surname', 'Adaptive Test (Computer Based)', 'A level Grade', 'Average GCSE Points']]
    if verbose:
        print('There are {1} NaN entries for GCSE points and {0} NaN entries for ALIS score'
          .format(len(test_nans.index), len(gcse_nans.index)))
        
    print("The data has length {0} including all NaN rows".format(len(data.index)))
    dropped_data = data.drop(index = set(test_nans.index).union(set(gcse_nans.index)))
    
    if verbose:
        print("If all of the NaN entries were removed from the original {0} this would leave {1} rows".
              format(len(data.index), len(dropped_data.index)))
    
    return data, {"Missing ALIS tests" : len(test_nans.index), 
                  "Missing GCSE results" : len(gcse_nans.index), 
                  "Complete data" : len(dropped_data.index),
                  }


def read_all_ALIS_data(ALIS_data_dir = ALIS_DATA_DIR, 
                          filenames = ALL_ALIS_FILES, verbose = False,
                          store_concatenated_data = False, 
                          store_individual_years = False,
                          store_missing_data_summary = False):
    
    results = {}
    new_data = {}
    for filename in filenames:
        new_data[filename], results[filename] = read_in_ALIS_file(ALIS_data_dir, filename, verbose = verbose)
        new_data[filename]['Original file'] = filename
        if store_individual_years:
            new_data[filename].to_csv("{0}/{1}".format(ALIS_data_dir, filename.replace("xls", 'csv')))
    
    all_data = pd.concat(new_data.values())
    print("Now concatenated giving total of {0} entries".format(len(all_data.index)))
    if store_concatenated_data:
        all_data.to_csv("{0}/all_years.csv".format(ALIS_data_dir))
        
    
    results = pd.DataFrame.from_dict(results)
    if store_missing_data_summary:
        results.to_csv("{0}/Missing data analysis summary.csv".format(ALIS_data_dir))
    
    return all_data
        

if __name__ == '__main__':
    # change boolean variables to overwrite stored results or display more detail
    all_data = read_all_ALIS_data(store_concatenated_data = False,
                                  store_individual_years = False,
                                  store_missing_data_summary = False,
                                  verbose = True)


