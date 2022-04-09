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
#import data_extraction_maths_dept as demaths
import pandas as pd

MATHS_TIME_SERIES_PATH = "{0}/Maths_scores_time_series".format(de.RESULTS_DIR)
GCSE_MARKS_PATH = "{0}/Maths_GCSE_marks".format(de.RESULTS_DIR)
GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT = {'GCSE_scores_2016.xlsx' : 'Yr 9 2013_14.csv',
                         }
"""
Code for reading pdf files with exam marks 
"""

def read_pdfs(filepath):
    #C:\Users\owen\OneDrive - Eastbourne College\School analytics project\Original data files\GCSE maths marks
    #data = tabula.read_pdf(filepath, pages = 'all')
    #return data
    #print(df[0].head())
    pass
    



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


def name_dis_wrapper(name_string, surname_first = True):
    name_dict = name_dis.split_name(name_string, surname_first = surname_first)
    return name_dict['Surname'], name_dict['Forename'], name_dict['Middle names']

### Uses the functions above to create a new dataframe with one row for each name
### Name is split into Surname, Forename and Middle names with a separate column for each                 
def format_maths_GCSE_marks_into_dataframes(files_dict):
    #path = "{0}/Original data files/GCSE maths marks".format(de.SOURCE_DATA_DIR)
    #filename = "GCSE_scores_2016.pdf"
    #word_filename = filename.replace("pdf", "docx")
    #excel_filename = filename.replace("pdf", "xlsx")
    
    for excel_filename in files_dict.keys(): 
        
        # extract the data from the excel file containing raw GCSE maths marks data
        marks_df = pd.read_excel("{0}/{1}".format(GCSE_MARKS_PATH, excel_filename), header = None)                          
        
        # create tidy dataframe with one row per pupil and rename columns
        marks_df.columns = ['Name', 'Average Score', 'Grade', 'Paper 3H', 'Paper 4H']
        tidied_marks_df = extract_relevant_maths_scores(marks_df, max_loops = 3) 
        

        # split name into forename, surname and middle names
        print(tidied_marks_df.head())
       
        tidied_marks_df[['Surname', 'Forename', 'Middle names']] = tidied_marks_df['Name'].apply(lambda x: name_dis_wrapper(x))
        
        print(tidied_marks_df.head())
        time_series_df = pd.read_csv("{0}/{1}".format(MATHS_TIME_SERIES_PATH, files_dict[excel_filename]))
        return tidied_marks_df
        

if __name__ == '__main__':
    # drop last few rows                        
    #print(data.iloc[-10:, :8])
    #last_rows = range(len(data.index) - 1, len(data.index) - 6, -1)
    #data.drop(last_rows[:], axis = 0, inplace = True)   
    #print(data.iloc[-10:, :8])
    data = format_maths_GCSE_marks_into_dataframes(GCSE_MARKS_TO_MATHS_TIME_SERIES_FILENAMES_DICT)
    pass

