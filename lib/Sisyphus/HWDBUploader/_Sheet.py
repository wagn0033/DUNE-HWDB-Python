#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Sheet.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut
from Sisyphus.RestApiV1.keywords import *
from Sisyphus.HWDBUploader.keywords import *

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re


pp = lambda s: print(json.dumps(s, indent=4))

'''
sheet node format

{
    "Docket Name": "Docket 001",
    "Source Name": "Bongos and Biffs",
    "File Name": "Upload_SN.xlsx",
    "Sheet Name": "Bongo-Items",
    "Values": {
        "Type ID": "Z00100300023"
    },
    "Encoder": "Auto",
    "Sheet Type": "Item",
    "Part Type ID": None,
    "Part Type Name": None,
}

'''

class Sheet:
    #{{{
    '''Load a CSV or Excel sheet and provide an interface for Encoders to extract data'''
    
    #_file_cache = {}  ## maybe we don't need to cache. how much overhead is there in just
                       ## reloading the file each time it's encountered?

    def __init__(self, sheet_info):
        #{{{
        self.sheet_info = deepcopy(sheet_info)

        #print("Creating Sheet object")
        #print("==Sheet Info==")
        #pp(sheet_info)

        self.global_values = sheet_info.get("Values", {})
        self.local_values = None
        self.dataframe = None

        self._read_data()
       

        #print("==End Sheet Info==")
 
        #}}}

    def coalesce(self, column, row_index=None):
        '''
        Returns the value for the row and column, if it exists. If it doesn't exist, it returns
        the value in the headers for the sheet, or the global values passed to the sheet. If none
        of them exist, returns None.
        '''

        gv = self.global_values
        lv = self.local_values
        df = self.dataframe

        default = lv.get(column, gv.get(column, None))

        if row_index is None:
            return default

        if column in df:
            value = df[column][row_index]
            if pd.isna(value) and default is not None:
                return default
            else:
                return value
        else:
            return default
                    

    def _read_data(self): 
        #{{{
        
        filename = self.sheet_info["File Name"]
        filetype = self.sheet_info["File Type"]
        sheetname = self.sheet_info.get("Sheet Name", None)

        # Read only the first two columns of the sheet, which we will analyze
        # further to determine what the true layout of the sheet might be
        if filetype == DKT_EXCEL:
            try:    
                #excel_file = pd.ExcelFile(filename)
                locals_df = pd.read_excel(
                        filename, 
                        self.sheet_info["Sheet Name"],
                        header=None,
                        usecols=[0, 1],
                    )     
                self.sheet_info["File Type"] = "Excel"
            except ValueError as err:
                msg = f"Could not load sheet '{sheetname}' from '{filename}'"
                logger.error(msg)
                logger.info(err)
                raise ValueError(msg)
        elif filetype == DKT_CSV:
            try:
                locals_df = pd.read_csv(
                    filename,
                    header=None,
                    usecols=[0, 1],
                    skip_blank_lines=False,
                    #on_bad_lines=lambda x: x[:2],
                    #engine='python'
                )
                self.sheet_info["File Type"] = "CSV"
            except ValueError as err2:
                msg = f"Could not load '{filename}'"
                logger.error(msg)
                logger.info(f"err")
                raise ValueError(msg)
        else:
            msg = f"Unknown File Type '{filetype}'"
            logger.error(msg)
            logger.info(f"err")
            raise ValueError(msg)

        # Only looking at the first column, the rule we will use to determine 
        # the layout shall be to look for the LAST occurence of "External ID" 
        # or "Serial Number" that has an empty cell above it, or is the first
        # cell. Everything above the empty cell will be considered global
        # (key, value) pairs, and everything after will be a table of data.
        #
        # If the last occurence isn't preceded by a blank cell, and it's not
        # the first cell, then we can try to interpret this as a single-record
        # sheet, where the record is entirely defined by (key, value) pairs,
        # with no table below.
        #
        # Note that if you do a single-record sheet, the first cell can't be
        # "External ID" or "Serial Number", or it will try to interpret it
        # as the beginning of the main table.
        
        column_header_row = -1
        local_value_rows = 0
        for row_index in reversed(range(len(locals_df[0]))):
            if locals_df[0][row_index] in ["External ID", "Serial Number"]:
                if row_index == 0 or pd.isna(locals_df[0][row_index-1]):
                    column_header_row = row_index
                    break

        # Let's grab the sheet local values, if there are any.
        # If the column header row is 0 or 1, there are no local values
        # If it's -1, then the whole sheet is local values
        local_values = self.local_values = {}

        if column_header_row == -1:
            local_value_rows = len(locals_df[0])
        elif column_header_row in [0, 1]:
            local_value_rows = 0
        else:
            local_value_rows = column_header_row - 1            

        for row_index in range(local_value_rows):
            if not pd.isna(locals_df[0][row_index]):
                if not pd.isna(locals_df[1][row_index]):
                    local_values[locals_df[0][row_index]] = locals_df[1][row_index]
                else:
                    local_values[locals_df[0][row_index]] = ""

        #print("==Local Values==")
        #pp(self.sheet_info["Local Values"])

        # Let's grab the table of values now
        if column_header_row == -1:
            # If this is a single-record sheet, make a dummy table with one row.
            # When we try to get the values for this one row, it will "coalesce" to the
            # local values and (possibly) make it a valid record if enough data is there.
            df = pd.DataFrame({None: [None]})
        else:
            if filetype == DKT_EXCEL:
                df = pd.read_excel(
                        filename,
                        sheetname,
                        skiprows=column_header_row
                    )
            else:
                df = pd.read_csv(
                        filename,
                        skiprows=column_header_row
                    )

        self.dataframe = df

        #print("==DataFrame==")
        #print(df)

    

        #}}}


    #}}}





























