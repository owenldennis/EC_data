# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:10:20 2022

Cross reference names in dataframes to check for matches and highlight ambiguous situations

@author: owen
"""


def check_consistency(row1, row2):
    """
    Only returns consistent if both surname and first name are identical
    """
    if not row1.Surname.lower() == row2.Surname.lower():
        return False
    if not row1.Forename.lower() == row2.Forename.lower():
        return False
    try:
        if not row1.dob == row2.dob:
            return False        
    except KeyError:
        pass