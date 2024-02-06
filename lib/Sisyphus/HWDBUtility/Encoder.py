#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUtility/Encoder.py
Copyright (c) 2024 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut
from Sisyphus.HWDBUtility.SheetReader import Sheet, Cell
from Sisyphus.HWDBUtility import TypeCheck as tc
from Sisyphus.Utils.Terminal.Style import Style

from Sisyphus.Utils import utils

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re
import time
import random
import uuid

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

default_universal_fields = \
{
    "Part Type ID": {KW_TYPE:"null,string", KW_COLUMN:"Part Type ID", KW_DEFAULT:None},
    "Part Type Name": {KW_TYPE:"null,string", KW_COLUMN:"Part Type Name", KW_DEFAULT:None},
    "Serial Number": {KW_TYPE:"null,string", KW_COLUMN:"Serial Number", KW_DEFAULT:None},
    "External ID": {KW_TYPE:"null,string", KW_COLUMN:"External ID", KW_DEFAULT:None},
}

default_schema_fields_by_record_type = \
{
    "Item":
    {
        # for all record types:
        **default_universal_fields,

        # for record type 'Item':
        "Institution": {KW_TYPE:"null,string", KW_COLUMN:"Institution", KW_DEFAULT:None},
        "Institution ID": {KW_TYPE:"null,integer", KW_COLUMN:"Institution ID", KW_DEFAULT:None},
        "Institution Name": {KW_TYPE:"null,string", KW_COLUMN:"Institution Name", KW_DEFAULT:None},
        "Country": {KW_TYPE:"null,string", KW_COLUMN:"Country", KW_DEFAULT:None},
        "Country Code": {KW_TYPE:"null,string", KW_COLUMN:"Country Code", KW_DEFAULT:None},
        "Country Name": {KW_TYPE:"null,string", KW_COLUMN:"Country Name", KW_DEFAULT:None},
        "Manufacturer": {KW_TYPE:"null,string", KW_COLUMN:"Manufacturer", KW_DEFAULT:None},
        "Manufacturer ID": {KW_TYPE:"null,integer", KW_COLUMN:"Manufacturer ID", KW_DEFAULT:None},
        "Manufacturer Name": {KW_TYPE:"null,string", KW_COLUMN:"Manufacturer Name", KW_DEFAULT:None},
        "Item Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None}, # SEE NOTE!
        "Subcomponents": {KW_TYPE:"special"},
        "Specifications": {KW_TYPE:"special"},
        "Enabled": {KW_TYPE:"boolean", KW_COLUMN:"Enabled", KW_DEFAULT:True},
        # NOTE: since "Comments" could belong to multiple record types or even
        #       in the datasheets for Items or Tests, we have to give it a 
        #       very specific name in the schema (e.g., "Item Comments") but
        #       indicate that it will be found under a more generic name in
        #       the spreadsheet (e.g., "Comments). But, it's configurable!
    },
    "Test":
    {
        # for all record types:
        **default_universal_fields,

        # for record_type 'Test' or 'Test Image':
        "Test Name": {KW_TYPE:"null,string", KW_COLUMN:"Test Name", KW_DEFAULT:None},

        # for record type 'Test':
        "Test Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Test Results": {KW_TYPE:"special"},
    },
    "Item Image":
    {
        # for all record types:
        **default_universal_fields,

        # for record_type 'Item Image' or 'Test Image':
        "Image Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Source File": {KW_TYPE:"null,string", KW_COLUMN:"File", KW_DEFAULT:None},
        "File Name": {KW_TYPE:"null,string", KW_COLUMN:"Rename", KW_DEFAULT:None},
    },
    "Test Image":
    {
        # for all record types:
        **default_universal_fields,

        # for record_type 'Test' or 'Test Image':
        "Test Name": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},

        # for record_type 'Item Image" or 'Test Image':
        "Image Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Source File": {KW_TYPE:"null,string", KW_COLUMN:"File", KW_DEFAULT:None},
        "File Name": {KW_TYPE:"null,string", KW_COLUMN:"Rename", KW_DEFAULT:None},
    }
}
#}}}



