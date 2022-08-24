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

ALL_ALIS_FILE = "{0}/all_years.csv".format(ALIS_ext.ALIS_DATA_DIR)

# link from GCSE and MidYIS filenames to matching (hopefully) ALIS data filenames
YEAR_MATCH = {'Yr 9 2012_13' : '2017.csv',
              'Yr 9 2013_14' : '2018.csv',
              'Yr 9 2014_15' : '2019.csv',
              'Yr 9 2015_16' : '2020.csv',
              'Yr 9 2016_17' : '2021.csv'}

midYIS_data_years = de.ALL_YEARS

def merge_results_wrapper(year, MidYIS_file = de.MidYIS_GCSE_DATA_FILE):
    
    dfs = {}
    dfs["MidYIS data for " + year] = de.get_columns_and_flatten(year)
    dfs["ALIS data for " + YEAR_MATCH[year]] = pd.read_csv("{0}/{1}".format(ALIS_ext.ALIS_DATA_DIR, YEAR_MATCH[year]))
    
    print(dfs["MidYIS data for " + year]['Surname'].sort_values())
    print(dfs["ALIS data for " + YEAR_MATCH[year]]['Surname'].sort_values())
    #print(dfs["ALIS data"].head())
    
    de.merge_wrapper(dfs, on = 'Surname', test_run = True)


#merge_results_wrapper('Yr 9 2014_15')

df = pd.read_csv("{0}/{1}".format(ALIS_ext.ALIS_DATA_DIR, '2017.csv'))
df_A_ref = df[df['Exam Type'] == "A-Level (A2)"]
#drop AS results
df_A = df[df['Exam Type'] == "A-Level (A2)"].copy()

# pivot to create subject title columns with grades as values
new_df = df_A.pivot(index = ['Surname', 'Forename'], columns = 'Subject Title ', values = 'A level Grade')
new_df.reset_index(inplace = True)
verbose = False




# drop columns that are now irrelevant from df_A
df_A.drop(columns = ["Subject Title ", 'A level Grade','Exam Type',  'A level Points',
                     'Syllabus Title', 'Exam Board', 'Syllabus Code'], inplace = True)

# join back to original dataframe with duplicates removed
new_df = new_df.join(other = df_A.drop_duplicates(subset = ['Surname', 'Forename']).set_index(['Surname', 'Forename']), 
                                        on = ['Surname', 'Forename'], how = 'left')

# test to confirm that grades are correctly allocated
for row_index in df_A_ref.index:
    surname = df_A_ref.loc[row_index,['Surname']]['Surname']
    forename = df_A_ref.loc[row_index,['Forename']]['Forename']
    subject_title = df_A_ref.loc[row_index, ['Subject Title ']]['Subject Title ']
    grade = df_A_ref.loc[row_index, ['A level Grade']]['A level Grade']
    
    matching = new_df[new_df['Surname'] == surname]
    matching[matching.Forename == forename]
    matching = matching[subject_title]
    assert(len(matching.index) == 1)
    assert(matching.iloc[0] == grade)
    #print(matching)
    if verbose:
        print("Confirming pivot operation for {0} {1} {2}".format(forename, surname, subject_title))
        print("Grade stored in pivoted dataframe : {0}".format(matching.iloc[0]))
        print("Grade stored in original dataframe : {0}".format(grade))

new_df.to_csv("{0}/test_join.csv".format(de.TEMP_DIR))

