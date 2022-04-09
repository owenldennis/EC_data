# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:10:20 2022

Cross reference names in dataframes to check for matches and highlight ambiguous situations

@author: owen
"""

import numpy as np
import re

def check_dob(name_to_identify, df_surname_match):
    pass



def split_name(name_string, surname_first = False):
    # split name string on emtpy space, assume last token is surname
    # If more than one token, assume this is either the forename or an initial if length 1
    initial = None
    forename = None
    middle_names = []
    
    name_string = re.sub(',', ' ', name_string)
    name_string = re.sub(':', ' ', name_string)
    #print(name_string)
    name_string = re.sub('/.', ' ', name_string)
    #print(name_string)
    names = name_string.lower().split()
    #print(names)
     
    if not len(names):
        return {'Surname' : None, 'Forename' : None,
                'Initial' : None, 'Middle names' : []}
    
    if surname_first:
        surname = names[0]
        # put surname at the end of the array
        names = [names[i] for i in range(1,len(names))]
        names.append(surname)

    surname = names[-1]
        
    if len(names) > 1:
        if len(names[0]) > 1:
            forename = names[0]
        else:
            initial = names[0]
        
        if len(names) > 2:
            middle_names = names[1:-1]
    return {'Surname' : surname, 'Forename' : forename,
            'Initial' : initial, 'Middle names' : middle_names}


def Lev_distance(string1, string2, strip = True, lower = True):
    if strip:
        string1 = string1.strip()
        string1 = string1.rstrip()
        string2 = string2.strip()
        string2 = string2.rstrip()
    if lower:
        string1 = string1.lower()
        string2 = string2.lower()
        
    # array to store lev distances
    Lev_array = np.array([np.zeros(len(string2) + 1) for i in range(len(string1) + 1)])
    Lev_array[0] = [i for i in range(len(string2) + 1)]
    
    for i in range(len(string1)):
        Lev_array[i+1][0] = i + 1
        for j in range(len(string2)):
            
            if string1[i] == string2[j]:
                cost = 0
            else:
                cost = 1
            
            Lev_array[i+1][j+1] = min(Lev_array[i,j] + cost, Lev_array[i+1,j] + 1, Lev_array[i,j+1] + 1)
    
    return Lev_array[i,j]
            
              
    
def find_best_match(name_to_identify, df_of_names):
    """
    Requires at least surname key in dictionary
    If DOB is provided, must be the same format and type as that in df_of_names
    Requires surname and forename columns in df_of_names
    """

    # find all Levenstein distances
   
    df_of_names['Lev surname dist'] = df_of_names['Surname'].map(lambda x : Lev_distance(x, name_to_identify['Surname']))
    
    if (name_to_identify.get('Forename') and 'Forename'.isin(df_of_names.columns)):
        df_of_names['Lev forename dist'] = df_of_names['Forename'].map(lambda x : Lev_distance(x, name_to_identify['Forename']))
    
    
    
def match_two_groups_of_names(df1, df2_to_cross_ref):
    pass
    
        
    
    
        
    
    
         
    
    