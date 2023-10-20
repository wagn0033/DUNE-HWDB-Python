#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Docket.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

"""

from Sisyphus.Configuration import config
logger = config.getLogger()


from Sisyphus.HWDBUploader.keywords import *

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut

import json
import sys
import numpy as np
import pandas as pd
from glob import glob
import os
from copy import deepcopy
import re

'''
# Dictionary keys for Docket files
DKT_DOCKET_NAME = "Docket Name"
DKT_VALUES = "Values"
DKT_SOURCES = "Sources"
DKT_SOURCE_NAME = "Source Name"
DKT_FILES = "Files"
DKT_FILE_NAME = "File Name"
DKT_SHEETS = "Sheets"
DKT_SHEET_NAME = "Sheet Name"
DKT_ENCODER = "Encoder"
DKT_AUTO = "Auto"
DKT_FILE_TYPE = "File Type"
DKT_EXCEL = "Excel"
DKT_CSV = "CSV"
DKT_FILE_HANDLE = "File Handle"
DKT_SHEET_TYPE = "Sheet Type"
DKT_ITEM = "Item"
DKT_TEST = "Test"
DKT_ITEM_IMAGES = "Item Image List"
DKT_TEST_IMAGES = "Test Image List"
DKT_UNKNOWN = "Unknown"
DKT_TYPE_ID = "Type ID"
DKT_TYPE_NAME = "Type Name"
DKT_EXTERNAL_ID = "External ID"
DKT_SERIAL_NUMBER = "Serial Number"
DKT_INST_ID = "Institution ID"
DKT_MANU_ID = "Manufacturer ID"
DKT_COUNTRY_CODE = "Country Code"
DKT_COMMENTS = "Comments"
DKT_ENABLED = "Enabled"

# Dictionary keys for REST API
RA_INSTITUTION = "institution"
RA_COUNTRY_CODE = "country_code"
RA_MANUFACTURER = "manufacturer"
RA_ENABLED = "enabled"
RA_COMMENTS = "comments"
RA_SPECIFICATIONS = "specifications"
RA_SUBCOMPONENTS = "subcomponents"
RA_PART_ID = "part_id"
RA_PART_TYPE_ID = "part_type_id"
RA_STATUS = "status"
RA_STATUS_OK = "OK"
RA_STATUS_ERROR = "ERROR"
RA_DATA = "data"
RA_SERIAL_NUMBER = "serial_number"
RA_COMPONENT_TYPE = "component_type"
RA_COUNTRY = "country"
RA_CODE = "code"
RA_ID = "id"
RA_FUNCTIONAL_POSITION = "functional_position"
'''

pp = lambda s: print(json.dumps(s, indent=4))

def get_hwitem_complete(part_id):
    logger.debug(f"getting part_id {part_id}")
    resp = ra.get_hwitem(part_id)
    if resp[RA_STATUS] != RA_STATUS_OK:
        raise RuntimeError("Error getting hwitem")
    data = resp[RA_DATA]

    resp = ra.get_subcomponents(part_id)
    if resp[RA_STATUS] != RA_STATUS_OK:
        raise RuntimeError("Error getting subcomponents")

    data[RA_SUBCOMPONENTS] = { item[RA_FUNCTIONAL_POSITION]: item[RA_PART_ID] for item in resp[RA_DATA] }

    return data



class _SN_Lookup:
    _cache = {}
    @classmethod
    def __call__(cls, part_type_id, serial_number):
        logger.debug(f"looking up {part_type_id}:{serial_number}")
        if (part_type_id, serial_number) not in cls._cache.keys():
            resp = ra.get_hwitems(part_type_id, serial_number=serial_number)
            if resp[RA_STATUS] != RA_STATUS_OK:
                msg = f"Error looking up serial number '{serial_number}' for " \
                            "part type '{part_type_id}'"
                logger.error(msg)
                raise ValueError(msg)
            if len(resp[RA_DATA]) == 1:
                part_id = resp[RA_DATA][0][RA_PART_ID]
                data = get_hwitem_complete(part_id)  
                cls._cache[part_type_id, serial_number] = part_id, data

            elif len(resp[RA_DATA]) == 0:
                cls._cache[part_type_id, serial_number] = None
            elif len(resp[RA_DATA]) > 1:
                msg = f"Serial number '{serial_number}' for part type '{part_type_id}' " \
                            "is assigned to {len(resp[RA_DATA])} parts."
                logger.error(msg)
                raise ValueError(msg)
        return cls._cache[part_type_id, serial_number]
    @classmethod
    def update(cls, part_type_id, serial_number, data):
        cls._cache[(part_type_id, serial_number)] = (data[RA_PART_TYPE_ID], data)
    @classmethod
    def delete(cls, part_type_id, serial_number):
        if (part_type_id, serial_number) in cls._cache.keys():
            del cls._cache[(part_type_id, serial_number)]

SN_Lookup = _SN_Lookup()



class Docket:
    def __init__(self, dkt):

        self.terminate_on_error = True

        # Global values for docket
        self.values = {}

        # Sources to be processed along with all data applicable to these sources
        self.sources = []

        # Encoders to process source files
        self.encoders = {}

        # Accumulators for HWDB requests
        self.new_hwitems = []
        self.update_hwitems = []
        self.enable_hwitems = []
        self.remove_subcomponents = []
        self.attach_subcomponents = []
        self.attach_hwitem_images = []     
        self.new_tests = []
        self.attach_test_images = []     
 
        # Cache of Excel/CSV files
        self._file_cache = {}

        # Multiple Dockets can be aggregated and sometimes need to be assigned
        # names, if they are unnamed. The docket counter is used to assign them
        # a name.
        self.docket_counter = 0

        # Add the docket. If it's a list, add each item in the list as a
        # separate docket.
        if type(dkt) == list:
            with item in dkt:
                self.add_docket(item)
        else:
            self.add_docket(dkt)


    def add_docket(self, dkt):
        self.docket_counter += 1

        # Let's make a copy, since we're going to be tweaking it as we
        # go along, and we don't want to mess up the original
        dkt = deepcopy(dkt)

        # If the docket is unnamed, give it a generic name
        if DKT_DOCKET_NAME not in dkt.keys():
            dkt[DKT_DOCKET_NAME] = f"Unnamed Docket {self.docket_counter}"

        self._parse_values(dkt)
        self._parse_sources(dkt)
        self._parse_encoder(dkt)


    @classmethod
    def df_coalesce_generator(cls, df, row_index, context={}):
        def df_coalesce(col_name):
            # If the column col_name exists, return the value in that column.
            # If the cell is empty, return an empty string.
            # If the column does NOT exist, check the context to see if there's
            # a default value and return it.
            # If there's no default, either, return None
            # Note that "" and None are different. The choice is deliberate.

            result = None
            if col_name in df.columns:
                if not pd.isna(df[col_name][row_index]):
                    result = df[col_name][row_index]
                else:
                    result = ""
            if result is None and col_name in context.keys():
                result = values[col_name]
            if type(result) is np.int64:
                result = int(result)
            return result
        return df_coalesce   
 
    def _parse_values(self, dkt):
        if DKT_VALUES not in dkt.keys():
            return

        self.values = {**self.values, **dkt[DKT_VALUES]}

    def _generate_hwitem_requests(self, old_data, new_data):

        #pp(old_data)
        #pp(new_data)

        if old_data is None:
            self._generate_new_hwitem(new_data)
        else:
            self._generate_update_hwitem(old_data, new_data)        


    def _generate_new_hwitem(self, new_data):
        
        # Make sure required information is there.
        if new_data[RA_INSTITUTION] is None:
            ValueError("Institution ID is required")
        if new_data[RA_COUNTRY_CODE] is None:
            ValueError("Country Code is required")


        # Generate request for creating a new hwitem
        data = \
        {
            RA_COMPONENT_TYPE: {RA_PART_TYPE_ID: new_data[RA_PART_TYPE_ID]},
            RA_INSTITUTION: {RA_ID: new_data[RA_INSTITUTION]},
            RA_COUNTRY_CODE: new_data[RA_COUNTRY_CODE],
            RA_MANUFACTURER: {RA_ID: new_data[RA_MANUFACTURER]},
            RA_SERIAL_NUMBER: new_data[RA_SERIAL_NUMBER],
            RA_SPECIFICATIONS: new_data[RA_SPECIFICATIONS],
            RA_COMMENTS: new_data[RA_COMMENTS],
        }

        self.new_hwitems.append(
            {
                "operation": "post_hwitem",
                "kwargs": 
                {
                    "part_type_id": new_data[RA_PART_TYPE_ID],
                    "data": data,
                }
            }
        )

        # Generate request for updating enabled status
        self.enable_hwitems.append(
            {
                "operation": "enable_hwitem",
                "kwargs":
                {
                    "part_id": f"{new_data[RA_PART_TYPE_ID]}:{new_data[RA_SERIAL_NUMBER]}",
                    "enable": new_data[RA_ENABLED],
                }
            }
        )
    
        # Generate request for attaching subcomponents
        if len(new_data[RA_SUBCOMPONENTS]) > 0:
            self.attach_subcomponents.append(
                {
                    "operation": "set_subcomponents",
                    "kwargs":
                    {
                        "part_id": f"{new_data[RA_PART_TYPE_ID]}:{new_data[RA_SERIAL_NUMBER]}",
                        "subcomponents": new_data[RA_SUBCOMPONENTS], 
                    }
                }
            )
        



    def _generate_update_hwitem(self, old_data, new_data):
        # Test the things that MUST NOT be changed and raise an error if this is attempted
        # If they are None, interpret it as not trying to change it
        if new_data.get(RA_INSTITUTION, None) is not None:
            if new_data[RA_INSTITUTION] != old_data[RA_INSTITUTION][RA_ID]:
                raise ValueError("Institution code cannot be changed!")
        if new_data.get(RA_COUNTRY_CODE, None) is not None:
            if new_data[RA_COUNTRY_CODE] != old_data[RA_COUNTRY_CODE]:
                raise ValueError("Country code cannot be changed!")
 
        data_has_changed = False
        enabled_has_changed = False

        #trace = []

        data = \
        {
            RA_PART_ID: old_data[RA_PART_ID],
        }
        enabled = None


        # Test if the things ALLOWED to change have changed
        # If they are None, interpret it as not trying to change it
        if new_data.get(RA_SERIAL_NUMBER, None) is not None:
            data[RA_SERIAL_NUMBER] = new_data[RA_SERIAL_NUMBER]
            if new_data[RA_SERIAL_NUMBER] != old_data[RA_SERIAL_NUMBER]:
                #trace.append("serial_number has changed")
                data_has_changed = True
        else:
            data[RA_SERIAL_NUMBER] = old_data[RA_SERIAL_NUMBER]

        if new_data.get(RA_COMMENTS, None) is not None:
            data[RA_COMMENTS] = new_data[RA_COMMENTS]
            if new_data[RA_COMMENTS] != old_data[RA_COMMENTS]:
                #trace.append("comments has changed")
                data_has_changed = True
        else:
            data[RA_COMMENTS] = old_data[RA_COMMENTS]
        
        if new_data.get(RA_MANUFACTURER) is not None:
            data[RA_MANUFACTURER] = {RA_ID: new_data[RA_MANUFACTURER]}
            if new_data[RA_MANUFACTURER] != old_data[RA_MANUFACTURER][RA_ID]:
                #trace.append("manufacturer has changed")
                data_has_changed = True
        else:
            data[RA_MANUFACTURER] = {RA_ID: old_data[RA_MANUFACTURER][RA_ID]}

        if new_data.get(RA_ENABLED, None) is not None:
            if new_data[RA_ENABLED] != old_data[RA_ENABLED]:
                enabled = new_data[RA_ENABLED]
                #trace.append("enabled has changed (1)")
                enabled_has_changed = True
        else:
            # If enabled is None, interpret it as true.
            # Any time we patch a hwitem, assume we want to enable it, unless we 
            # SPECIFICALLY disable it.
            enabled = True 
            if old_data[RA_ENABLED] == False:
                #trace.append("enabled has changed (2)")
                enabled_has_changed = True

        # For specifications, DO NOT assume that the new data can be None. It should
        # be given every time.
        # Luckily, python allows comparing dictionaries even if their keys are in 
        # a different order.
        if new_data[RA_SPECIFICATIONS] != old_data[RA_SPECIFICATIONS][0]:
            #trace.append("specifications has changed")
            data_has_changed = True
        # put this in there regardless of whether it was the thing 
        # that triggered the "data_has_changed" flag
        data[RA_SPECIFICATIONS] = new_data[RA_SPECIFICATIONS]

        

        if data_has_changed:
            self.update_hwitems.append(
                {
                    "operation": "patch_hwitem",
                    "kwargs": 
                    {
                        "part_id": old_data[RA_PART_ID],
                        "data": data,
                    },
                    #"old_data": old_data,
                    #"new_data": new_data,
                    #"trace": trace,
                }
            )
        else:
            self.update_hwitems.append(
                {
                    "operation": "no action",
                    "info": f"{old_data[RA_PART_ID]} is up to date.",
                }
            )

        if enabled_has_changed:
            self.enable_hwitems.append(
                {
                    "operation": "enable_hwitem",
                    "kwargs":
                    {
                        "part_id": old_data[RA_PART_ID],
                        "enable": enabled,
                        "comments": data[RA_COMMENTS],
                    },
                    #"old_data": old_data,
                    #"new_data": new_data,
                    #"trace": trace,
                }
            )
        else:
            self.enable_hwitems.append(
                {
                    "operation": "no action",
                    "info": f"{old_data[RA_PART_ID]} enabled status is up to date.",
                }
            )

        # Test for changes in subcomponents
        # This is a little more complicated than just comparing "old" and "new" because
        # "old" is only going to contain the functional positions that have been filled,
        # but "new" is going to have all available functional positions, with None when
        # there is no subcomponent there.
        # Note that since "new" is figuring out what subcomponents to look for based on
        # the component type's definition, there can't be any "extras" in "old" to look
        # for.
        # If there are changes AND there were subcomps in "old", we need to remove the
        # old ones first. (I mean, technically, we don't have to, but if the old ones
        # are going to be picked up by a different parent, and we don't know what order
        # the requests will process, we really should drop old ones first.
        drops = {}
        adds = {}

        for funcpos in new_data[RA_SUBCOMPONENTS].keys():
            if new_data[RA_SUBCOMPONENTS][funcpos] != old_data[RA_SUBCOMPONENTS].get(funcpos, None):
                adds[funcpos] = new_data[RA_SUBCOMPONENTS][funcpos]
                if old_data.get(funcpos, None) is not None:
                    drops[funcpos] = None

        if len(drops) > 0:
            self.remove_subcomponents.append(
                {
                    "operation": "set_subcomponents",
                    "kwargs":
                    {
                        "part_id": old_data[RA_PART_ID],
                        "subcomponents": drops,
                    }
                }
            )
        if len(adds) > 0:
            self.attach_subcomponents.append(
                {
                    "operation": "set_subcomponents",
                    "kwargs":
                    {
                        "part_id": old_data[RA_PART_ID],
                        "subcomponents": adds,
                    },
                    
                    #"old_data": old_data,
                    #"new_data": new_data,
                }
            ) 


    def _parse_source(self, dkt, source_item):
        logger.debug(f"parsing {source_item}")

        # The source should be a dictionary, but it is allowed to be a string.
        # If it's a string, put it in a dictionary under "File Name" and use 
        # that dictionary instead.
        if type(source_item) == str:
            source_item = {DKT_FILES: source_item}
        if type(source_item) != dict:
            raise ValueError(f"Objects in '{DKT_SOURCE}' node must be strings or dictionaries")
        
        # Accumulate the 'refined' source node data here
        src = {
            DKT_SOURCE_NAME: source_item[DKT_SOURCE_NAME],
            # We are potentially accumulating from several dockets,
            # so record which docket this source came from
            DKT_DOCKET_NAME: dkt[DKT_DOCKET_NAME]
        }

        # The source node MUST have a filename. 
        if DKT_FILES not in source_item:
            raise ValueError(f"""Source Node "{source_item[DKT_SOURCE_NAME]} must have a """
                                """'{DKT_FILES}' node.""")
        
        # The filename could actually be a list, so promote a single item to 
        # a list and handle it that way. (Though, I suspect it'll usually just
        # be a single item.) 
        filenames = source_item[DKT_FILES]
        if type(filenames) == str:
            filenames = [ filenames ]

        # Let's find all the files that match the items in filename, using glob
        # rules.
        files = []
        for filename in filenames:
            #globbed = [ os.path.abspath(fn) 
            #                for fn in glob(os.path.expanduser(filename)) ]
            globbed = glob(os.path.expanduser(filename))
            files.extend(globbed)
        if len(files) == 0:
            msg = (f"Warning: file patterns in source '{src[DKT_SOURCE_NAME]}' in "
                    f"docket '{src[DKT_DOCKET_NAME]}' doesn't match any files.")
            logger.warning(msg)
            print(msg)

        # Grab the values attached at the source node level, if any.
        values = source_item.get(DKT_VALUES, {})

        # Check for an encoder at the source node level
        # (Note that there can be one at the sheet level that overrides this)
        encoder_name = source_item.get(DKT_ENCODER, None)
        if encoder_name is None:
            encoder_name = DKT_AUTO        
        
        # Check for a data type (e.g., item, test, image list)
        data_type = source_item.get(DKT_SHEET_TYPE, None)
        if data_type is None:
            data_type = DKT_UNKNOWN

        # Let's go through each sheet for each file and assemble exactly what
        # operation we're trying to do on it into a manifest
        manifest = []
        
        for filename in files:
            if filename not in self._file_cache.keys():
                try:
                    excel_file = pd.ExcelFile(filename)
                    self._file_cache[filename] = {
                        DKT_FILE_TYPE: DKT_EXCEL,
                        DKT_FILE_HANDLE: excel_file,
                        DKT_SHEET_NAME: excel_file.sheet_names,
                    }
                except ValueError as err1:
                    try:
                        csv_file = pd.read_csv(filename)
                        self._file_cache[filename] = {
                            DKT_FILE_TYPE: DKT_CSV,
                            DKT_FILE_HANDLE: csv_file,
                        }
                    except ValueError as err2:
                        msg = f"Could not parse '{filename}' as Excel or CSV."
                        logger.error(msg)
                        logger.info(f"As Excel: {err1}")
                        logger.info(f"As CSV: {err2}")
                        raise err2
            file_info = self._file_cache[filename]

            # Handle CSV files
            if file_info[DKT_FILE_TYPE] == DKT_CSV:
                # If this is a CSV file, it better not have Sheets!
                if  DKT_SHEETS in source_item.keys():
                    msg = (f"Warning: source node '{src[DKT_SOURCE_NAME]}' in "
                        f"docket '{src[DKT_DOCKET_NAME]}' contains CSV files which have "
                        f"no sheets to match.")
                    logger.warning(msg)
                    print(msg)
                else:
                    manifest.append(
                        {
                            DKT_FILE_NAME: filename,
                            DKT_VALUES: {**values, **self.values},
                            DKT_ENCODER: encoder_name,
                            DKT_SHEET_TYPE: data_type,
                        })
            
            # Handle Excel files
            else: 
                # If no sheets are specified, do ALL sheets
                if DKT_SHEETS not in source_item.keys():

                    # Iterate through the sheets 
                    for sheet_name in file_info[DKT_SHEET_NAME]:
                        manifest.append(
                            {
                                DKT_FILE_NAME: filename,
                                DKT_SHEET_NAME: sheet_name,
                                DKT_VALUES: {**values, **self.values},
                                DKT_ENCODER: encoder_name,
                                DKT_SHEET_TYPE: data_type,
                            })
                # Add the sheets specified
                else:
                    sheets = source_item[DKT_SHEETS]
                    if type(sheets) == str:
                        sheets = [ {DKT_SHEET_NAME: sheets} ]
                    elif type(sheets) == dict:
                        sheets = [ sheets ]

                    for sheet_info in sheets:
                        sheet_encoder = sheet_info.get(DKT_ENCODER, None)
                        if sheet_encoder is None:
                            sheet_encoder = encoder_name
                        sheet_data_type = sheet_info.get(DKT_SHEET_TYPE, None)
                        if sheet_data_type is None:
                            sheet_data_type = data_type
                    

                        if DKT_SHEET_NAME not in sheet_info:
                            msg = (f"Error: source node '{src[DKT_SOURCE_NAME]}' in "
                                f"docket '{src[DKT_DOCKET_NAME]}': Sheets node list "
                                f"must contain 'Sheet Name'")
                            logger.error(msg)
                            print(msg)
                            raise ValueError(msg)
                        sheet_name = sheet_info[DKT_SHEET_NAME]
                        if sheet_name not in file_info[DKT_SHEET_NAME]:
                            print(file_info[DKT_SHEET_NAME])
                            msg = (f"Error: source node '{src[DKT_SOURCE_NAME]}' in "
                                f"docket '{src[DKT_DOCKET_NAME]}': file '{filename}' does "
                                f"not contain sheet '{sheet_name}'")
                            logger.error(msg)
                            print(msg)
                            raise ValueError(msg)
                        sheet_values = sheet_info.get(DKT_VALUES, {})
                        manifest.append(
                            {
                                DKT_FILE_NAME: filename,
                                DKT_SHEET_NAME: sheet_name,
                                DKT_VALUES: {**sheet_values, **values, **self.values},
                                DKT_ENCODER: sheet_encoder,
                                DKT_SHEET_TYPE: sheet_data_type,
                            })

        src["Manifest"] = manifest

        #src[DKT_FILES] = files

        # Add this source to sources
        self.sources.append(src) 

    def _parse_sources(self, dkt):
        logger.debug("Parsing sources")
        if DKT_SOURCES not in dkt.keys():
            logger.warning(f"Docket '{dkt[DKT_DOCKET_NAME]}' has no '{DKT_SOURCES}' node")
            return

        # Grab the sources node. It should be a list, but it is allowed to be
        # a single item if there's only one item. In that case, grab it and
        # put it in a list so that it can be handled the same ways lists are.
        sources = dkt[DKT_SOURCES]
        if type(sources) != list:
            sources = dkt[DKT_SOURCES]

        for source_index, source_item in enumerate(sources):
            if DKT_SOURCE_NAME not in source_item.keys():
                source_item[DKT_SOURCE_NAME] = "Unnamed Source Node {source_index}"
            self._parse_source(dkt, source_item)
        
    def _parse_encoder(self, dkt):
        pass


    def _process_auto_item(self, source_node, sheet_node):
    
        # We need to analyze the component type to see what fields we even need
        # TBD: we can possibly get this from the sheet in the future, but for now
        # it MUST be in the "Values"
      
        # First, let's get the Type ID 
        if DKT_TYPE_NAME in sheet_node[DKT_VALUES]: 
            type_info = ut.lookup_part_type_id_by_fullname(sheet_node[DKT_VALUES][DKT_TYPE_NAME])
            if DKT_TYPE_ID in sheet_node[DKT_VALUES]:
                # If both Type ID and Type Name are given, they must match!
                if sheet_node[DKT_VALUES][DKT_TYPE_ID] != type_info[1]:
                    raise ValueError("Type ID and Type Name do not match!")
            else:
                sheet_node[DKT_VALUES][DKT_TYPE_ID] = type_info[1]
        elif DKT_TYPE_ID not in sheet_node[DKT_VALUES]:
            raise ValueError("Unable to determine Type ID!")
        part_type_id = sheet_node[DKT_VALUES][DKT_TYPE_ID]

        
        # Now let's go to the HWDB and see what fields we're going to need, 
        # i.e, what fields are in the Specs and Subcomponents
        
        comp_type_info = ut.lookup_component_type_defs(part_type_id)
        #print(comp_type_info)

        # Get the data from the sheet    
        file_info = self._file_cache[sheet_node[DKT_FILE_NAME]]
        if file_info[DKT_FILE_TYPE] == DKT_EXCEL:
            df = pd.read_excel(file_info[DKT_FILE_HANDLE], sheet_node[DKT_SHEET_NAME])
        else:
            df = file_info[DKT_FILE_HANDLE]
        #print(df)


        # Let's start putting together some items to add to the HWDB        
        for row_index in range(len(df)):
            
            # Create a coalesce "helper" to speed lookups of data
            df_coalesce = self.df_coalesce_generator(df, row_index, sheet_node[DKT_VALUES]) 

            #method = None
            #has_changed = None
            old_data = None
            new_data = {RA_PART_TYPE_ID: part_type_id}

            # Examine External ID and Serial Number to determine if we're adding a new item or
            # updating an existing item
            part_id = df_coalesce(DKT_EXTERNAL_ID)
            serial_number = df_coalesce(DKT_SERIAL_NUMBER)

            if part_id is None or part_id=='':
                if serial_number is None:
                    ValueError("New HW Items must have a serial number")
                else:
                    new_data[RA_SERIAL_NUMBER] = serial_number
                    if SN_Lookup(part_type_id, serial_number) is None:
                        new_data[RA_COMPONENT_TYPE] = {RA_PART_TYPE_ID: part_type_id},
                    else:
                        part_id, old_data = SN_Lookup(part_type_id, serial_number)
                        new_data[RA_PART_ID] = part_id
            else:
                old_data =  get_hwitem_complete(part_id)
                new_data[RA_SERIAL_NUMBER] = serial_number

            inst_id = df_coalesce(DKT_INST_ID)
            if inst_id is not None:
                new_data[RA_INSTITUTION] = df_coalesce(DKT_INST_ID)
                new_data[RA_COUNTRY_CODE] = ut.lookup_institution_by_id(
                        new_data[RA_INSTITUTION])[RA_COUNTRY][RA_CODE]

            # User can "override" the country code associated with the institution,
            # though I can't think of why they'd do that.
            if df_coalesce(DKT_COUNTRY_CODE) is not None:
                new_data[RA_COUNTRY_CODE] = df_coalesce(DKT_COUNTRY_CODE)

            if df_coalesce(DKT_MANU_ID) is not None:
                new_data[RA_MANUFACTURER] = df_coalesce(DKT_MANU_ID)
            
            if df_coalesce(DKT_COMMENTS) is not None:
                new_data[RA_COMMENTS] = str(df_coalesce(DKT_COMMENTS))
            
            #print(f"ENABLED: {df_coalesce(DKT_ENABLED)}")
            if df_coalesce(DKT_ENABLED) is not None:
                new_data[RA_ENABLED] = df_coalesce(DKT_ENABLED)
                if str(new_data[RA_ENABLED]).lower() in ['0', 'false', 'no', '']:
                    new_data[RA_ENABLED] = False
                elif str(new_data[RA_ENABLED]).lower() in ['1', 'true', 'yes']:
                    new_data[RA_ENABLED] = True
                else:
                    raise ValueError("Enabled could not be cast as a boolean value")
            else:
                # if it's None, then default to Enable being true.
                new_data[RA_ENABLED] = True 

            specs = {}
            for spec_item in comp_type_info['spec_def'].keys():
                specs[spec_item] = df_coalesce(spec_item)
            new_data[RA_SPECIFICATIONS] = specs

            subcomponents = {}
            for subcomp in comp_type_info[RA_SUBCOMPONENTS].keys():
                raw_subcomp = df_coalesce(subcomp)
                    
                if re.match("^[A-Za-z][0-9]{11}-[0-9]{5}$", raw_subcomp) is None:
                    subcomponents[subcomp] = \
                            f"{comp_type_info[RA_SUBCOMPONENTS][subcomp]}:{raw_subcomp}"
                else:
                    subcomponents[subcomp] = raw_subcomp
            new_data[RA_SUBCOMPONENTS] = subcomponents

            self._generate_hwitem_requests(old_data, new_data)

    def _resolve_serial_number(self, alt_id, part_id):
        for op_node in self.enable_hwitems:
            if op_node["operation"] == "enable_hwitem":
                if op_node["kwargs"][RA_PART_ID] == alt_id:
                    op_node["kwargs"][RA_PART_ID] = part_id
        for op_node in self.attach_subcomponents:
            if op_node["operation"] == "set_subcomponents":
                if op_node["kwargs"][RA_PART_ID] == alt_id: 
                    op_node["kwargs"][RA_PART_ID] = part_id
                for funcpos, subcomp in op_node["kwargs"]["subcomponents"].items():
                    if subcomp == alt_id:
                        op_node["kwargs"]["subcomponents"][funcpos] = part_id
        part_type_id, serial_number = alt_id[:12], alt_id[13:]
        SN_Lookup.delete(part_type_id, serial_number)

    def display_plan(self):
        print("========== New Items ===========")
        pp(self.new_hwitems)
        print("======== Updated Items =========") 
        pp(self.update_hwitems)
        print("======== Enable Status =========")
        pp(self.enable_hwitems)
        print("===== Remove Subcomponents =====")
        pp(self.remove_subcomponents)
        print("===== Attach Subcomponents =====")
        pp(self.attach_subcomponents)

    def update_hwdb(self):

        # Add the new items
        for op_node in self.new_hwitems:
            if op_node["operation"] == "post_hwitem":
                print("== posting item ==")
                pp(op_node)
                resp = ra.post_hwitem(**op_node["kwargs"])
                if resp[RA_STATUS] != RA_STATUS_OK:
                    raise RuntimeError("Failed to post hwitem")
                
                # Update any future operations that are still referring to the serial number
                #   instead of part_id
                part_id = resp[RA_PART_ID]
                alt_id = f'{op_node["kwargs"]["part_type_id"]}:' \
                            f'{op_node["kwargs"]["data"][RA_SERIAL_NUMBER]}'
                #SN_Lookup.delete(*alt_id)
                self._resolve_serial_number(alt_id, part_id)
        
        # Update items
        for op_node in self.update_hwitems:
            if op_node["operation"] == "patch_hwitem":
                print("== updating item ==")
                pp(op_node)
                resp = ra.patch_hwitem(**op_node["kwargs"])
                if resp[RA_STATUS] != RA_STATUS_OK:
                    raise RuntimeError("Failed to patch hwitem")
                
                # Update any future operations that are still referring to the serial number
                #   instead of part_id
                # This should be less likely for an update, but it's still possible 
                part_id = resp[RA_PART_ID]
                
                # HACK HACK HACK
                part_type_id = part_id[:12]
                alt_id = f'{part_type_id}:{op_node["kwargs"]["data"][RA_SERIAL_NUMBER]}'
                #SN_Lookup.delete(*alt_id)
                self._resolve_serial_number(alt_id, part_id)
        
        # Update the enabled status
        for op_node in self.enable_hwitems:
            if op_node["operation"] == "enable_hwitem":
                print("== updating enable status ==")
                pp(op_node)
                alt_id = op_node["kwargs"]["part_id"]
                if ":" in alt_id:
                    part_type_id, serial_number = alt_id[:12], alt_id[13:]
                    part_id, data = SN_Lookup(part_type_id, serial_number)
                    op_node["kwargs"]["part_id"] = part_id
                resp = ut.enable_hwitem(**op_node["kwargs"])
                if resp[RA_STATUS] != RA_STATUS_OK:
                    raise RuntimeError("Failed to update enable status")

        # Update subcomponents                
        for op_node in self.remove_subcomponents:
            if op_node["operation"] == "set_subcomponents":
                print("== removing subcomponents ==")
                pp(op_node)
                for funcpos, subcomp in op_node["kwargs"]["subcomponents"].items():
                    if ":" in subcomp:
                        part_type_id, serial_number = subcomp[:12], subcomp[13:]
                        part_id, data = SN_Lookup(part_type_id, serial_number)
                        op_node["kwargs"]["subcomponents"][funcpos] = part_id
                resp = ut.set_subcomponents(**kwargs)
                if resp[RA_STATUS] != RA_STATUS_OK:
                    raise RuntimeError("Failed to remove subcomponents")
        for op_node in self.attach_subcomponents:
            if op_node["operation"] == "set_subcomponents":
                print("== attaching subcomponents ==")
                pp(op_node)
                for funcpos, subcomp in op_node["kwargs"]["subcomponents"].items():
                    if ":" in subcomp:
                        part_type_id, serial_number = subcomp[:12], subcomp[13:]
                        part_id, data = SN_Lookup(part_type_id, serial_number)
                        op_node["kwargs"]["subcomponents"][funcpos] = part_id
                resp = ut.set_subcomponents(**op_node["kwargs"])
                if resp[RA_STATUS] != RA_STATUS_OK:
                    raise RuntimeError("Failed to remove subcomponents")






    def _process_auto_test(self, source_node, sheet_node):
        print("skipping test node")
        pass



    def _process_auto_item_images(self, source_node, sheet_node):
        print("skipping item images node")
        pass




    def _process_auto_test_images(self, source_node, sheet_node):
        print("skipping test images node")
        pass


    def process_sources(self):
        pp(self.sources)
        for source_node in self.sources:
            for sheet_node in source_node["Manifest"]:

                if sheet_node[DKT_ENCODER] == DKT_AUTO:
                    if sheet_node[DKT_SHEET_TYPE] == DKT_ITEM:
                        self._process_auto_item(source_node, sheet_node)
                    elif sheet_node[DKT_SHEET_TYPE] == DKT_TEST:
                        self._process_auto_test(source_node, sheet_node)
                    elif sheet_node[DKT_SHEET_TYPE] == DKT_ITEM_IMAGES:
                        self._process_auto_item_images(source_node, sheet_node)
                    elif sheet_node[DKT_SHEET_TYPE] == DKT_TEST_IMAGES:
                        self._process_auto_test_images(source_node, sheet_node)
                    else:
                        raise ValueError("Automatic detection of data type not implemented (yet)")
                else:
                    raise ValueError("Custom encoders not implemented (yet)")






















