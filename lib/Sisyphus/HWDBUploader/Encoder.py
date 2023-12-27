#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Encoder.py
Copyright (c) 2023 Regents of the University of Minnesota
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

pp = lambda s: print(json.dumps(s, indent=4))

printcolor = lambda c, s: print(Style.fg(c)(s))

#{{{
# Schema fields correspond to the database fields for the record type
# (Item, Test, etc.) that this encoder handles. The Encoder's "Schema"
# doesn't need to specify these unless they need some special handling
# that's different than the defaults.
default_schema_fields = \
{
    # for all record types:
    "Serial Number": {"datatype":"string", "column":"Serial Number", "default":None},
    "External ID": {"datatype":"string", "column":"External ID", "default":None},

    # for record type 'Item':
    "Institution": {"datatype":"string", "column":"Institution", "default":None},
    "Institution ID": {"datatype":"integer", "column":"Institution ID", "default":None},
    "Institution Name": {"datatype":"string", "column":"Institution Name", "default":None},
    "Country": {"datatype":"string", "column":"Country", "default":None},
    "Country Code": {"datatype":"string", "column":"Country Code", "default":None},
    "Country Name": {"datatype":"string", "column":"Country Name", "default":None},
    "Manufacturer": {"datatype":"string", "column":"Manufacturer", "default":None},
    "Manufacturer ID": {"datatype":"integer", "column":"Manufacturer ID", "default":None},
    "Manufacturer Name": {"datatype":"string", "column":"Manufacturer Name", "default":None},
    "Item Comments": {"datatype":"string", "column":"Comments", "default":None}, # SEE NOTE!
    "Subcomponents": {"datatype":"special"},
    "Specifications": {"datatype":"special"},
    "Enabled": {"datatype":"boolean", "column":"Enabled", "default":True},
    # NOTE: since "Comments" could belong to multiple record types or even
    #       in the datasheets for Items or Tests, we have to give it a 
    #       very specific name in the schema (e.g., "Item Comments") but
    #       indicate that it will be found under a more generic name in
    #       the spreadsheet (e.g., "Comments). But, it's configurable!

    # for record type 'Test':
    "Test Comments": {"datatype":"string", "column":"Comments", "default":None},
    "Test Results": {"datatype":"special"},

    # for record_type 'Item Image" or "Test Image":
    "Image Comments": {"datatype":"string", "column":"Comments", "default":None},
    "Source File": {"datatype":"string", "column":"File", "default":None},
    "File Name": {"datatype":"string", "column":"Rename", "default":None},
}
#}}}

class Encoder:
    def __init__(self, encoder_def):
        self._encoder_def = deepcopy(encoder_def)
        enc = deepcopy(self._encoder_def)
        
        self.warnings = []
        
        self.name = enc.pop("Encoder Name", None)
        self.record_type = enc.pop("Record Type", None)
        self.part_type_name = enc.pop("Part Type Name", None)
        self.part_type_id = enc.pop("Part Type ID", None)
        self.test_name = enc.pop("Test Name", None)

        self.options = enc.pop("Options", {})
        self.schema = self._preprocess_schema(enc.pop("Schema", {}))

        # TODO: more fields


        #printcolor("cornflowerblue", "Encoder Def Unused Keys")
        #printcolor("cornflowerblue", json.dumps(enc, indent=4))

    def add_warning(self, warning):
        printcolor(0xffaa33, f"WARNING: {warning}")
        self.warnings.append(warning)

    def _preprocess_schema(self, schema):
        #{{{
        typedef_default = \
        {
            "datatype": "any", 
            "column": None, 
            "default": None,
        }

        sch_in = deepcopy(schema)
        sch_out = {}

        for schema_key, default_field_def in default_schema_fields.items():
        
            if schema_key in sch_in:
                #printcolor(0xff33cc, f"'{schema_key}' is in incoming schema")
                if default_field_def["datatype"] == "special":
                    # TODO: check if user already defined this as a group
                    # and process it differently

                    #printcolor(0xcc9933, f"'{schema_key}' is defined as 'special'")

                    sch_out[schema_key] = \
                    {
                        "datatype": "group",
                        "key": [],
                        "members": sch_in[schema_key],
                    }               
                else:
                    schema_field = sch_in.pop(schema_key)
                    if type(schema_field) is str:
                        sch_out[schema_key] = {**default_field_def, "datatype": schema_field}
                    else:
                        sch_out[schema_key] = {**default_field_def, **schema_field}
            else:
                #printcolor(0xcc1199, f"'{schema_key}' is not in incoming schema")
                if default_field_def["datatype"] == "special":
                    sch_out[schema_key] = \
                    {
                        "datatype": "group",
                        "key": [],
                        "members": {}
                    }
                else:
                    sch_out[schema_key] = deepcopy(default_field_def)

        #print(json.dumps(sch_out, indent=4))
        return sch_out
        #}}}

    def get_field(self, sheet, column, row_index):
        ...


    def encode(self, sheet):
        result = {}
        printcolor(0xffcc99, f"Record Type: {self.record_type}")

        for row_index in range(sheet.rows):
            row_record = {}
            for schema_key, field_def in self.schema.items():
                if field_def["datatype"] == "group":
                    continue
                
                #print(schema_key, field_def)
                field_contents = sheet.coalesce(field_def["column"], row_index)
                #row_record[schema_key] = field_contents
                printcolor(0x8888ff, f"schema_key: {schema_key}")
                print(f"source:   {field_contents.source}")
                print(f"location: {field_contents.location}")
                print(f"warnings: {field_contents.warnings}")
                print(f"datatype: {field_contents.datatype}")
                print(f"value:    {repr(field_contents.value)}")
                #print(f"value type:    {type(field_contents.value)}")
                #print(f"value as json: {json.dumps(value)}")

                field_contents.datatype = field_def["datatype"]

                cast_value = tc.cast(field_contents)
                row_record[schema_key] = cast_value.value

            print(row_record)
            print(json.dumps(row_record, indent=4))            


            ...   


        return result

    def decode(self, obj):
        ...