class Encoder:
    _encoder_cache = {}
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
        #Style.fg(0xff00cc).print(f"'{self.name}', '{self.record_type}'") 
        #Style.fg(0xffcc00).print( json.dumps(self.default_schema_fields , indent=4))


        self.part_type_name = enc.pop("Part Type Name", None)
        self.part_type_id = enc.pop("Part Type ID", None)
        self.test_name = enc.pop("Test Name", None)

        self.options = enc.pop("Options", {})
        
        self.raw_schema = enc.pop("Schema", {})
        self.schema = self._preprocess_schema(self.raw_schema)


        self.uuid = str(uuid.uuid4()).upper()
        self.__class__._encoder_cache[self.uuid] = self    

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
            KW_TYPE: "null,any", 
            KW_COLUMN: None, 
            KW_DEFAULT: None,
        }
        
        #......................................................................

        def preprocess_group(sch_in):
            #{{{
            #print(json.dumps(sch_in, indent=4))
            sch_in = deepcopy(sch_in)
            sch_out = {}

            for schema_key, field_def in sch_in.items():
                #if schema_key == "Length":
                #    breakpoint()
                #print(schema_key, field_def)
                field_def = deepcopy(field_def)
                #Style.info.print(schema_key, field_def)

                if type(field_def) is str:
                    sch_out[schema_key] = \
                    {
                        KW_TYPE: field_def,
                        KW_COLUMN: schema_key,
                        KW_DEFAULT: None
                    }
                    continue

                # From here forward, "field_def" is assumed to be a dict

                #node = sch_out[schema_key] = {KW_TYPE: field_def.pop(KW_TYPE, "any")}
                node = sch_out[schema_key] = {KW_TYPE: field_def.get(KW_TYPE, "null,any")}
               
                # If this has a "value", then this is just a constant that doesn't
                # actually depend on what's in the sheet. 
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

                #member_def = {**typedef_default, KW_COLUMN: schema_key}
                member_def = {**typedef_default, **field_def}

                sch_out[schema_key] = member_def

            return sch_out
            #}}}
        
        #......................................................................

        sch_in = deepcopy(schema)
        sch_out = {}

        #Style.fg(0xcc00ff).print(json.dumps(schema, indent=4))

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
        preprocessed_schema = \
        {
            KW_TYPE: "group",
            KW_KEY: ["External ID", "Serial Number"],
            KW_MEMBERS: sch_out,
        }

        #Style.fg(0x33ff33).print(json.dumps(preprocessed_schema, indent=4))

        #logger.warning(f"schema in:\n{json.dumps(schema, indent=4)}")
        #logger.warning(f"schema out:\n{json.dumps(preprocessed_schema, indent=4)}")


        return preprocessed_schema
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
        
        #......................................................................

        def encode_group(sheet, row_index, parent_field_def):
           
            group_value = {} 
 
            for schema_key, field_def in parent_field_def[KW_MEMBERS].items():
                #if schema_key == "Test Name":
                #    breakpoint()
                #print(schema_key)
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
                
                #cast_value = tc.cast(field_contents)

                #logger.info(f"schema_key: {schema_key}")
                #logger.info(f"field_def: {field_def}")
                #logger.debug(f"cell value: {field_contents}")
                #logger.debug(f"after casting:  {cast_value}")

                # TODO: handle warnings
                group_value[schema_key] = field_contents.value

            key = tuple( group_value[key] for key in parent_field_def[KW_KEY])
            
            return key, group_value
        
        #......................................................................
        sheet.local_values["Test Name"] = self.test_name

        result = {}

        for row_index in range(sheet.rows):

            key, group_value = encode_group(sheet, row_index, self.schema)

            if key not in result:
                result[key] = group_value
            else:
                result[key] = self.merge_indexed_records(result[key], group_value)

        #result.setdefault("_meta", {})["encoder_uuid"] = self.uuid
        return result
        #}}}    

    #-----------------------------------------------------------------------------

    def encode(self, sheet):
        #{{{
        """Encode a spreadsheet using the stored schema"""

        encoded_data = self.encode_indexed(sheet)
        deindexed = self.deindex(encoded_data)
        #print(deindexed)
        return deindexed, self.uuid
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
            

        #printcolor(0xffff00, json.dumps(rows, indent=4))

        #}}}

    #-----------------------------------------------------------------------------

    @staticmethod
    def create_auto_encoder(part_type_id, part_type_name, record_type, test_name=None):
        #{{{
        record_types = \
        {
            "item": "Item",
            "test": "Test",
            "item image": "Item Image",
            "test image": "Test Image",
        }


        if str(record_type).casefold() not in record_types.keys():
            raise ValueError("'Record Type' should be one of these: "
                            f"{list(record_types.values())}")
        else:
            record_type = record_types[record_type.casefold()]

        try:
            part_type_data = ut.fetch_component_type(part_type_id, part_type_name)
        except ra.MissingArguments:
            raise ValueError("Must identify Part Type in order to create auto-encoder") from None
        part_type_id = part_type_data["ComponentType"]['part_type_id']
        part_type_name = part_type_data["ComponentType"]['full_name']

        if record_type == 'Test':
            if test_name is None:
                raise ValueError("Must identify 'Test Name' when 'Record Type' is 'Test'.")
            elif test_name not in part_type_data["TestTypeDefs"]:
                raise ValueError(f"Part Type does not have a test '{test_name}'")  

        #......................................................................

        def create_item_encoder():
            encoder_def = \
            {
                "Encoder Name": f"_AUTO_{part_type_id}",
                "Record Type": "Item",
                "Part Type ID": part_type_id,
                "Part Type Name": part_type_name,
                "Schema": {"Specifications": {}, "Subcomponents": {}}
            }
            spec = part_type_data["ComponentType"]["properties"]["specifications"][0]["datasheet"]
            meta = spec.get('_meta', {})
            spec = utils.restore_order(deepcopy(spec))
            connectors = part_type_data["ComponentType"]["connectors"]

            for k, v in spec.items():
                encoder_def["Schema"]["Specifications"][k] = \
                        {
                            "type": "null,any",
                            "default": v,
                            "column": f"S:{k}" 
                        }
            for k, v in connectors.items():
                encoder_def["Schema"]["Subcomponents"][k] = \
                        {
                            "type": "null,str",
                            "column": f"C:{k}",
                            "default": "<null>" 
                        }

            #logger.warning(json.dumps(encoder_def, indent=4))

            return encoder_def

        #......................................................................
        
        def create_test_encoder():
            encoder_def = \
            {
                "Encoder Name": f"_AUTO_{part_type_id}_{test_name}",
                "Record Type": "Test",
                "Part Type ID": part_type_id,
                "Part Type Name": part_type_name,
                "Test Name": test_name,
                "Schema": {"Test Results": {}}
            }
            test_node = part_type_data["TestTypeDefs"][test_name]["data"]
            spec = test_node["properties"]["specifications"][0]["datasheet"]
            for k, v in spec.items():
                # the value v normally means the default value, but if it's 
                # a list, it's supposed to mean that the value is supposed
                # to be chosen from the list, not the list itself. So if we
                # see a list, make it a default value of null
                if isinstance(v, list):
                    v = None
                encoder_def["Schema"]["Test Results"][k] = \
                    {
                        "default": v,
                        "column": f"T:{k}"
                    }

            return encoder_def
        
        #......................................................................

        def create_item_image_encoder():
            
            encoder_def = \
            {
                "Encoder Name": f"_AUTO_{part_type_id}_Item_Image",
                "Record Type": "Item Image",
                "Part Type ID": part_type_id,
                "Part Type Name": part_type_name,
                "Schema": {}
            }

            return encoder_def
        
        #......................................................................
        
        def create_test_image_encoder():
           
            if test_name is None:
                raise ValueError("Cannot generate 'Test Image' encoder because "
                            "'Test Name' was not provided.")
 
            encoder_def = \
            {
                "Encoder Name": f"_AUTO_{part_type_id}_Test_Image",
                "Record Type": "Test Image",
                "Part Type ID": part_type_id,
                "Part Type Name": part_type_name,
                "Test Name": test_name,
                "Schema": {}
            }

            return encoder_def
        
        #......................................................................

        if record_type == 'Item':
            return create_item_encoder()
        if record_type == 'Test':
            return create_test_encoder()
        if record_type == 'Item Image':
            return create_item_image_encoder()
        if record_type == 'Test Image':
            return create_test_image_encoder()




        #......................................................................

        #Style.warning.print(json.dumps(part_type_data, indent=4))   

        #}}}

    @staticmethod
    def preserve_order(obj):
        return utils.preserve_order(obj)

    @staticmethod
    def restore_order(obj):
        return utils.restore_order(obj)

    @staticmethod
    def scramble_order(obj):
        return utils.scramble_order(obj)


if __name__ == "__main__":
    pass






















