#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Sheet.py
Copyright (c) 2024 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Provides a consistent interface for reading data from Excel or CSV sheets.

The sheet may have some "default" column values specified by:
  (1) passing in a "Values" node in the sheet info on construction, or
  (2) reserving the top several rows of the sheet for key/value pairs,
      followed by a blank line, followed by the actual row data.
A sheet that only has the header data and is not followed by row data
is considered to have exactly one "row" that consists of whatever keys 
that are supplied in the header and/or "Values" node.

"""

from Sisyphus import version
from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut
from Sisyphus.RestApiV1.keywords import *
from Sisyphus.HWDBUploader.keywords import *

from Sisyphus.HWDBUploader import TypeCheck as tc
from Sisyphus.HWDBUploader.TypeCheck import Cell, CellLocation

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re

from dataclasses import dataclass, field
from collections import namedtuple

pp = lambda s: print(json.dumps(s, indent=4))

'''
sheet node format

{
    ##"Docket Name": "Docket 001",
    "Docket": "docket.json",
    ##"Source Name": "Bongos and Biffs",
    "Source": "Bongos and Biffs",
    ##"File Name": "Upload_SN.xlsx",
    "File": "Upload_SN.xlsx",
    ##"Sheet Name": "Bongo-Items",
    "Sheet": "Bongo-Items",
    "Values": {
        "Part Type ID": "Z00100300023"
    },
    "Encoder": "Auto",
    "Record Type": "Item",
    ##"Part Type ID": None,
    ##"Part Type Name": None,
}
'''

CellLocation = namedtuple("CellLocation", ["column", "row"])

@dataclass
class Cell:
    """Class for holding a cell's contents, plus tracking information"""
    source: str
    location: CellLocation = None
    warnings: list = field(default_factory=list)
    datatype: str = None
    value: 'typing.Any' = None




