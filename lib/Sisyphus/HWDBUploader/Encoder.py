#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Encoder.py
Copyright (c) 2024 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut
from Sisyphus.HWDBUploader.Sheet import Sheet, Cell
from Sisyphus.HWDBUploader import TypeCheck as tc
from Sisyphus.Utils.Terminal import Style

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re
import time
import random


KW_TYPE = "type"
KW_KEY = "key"
KW_COLUMN = "column"
KW_MEMBERS = "members"
KW_VALUE = "value"
KW_DEFAULT = "default"

pp = lambda s: print(json.dumps(s, indent=4))

printcolor = lambda c, s: print(Style.fg(c)(s))

#{{{
# Schema fields correspond to the database fields for the record type
# (Item, Test, etc.) that this encoder handles. The Encoder's "Schema"
# doesn't need to specify these unless they need some special handling
# that's different than the defaults.

default_schema_fields_by_record_type = \
{
    "Item":
    {
        # for all record types:
        "Serial Number": {KW_TYPE:"string,null", KW_COLUMN:"Serial Number", KW_DEFAULT:None},
        "External ID": {KW_TYPE:"string,null", KW_COLUMN:"External ID", KW_DEFAULT:None},

        # for record type 'Item':
        "Institution": {KW_TYPE:"string,null", KW_COLUMN:"Institution", KW_DEFAULT:None},
        "Institution ID": {KW_TYPE:"integer,null", KW_COLUMN:"Institution ID", KW_DEFAULT:None},
        "Institution Name": {KW_TYPE:"string,null", KW_COLUMN:"Institution Name", KW_DEFAULT:None},
        "Country": {KW_TYPE:"string,null", KW_COLUMN:"Country", KW_DEFAULT:None},
        "Country Code": {KW_TYPE:"string,null", KW_COLUMN:"Country Code", KW_DEFAULT:None},
        "Country Name": {KW_TYPE:"string,null", KW_COLUMN:"Country Name", KW_DEFAULT:None},
        "Manufacturer": {KW_TYPE:"string,null", KW_COLUMN:"Manufacturer", KW_DEFAULT:None},
        "Manufacturer ID": {KW_TYPE:"integer,null", KW_COLUMN:"Manufacturer ID", KW_DEFAULT:None},
        "Manufacturer Name": {KW_TYPE:"string,null", KW_COLUMN:"Manufacturer Name", KW_DEFAULT:None},
        "Item Comments": {KW_TYPE:"string,null", KW_COLUMN:"Comments", KW_DEFAULT:None}, # SEE NOTE!
        "Subcomponents": {KW_TYPE:"special"},
        "Specifications": {KW_TYPE:"special"},
        "Enabled": {KW_TYPE:"boolean", KW_COLUMN:"Enabled", KW_DEFAULT:True},
        # NOTE: since "Comments" could belong to multiple record types or even
        #       in the datasheets for Items or Tests, we have to give it a 
        #       very specific name in the schema (e.g., "Item Comments") but
        #       indicate that it will be found under a more generic name in
        #       the spreadsheet (e.g., "Comments). But, it's configurable!

        # for record type 'Test':
        "Test Comments": {KW_TYPE:"string,null", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Test Results": {KW_TYPE:"special"},

        # for record_type 'Item Image" or "Test Image":
        "Image Comments": {KW_TYPE:"string,null", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Source File": {KW_TYPE:"string,null", KW_COLUMN:"File", KW_DEFAULT:None},
        "File Name": {KW_TYPE:"string,null", KW_COLUMN:"Rename", KW_DEFAULT:None},
    },
    "Test":
    {
        # for all record types:
        "Serial Number": {KW_TYPE:"string,null", KW_COLUMN:"Serial Number", KW_DEFAULT:None},
        "External ID": {KW_TYPE:"string,null", KW_COLUMN:"External ID", KW_DEFAULT:None},

        # for record type 'Test':
        "Test Comments": {KW_TYPE:"string,null", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Test Results": {KW_TYPE:"special"},
    },
    "Item Image":
    {
        # for all record types:
        "Serial Number": {KW_TYPE:"string,null", KW_COLUMN:"Serial Number", KW_DEFAULT:None},
        "External ID": {KW_TYPE:"string,null", KW_COLUMN:"External ID", KW_DEFAULT:None},

        # for record_type 'Item Image" or "Test Image":
        "Image Comments": {KW_TYPE:"string,null", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Source File": {KW_TYPE:"string,null", KW_COLUMN:"File", KW_DEFAULT:None},
        "File Name": {KW_TYPE:"string,null", KW_COLUMN:"Rename", KW_DEFAULT:None},
    },
    "Test Image":
    {
        # for all record types:
        "Serial Number": {KW_TYPE:"string,null", KW_COLUMN:"Serial Number", KW_DEFAULT:None},
        "External ID": {KW_TYPE:"string,null", KW_COLUMN:"External ID", KW_DEFAULT:None},

        # for record_type 'Item Image" or "Test Image":
        "Image Comments": {KW_TYPE:"string,null", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Source File": {KW_TYPE:"string,null", KW_COLUMN:"File", KW_DEFAULT:None},
        "File Name": {KW_TYPE:"string,null", KW_COLUMN:"Rename", KW_DEFAULT:None},
    }
}
#}}}

class Encoder:
    def __init__(self, encoder_def):
        #{{{
        self._encoder_def = deepcopy(encoder_def)
        enc = deepcopy(self._encoder_def)
        
        self.warnings = []
        
        self.name = enc.pop("Encoder Name", None)
        
        self.record_type = enc.pop("Record Type", None)
        if self.record_type in default_schema_fields_by_record_type:
            self.default_schema_fields = default_schema_fields_by_record_type[self.record_type] 
        else:
            raise ValueError("Record Type is required.")
        
        self.part_type_name = enc.pop("Part Type Name", None)
        self.part_type_id = enc.pop("Part Type ID", None)
        self.test_name = enc.pop("Test Name", None)

        self.options = enc.pop("Options", {})
        
        self.raw_schema = enc.pop("Schema", {})
        self.schema = self._preprocess_schema(self.raw_schema)

        # TODO: more fields

        #printcolor("cornflowerblue", "Encoder Def Unused Keys")
        #printcolor("cornflowerblue", json.dumps(enc, indent=4))
        #}}}
    
    #-----------------------------------------------------------------------------        
    
    def add_warning(self, warning):
        printcolor(0xffaa33, f"WARNING: {warning}")
        self.warnings.append(warning)
    
    #-----------------------------------------------------------------------------        

    def _preprocess_schema(self, schema):
        #{{{
        typedef_default = \
        {
            KW_TYPE: "any", 
            KW_COLUMN: None, 
            KW_DEFAULT: None,
        }

        def preprocess_group(sch_in):
            #{{{
            #print(json.dumps(sch_in, indent=4))
            sch_in = deepcopy(sch_in)
            sch_out = {}

            for schema_key, field_def in sch_in.items():
                #print(schema_key, field_def)
                field_def = deepcopy(field_def)

                if type(field_def) is str:
                    sch_out[schema_key] = \
                    {
                        KW_TYPE: field_def,
                        KW_COLUMN: schema_key,
                        KW_DEFAULT: None
                    }
                    continue

                # From here forward, "field_def" is assumed to be a dict

                node = sch_out[schema_key] = {KW_TYPE: field_def.pop(KW_TYPE, "any")}
                
                if KW_VALUE in field_def:
                    node[KW_VALUE] = field_def.pop(KW_VALUE)
                    # TODO: check if there are any leftover keys
                    continue

                if node[KW_TYPE] == "group":
                    key = field_def.pop(KW_KEY, []) 
                    if type(key) is list:
                        node[KW_KEY] = key
                    else:
                        node[KW_KEY] = [key]

                    members = field_def.pop(KW_MEMBERS, {})
                    node[KW_MEMBERS] = preprocess_group(members)

                    # check that all the "key"s are in members
                    for key_name in node[KW_KEY]:
                        if key_name not in node[KW_MEMBERS]:
                            raise ValueError("Bad schema: key '{key_name}' not in members")

                    # TODO: check if there are any leftover keys
                    continue

                sch_out[schema_key] = "TBD"
            return sch_out
            #}}}

        sch_in = deepcopy(schema)
        sch_out = {}

        for schema_key, default_field_def in self.default_schema_fields.items():
        
            if schema_key in sch_in:
                #printcolor(0xff33cc, f"'{schema_key}' is in incoming schema")
                if default_field_def[KW_TYPE] == "special":
                    # TODO: check if user already defined this as a group
                    # and process it differently

                    #printcolor(0xcc9933, f"'{schema_key}' is defined as 'special'")

                    sch_out[schema_key] = \
                    {
                        KW_TYPE: "group",
                        KW_KEY: [],
                        KW_MEMBERS: preprocess_group(sch_in[schema_key]),
                    }               
                else:
                    field_def = sch_in.pop(schema_key)
                    if type(field_def) is str:
                        sch_out[schema_key] = {**default_field_def, KW_TYPE: field_def}
                    else:
                        sch_out[schema_key] = {**default_field_def, **field_def}
            else:
                #printcolor(0xcc1199, f"'{schema_key}' is not in incoming schema")
                if default_field_def[KW_TYPE] == "special":
                    sch_out[schema_key] = \
                    {
                        KW_TYPE: "group",
                        KW_KEY: [],
                        KW_MEMBERS: {}
                    }
                else:
                    sch_out[schema_key] = deepcopy(default_field_def)

        #print(json.dumps(sch_out, indent=4)); exit()
        #return sch_out
        return \
        {
            KW_TYPE: "group",
            KW_KEY: ["External ID", "Serial Number"],
            KW_MEMBERS: sch_out,
        }

        #}}}
    
    #-----------------------------------------------------------------------------        

    def index(self, record, schema=None):
        #{{{
        """Convert lists of row data into indexed dictionaries

        This makes it easier to locate rows so that information can be inserted.
        Since indexes may have more than one key, and JSON doesn't allow tuples
        to be keys, this format should be only used to manipulate data. It should
        be deindexed again before adding to the HWDB.
        """

        record = deepcopy(record)
        if schema is None:
            schema = self.schema

        indexed = { tuple(v[k] for k in schema[KW_KEY]): v for v in record }

        for k, v in indexed.items():
            for member_key, member_def in schema['members'].items():
                if member_def[KW_TYPE] == "group":
                    v[member_key] = self.index(v[member_key], member_def)

        return indexed
        #}}}    

    #-----------------------------------------------------------------------------        

    def deindex(self, record, schema=None):
        #{{{
        """Turn indexed rows back into lists"""

        record = deepcopy(record)
        if schema is None:
            schema = self.schema

        for k, v in record.items():
            for schema_key, field_def in schema[KW_MEMBERS].items():
                if field_def[KW_TYPE] == "group":
                    v[schema_key] = self.deindex(v[schema_key], field_def)
        
        return list(record.values())
        #}}}

    #-----------------------------------------------------------------------------        

    def merge_indexed_records(self, record, addendum, schema=None):
        #{{{
        """Merge two sets of row data when the rows are already indexed"""

        if schema is None:
            schema = self.schema
        
        merged = {}

        for schema_key, field_def in schema[KW_MEMBERS].items():
            if field_def[KW_TYPE] == "group":
                merged[schema_key] = deepcopy(record[schema_key])
                for k, v in addendum[schema_key].items():
                    if k in record[schema_key]:
                        merged[schema_key][k] = self.merge_indexed_records(
                                                    record[schema_key][k], 
                                                    v,
                                                    field_def)
                    else:
                        merged[schema_key][k] = v
            else:
                merged[schema_key] = record[schema_key]

        return merged
        #}}}

    #-----------------------------------------------------------------------------        

    def merge_records(self, record, addendum, schema=None):
        #{{{
        """Merge two sets of row data"""

        record_indexed = self.index(record, schema)
        addendum_indexed = self.index(addendum, schema)
        return merge_indexed_records(record_indexed, addendum_indexed, schema)
        #}}}

    #-----------------------------------------------------------------------------        

    def encode_indexed(self, sheet):
        #{{{
        """Encode a spreadsheet using the stored schema using indexed rows"""

        def encode_group(sheet, row_index, parent_field_def):
           
            group_value = {} 
 
            for schema_key, field_def in parent_field_def[KW_MEMBERS].items():
                
                if field_def[KW_TYPE] == "group":
                    k, v = encode_group(sheet, row_index, field_def)
                    group_value[schema_key] = {k: v} 
                    continue

                if KW_COLUMN in field_def:
                    field_contents = sheet.coalesce(field_def[KW_COLUMN], 
                                                    row_index, field_def[KW_TYPE])
                elif KW_VALUE in field_def:
                    field_contents = Cell(  
                            source="encoder", 
                            location=None,
                            warnings=[], 
                            datatype=field_def[KW_TYPE],
                            value=field_def[KW_VALUE])
                
                cast_value = tc.cast(field_contents)
                # TODO: handle warnings
                group_value[schema_key] = cast_value.value

            key = tuple( group_value[key] for key in parent_field_def[KW_KEY])
            
            return key, group_value


        result = {}

        for row_index in range(sheet.rows):
 
            key, group_value = encode_group(sheet, row_index, self.schema)

            if key not in result:
                result[key] = group_value
            else:
                result[key] = self.merge_indexed_records(result[key], group_value)

        return result
        #}}}    

    #-----------------------------------------------------------------------------

    def encode(self, sheet):
        #{{{
        """Encode a spreadsheet using the stored schema"""

        return self.deindex(self.encode_indexed(sheet))
        #}}}
    #-----------------------------------------------------------------------------        

    def decode(self, record):
        #{{{
        def make_row_template(schema):
            template = {}
            for schema_key, field_def in schema["members"].items():
                if field_def["type"] != "group":
                    template[schema_key] = field_def
                else:
                    template.update(make_row_template(field_def))
            return template


        template = make_row_template(self.schema)

        #printcolor(0x3333ff, json.dumps(template, indent=4))


        #printcolor(0xff33cc, json.dumps(Encoder.preserve_order(self.raw_schema), indent=4))
        #print()
        #indexed = self.index(record)

        def make_rows(record, schema, current_row):
            for item in record:
                #print(f"ITEM: {item}")
                current_row = deepcopy(current_row)
                next_group_key, next_group_field_def = None, None
                for schema_key, field_def in schema["members"].items():
                    if field_def[KW_TYPE] == "group":
                        next_group_key, next_group_field_def = schema_key, field_def
                    else:
                        current_row[schema_key] = item[schema_key]
                if next_group_key is not None:
                    make_rows(item[next_group_key], next_group_field_def, current_row)
                else:
                    rows.append(deepcopy(current_row))                    


        def append_row(current_row):
            pass


        record = deepcopy(record)
        rows = []
        current_row = {key: None for key in template}
        
        make_rows(record, self.schema, current_row)
            

        printcolor(0xffff00, json.dumps(rows, indent=4))

        #}}}

    #-----------------------------------------------------------------------------

    @staticmethod
    def preserve_order(obj):
        #{{{
        '''Recursively store the key order of any dictionaries found

        As of Python 3.6, dictionaries already preserve the order of their
        keys, but when uploading to the HWDB and downloading again, the 
        order of the keys is not guaranteed to stay the same. So, add an
        extra "_meta" tag that contains the correct order. 

        Lists always preserve order, so leave them alone (but still recurse
        through them). 

        Use 'restore_order' after downloading from the HWDB to get the 
        dictionaries back into the correct order.

        NOTE: this adds the _meta tags in-place, so 'obj' is actually 
        changed. Make a copy if this is not desired!
        '''

        if type(obj) is list:
            for item in obj:
                Encoder.preserve_order(item)
        elif type(obj) is dict:
            order = list(obj.keys())
            if "_meta" not in obj:
                obj["_meta"] = {}
            obj["_meta"]["keys"] = order
            
            # We have to make sure to skip the '_meta' tag, so we don't
            # recurse forever. Note that if there was already a '_meta' tag
            # before we added one, the order of its contents will not be
            # preserved.
            for key, item in obj.items():
                if key != '_meta':
                    Encoder.preserve_order(item) 
        
        # Even though the change was made in-place, return the object anyway.
        # It simplifies the syntax when one wants to make a copy:
        #     mycopy = Encoder.preserve_order(deepcopy(original))
        return obj
        #}}}

    @staticmethod
    def restore_order(obj):
        #{{{
        """Re-order the keys in dictionaries to saved order

        If the "_meta" tag only contains "keys", the entire "_meta" tag
        will be removed. Otherwise, only the "keys" will be removed.

        NOTE: this does the reordering 
        """

        if type(obj) is list:
            for item in obj:
                Encoder.restore_order(item)
        elif type(obj) is dict:
            if "_meta" in obj and "keys" in obj["_meta"]:
                # Get the preserved ordering, but then look for any extra
                # keys that might have been added and add those to the list
                # at the end. At the time this comment was written, this 
                # shouldn't happen, but I'd like it to go smoothly and not
                # drop data if this should happen in the future.
                order = obj["_meta"]["keys"]

                for key in order:
                    if key not in obj:
                        order.remove(key)
                for key in obj.keys():
                    if key not in order:
                        order.append(key)
                
                # Re-order the dictionary by popping each item and re-adding
                # it, which will place it at the end.
                for key in order:
                    obj[key] = obj.pop(key)
            
                obj['_meta'].pop("keys")
                if len(obj['_meta']) == 0:
                    obj.pop('_meta')


            for key, item in obj.items():
                Encoder.restore_order(item)
        
        # Even though the change was made in-place, return the object anyway.
        # It simplifies the syntax when one wants to make a copy:
        #     mycopy = Encoder.restore_order(deepcopy(original))
        return obj
        #}}}

    @staticmethod
    def scramble_order(obj):
        #{{{
        '''Scramble the order of keys in dictionaries

        This function serves only as a test to simulate what might happen
        to an object that was uploaded to the HWDB and downloaded again.
        '''

        if type(obj) is list:
            for item in obj:
                Encoder.scramble_order(item)
        elif type(obj) is dict:
            keys = list(obj.keys())

            # Shuffle the keys
            # if there are at least two keys, make sure the shuffle
            # actually changes the order. Redo if it doesn't.
            if len(keys) > 1:
                original_order = keys[:]
                while keys == original_order:
                    random.shuffle(keys)
            for key in keys:
                obj[key] = obj.pop(key)
            for key, item in obj.items():
                Encoder.scramble_order(item)
        
        # Even though the change was made in-place, return the object anyway.
        # It simplifies the syntax when one wants to make a copy:
        #     mycopy = Encoder.scramble_order(deepcopy(original))
        return obj
        #}}}

if __name__ == "__main__":
    pass






