class Sheet:
    #{{{
    '''Load a CSV or Excel sheet and provide an interface for Encoders to extract data'''

    def __init__(self, sheet_info):
        #{{{
        self.sheet_info = deepcopy(sheet_info)

        self.global_values = sheet_info.get("Values", {})
        self.global_values["HWDB Utility Version"] = version
        self.local_values = None
        self.dataframe = None
        self.rows = None

        sheet_source_info = []
        if "Docket" in sheet_info:
            sheet_source_info.append(f"Docket '{sheet_info['Docket']}'")
        if "Source" in sheet_info:
            sheet_source_info.append(f"Source '{sheet_info['Source']}'")
        if "Source" in sheet_info:
            sheet_source_info.append(f"File '{sheet_info['File']}'")
        if "Sheet" in sheet_info:
            sheet_source_info.append(f"Sheet '{sheet_info['Sheet']}'")
        self.sheet_source = ", ".join(sheet_source_info)
        
        self._read_data()
        #}}}

    def create_cell(self, location, value, datatype):
        return Cell(
                source=self.sheet_source, 
                location=location, 
                warnings=[],
                datatype=datatype,
                value=value)
    
    def coalesce(self, column, row_index, datatype):
        #{{{
        '''
        Returns the value of a cell, or a set default value.

        Returns the value for the row and column, if it exists. If it doesn't exist, it returns
        the value in the headers for the sheet, or the global values passed to the sheet. If none
        of them exist, returns None.
        '''
    
        def inner_coalesce(self, column, row_index, datatype):
            if row_index is not None and (row_index >= self.rows or row_index < 0):
                msg = f"{self.sheet_source}: row index {row_index} out of range"
                logger.error(msg)
                raise IndexError(msg)

            if row_index is not None and column in self.dataframe:
                return self.create_cell(
                        CellLocation(column, self.row_offset+row_index),
                        self.dataframe[column][row_index],
                        datatype)
                        #self.dictionary[row_index][column])

            if column in self.local_values:
                return self.create_cell(
                        "header",
                        self.local_values[column],
                        datatype)

            if column in self.global_values:
                return self.create_cell(
                        "inherited",
                        self.global_values[column],
                        datatype)

            return self.create_cell("not found", None, "any")

        return tc.cast(inner_coalesce(self, column, row_index, datatype))
        #}}}        

    def _read_data(self): 
        #{{{
        
        filename = self.sheet_info["File"]
        filetype = self.sheet_info["File Type"]
        sheetname = self.sheet_info.get("Sheet Name", None)

        # make read_excel and read_csv look the same, so we don't
        # have to keep handling each case differently.
        if filetype == DKT_EXCEL:
            #print("SETTING EXCEL READ")
            def read_sheet(**kwargs):
                #print("READING EXCEL")
                try:
                    return pd.read_excel(
                                filename,
                                self.sheet_info["Sheet"],
                                keep_default_na=False,
                                **kwargs)
                except ValueError as err:
                    msg = f"Could not load sheet '{sheetname}' from '{filename}'"
                    logger.error(msg)
                    logger.info(err)
                    raise ValueError(msg)
        elif filetype == DKT_CSV:
            #print("SETTING CSV READ")
            def read_sheet(**kwargs):
                #print("READING CSV")
                try:
                    return pd.read_csv(
                                filename,
                                keep_default_na=False,
                                skip_blank_lines=False,
                                **kwargs)
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

        # Read only the first two columns of the sheet, which we will analyze
        # further to determine what the true layout of the sheet might be
        locals_df = read_sheet(header=None, usecols=lambda x: x is None or x<2)
        
        column_header_row = 0
        local_value_rows = 0
        local_values = {}
        if len(locals_df.columns) < 2:
            # note, it's possible for it to be just 1 if it's a 1-column table       
            # but then there are definitely no locals.
            column_header_row = 0
            local_values = {}

        else:
            # Our strategy to determine whether what we just read is the
            # header will be as follows:
            # Read down the first column until there's an empty cell (or the
            # end). If there's a non-empty cell after that, then this was
            # probably the header and more data will follow. Check that the
            # empty cell is actually an entirely empty row, because it could
            # just be an omitted value in that column.
            
            local_values = {}
            for row_index, series in locals_df.iterrows():
                #if locals_df[0][row_index] in local_values:
                #    msg = f"'{locals_df[0][row_index]}' declared multiple times"
                #    logger.error(msg)
                #    raise ValueError(msg)
                local_values[locals_df[0][row_index]] = locals_df[1][row_index]
                if series[0] == "":
                    blank_line_df = read_sheet(
                                header=None, 
                                skiprows=lambda x: x!=row_index)
                    row_values = list(blank_line_df.values[0])
                    nonblanks = len([x for x in row_values if x!=""])
                    if nonblanks > 0:
                        # Since we hit a row that started with an empty cell
                        # but wasn't entirely blank, we can conclude that
                        # this wasn't a header at all.
                        column_header_row = 0
                        local_values = {}
                    else:
                        column_header_row = row_index + 1
                        local_value_rows = row_index - 1
                    break
            else: # that weird "for-else" construction is sometimes useful
                # We got to the end without hitting the blank, so now we
                # have to see whether the existing data makes more sense as
                # a header or a table.

                # does it have more than two columns, if we ask for it?
                # if so, it's a table.
                locals_df = read_sheet(header=None)
                if len(locals_df.columns) > 2:
                    column_header_row = 0
                    local_values = {}

                # Since it has two columns, let's decide by whether the 
                # local keys has "Record Type".
                elif "Record Type" in local_values:
                    column_header_row = None
                    local_value_rows = row_index + 1
                else:
                    local_values = {}
 
        self.local_values = local_values

        if column_header_row is None:
            self.dataframe = pd.DataFrame({None: [None]})
            self.dictionary = self.dataframe.to_dict()
            self.rows = 1
            self.row_offset = None
        else:
            logger.debug(f"reading table from {self.sheet_source} starting at "
                    f"row {column_header_row}")
            self.dataframe = read_sheet(skiprows=column_header_row)
            self.dictionary = self.dataframe.to_dict()
            self.rows = len(self.dataframe.index)
            self.row_offset = column_header_row

        return


        #}}}


    #}}}





























