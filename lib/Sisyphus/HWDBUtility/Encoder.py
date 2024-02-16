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

import pprint
pp = pprint.PrettyPrinter(indent=4)

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

#pp = lambda s: print(json.dumps(s, indent=4))

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
    "External ID": {KW_TYPE:"null,string", KW_COLUMN:"External ID", KW_DEFAULT:None},
    "Serial Number": {KW_TYPE:"null,string", KW_COLUMN:"Serial Number", KW_DEFAULT:None},
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
        "Comments": {KW_TYPE:"string", KW_COLUMN:"Comments", KW_DEFAULT:""}, # SEE NOTE!
        "Enabled": {KW_TYPE:"boolean", KW_COLUMN:"Enabled", KW_DEFAULT:True},
        "Subcomponents": {KW_TYPE:"collection", KW_MEMBERS: {}},
        "Specifications": {KW_TYPE:"datasheet", KW_MEMBERS: {}},
    },
    "Test":
    {
        # for all record types:
        **default_universal_fields,

        # for record_type 'Test' or 'Test Image':
        "Test Name": {KW_TYPE:"null,string", KW_COLUMN:"Test Name", KW_DEFAULT:None},

        # for record type 'Test':
        "Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},
        "Test Results": {KW_TYPE:"datasheet"},
    },
    "Item Image":
    {
        # for all record types:
        **default_universal_fields,

        # for record_type 'Item Image' or 'Test Image':
        "Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},
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
        "Comments": {KW_TYPE:"null,string", KW_COLUMN:"Comments", KW_DEFAULT:None},
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

        self.part_type_name = enc.pop("Part Type Name", None)
        self.part_type_id = enc.pop("Part Type ID", None)
        self.test_name = enc.pop("Test Name", None)

        self.options = enc.pop("Options", {})
        
        self.raw_schema = enc.pop("Schema", {})
        self.schema = self._preprocess_schema(self.raw_schema)


        self.uuid = str(uuid.uuid4()).upper()
        self.__class__._encoder_cache[self.uuid] = self    

        # TODO: more fields

        #}}}
    
    #--------------------------------------------------------------------------
    
    def add_warning(self, warning):
        printcolor(0xffaa33, f"WARNING: {warning}")
        self.warnings.append(warning)
    
    #--------------------------------------------------------------------------

    def _preprocess_schema(self, schema):
        #{{{
        """'Normalize' the schema to make encoding simpler

        * make the entire schema a 'schema' type (essentially, a group), and 
            all schema fields 'members' of this schema/group. The key for this
            schema/group is ('External ID', 'Serial Number')
        * insert the default fields for this record_type, if not already present
        * make all field definitions into dictionaries with the correct fields
            (user's field definitions are allowed to be a string containing the
            type, but convert it to a dict containing 'type'
        * any fields that are of type 'datasheet' (i.e., 'Specifications' and
            'Test Results') or 'collection' ('Subcomponents') should also be
            converted into 'datasheet' or 'collection' groups.
        """
        #......................................................................

        def preprocess_group(sch_in):
            #{{{
            sch_in = deepcopy(sch_in)
            sch_out = {}

            for schema_key, field_def in sch_in.items():
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

                member_def = {**typedef_default, **field_def}

                sch_out[schema_key] = member_def

            return sch_out
            #}}}
        
        #......................................................................
        
        def has_groups(members):
            return (
                isinstance(members, dict)
                and any(
                    isinstance(v, dict) and v.get('type', None) in 
                            ('group', 'collection', 'datasheet', 'schema')
                    for v in members.values())
                )

        #......................................................................

        typedef_default = \
        {
            KW_TYPE: "null,any", 
            KW_COLUMN: None, 
            KW_DEFAULT: None,
        }

        sch_in = deepcopy(schema)
        sch_out = {}

        # Process the root level
        # We can only handle the fields listed in the 'default' schema, because
        # these correspond with what the database can hold for this record type.
        # TODO: Warn if extra fields are found
        # TODO: Create a mechanism to suppress this warning
        
        for schema_key, default_field_def in self.default_schema_fields.items():
        
            #if schema_key == "Serial Number":
            #    breakpoint()

            field_type = default_field_def[KW_TYPE]

            if field_type in ("datasheet", "collection"):
                if schema_key in sch_in:
                    user_field_def = sch_in[schema_key]
                    # If the user provided this (and they should!), we should check
                    # how they provided it. The usual case is that they gave it as
                    # a dictionary of fields, which consists of the "members" of 
                    # this datasheet (which is essentially the same as a group), 
                    # but they should be allowed to provide it in the same form
                    # as we will process it into, so check for 'type' and 'members'.
                    if isinstance(default_field_def, str):
                        # If it's a string instead of a dictionary, then the 
                        # string indicates the type, which is useless for a
                        # datasheet, because then there's no way of listing the
                        # members. But, let's go ahead and give them a datasheet
                        # with no members.
                        sch_out[schema_key] = \
                        {
                            KW_TYPE: field_type,
                            KW_MEMBERS: {},
                        }
                        continue
                    if isinstance(default_field_def, list):
                        # If it's a list, it better be a list of strings, each
                        # of which is a name of a field of type 'any'.
                        assert(all(isinstance(s, str) for s in default_field_def))
                        sch_out[schema_key] = \
                        {
                            KW_TYPE: field_type,
                            KW_MEMBERS: {s:"any" for s in default_field_def},
                        }
                        continue
                    if not isinstance(default_field_def, dict):
                        raise ValueError(f"{field_type} in schema must be a dictionary")

                    if not {KW_TYPE, KW_MEMBERS, KW_KEY}.difference(default_field_def.keys()):
                        # The only fields here, if any at all, are 'type', 
                        # 'members', and 'key', so interpret this as a 
                        # fully-defined field definition and use it as-is. But
                        # the type (if present) has to be the correct field
                        # type, and the key (if present) has to be empty.
                        if user_field_def.get(KW_TYPE, field_type) != field_type:
                            raise ValueError("this schema field must be of type "
                                        f"'{field_type}'")
                        if not user_field_def.get(KW_KEY, None):
                            raise ValueError(f"{field_type} must not have 'key'")
                       
                        members = user_field_def.get(KW_MEMBERS, {})

                        if field_type == "collection":
                            if has_groups(members):
                                raise ValueError(f"{schema_key} may not have any subgroups")   
 
                        sch_out[schema_key] = \
                        {
                            KW_TYPE: field_type,
                            KW_MEMBERS: preprocess_group(members),
                        }
                        continue
                        
                    # None of the above apply.
                    # NOTE: this should be the most common case!
                    # Treat this dictionary as a list of members. (It might
                    # actually include the members 'type', 'members', and 
                    # 'key', as long as there's at least one more field. 
                    # (If something goes wrong because of it, then they get 
                    # what they deserve.) Since one of these members might
                    # be a group, we have to preprocess that node, too.
                    members = user_field_def
                    if field_type == "collection":
                        if has_groups(members):
                            raise ValueError(f"{schema_key} may not have any subgroups")   
                    
                    sch_out[schema_key] = \
                    {
                        KW_TYPE: field_type,
                        KW_MEMBERS: preprocess_group(members),
                    }
                    continue
                
                else:
                    # They didn't provide this field, so we'll just give them
                    # a datasheet with no members.
                    sch_out[schema_key] = default_field_def
                    continue
                logger.warning("This line should be unreachable. A 'continue' "
                        "is missing somewhere.")
                continue
           
            # If we got here, the field_type is just a normal field
            if schema_key in sch_in:
                user_field_def = sch_in[schema_key]
                if type(user_field_def) is str:
                    sch_out[schema_key] = {**default_field_def, KW_TYPE: user_field_def}
                else:
                    sch_out[schema_key] = {**default_field_def, **user_field_def}
                continue           
 
            # Use the default
            sch_out[schema_key] = deepcopy(default_field_def)

        
        # Embed this in a schema type and return
        preprocessed_schema = \
        {
            KW_TYPE: "schema",
            KW_KEY: ["External ID", "Serial Number"],
            KW_MEMBERS: sch_out,
        }

        return preprocessed_schema
        #}}}
    
    #--------------------------------------------------------------------------

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

    #--------------------------------------------------------------------------        

    def deindex(self, record, schema=None):
        #{{{
        """Turn indexed rows back into lists"""

        record = deepcopy(record)
        if schema is None:
            schema = self.schema

        for k, v in record.items():
            for schema_key, field_def in schema[KW_MEMBERS].items():
                if field_def[KW_TYPE] in ("group", "schema", "datasheet", "collection"):
                    v[schema_key] = self.deindex(v[schema_key], field_def)
        
        return list(record.values())
        #}}}

    #-------------------------------------------------------------------------- 

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

    #--------------------------------------------------------------------------

    def merge_records(self, record, addendum, schema=None):
        #{{{
        """Merge two sets of row data"""

        record_indexed = self.index(record, schema)
        addendum_indexed = self.index(addendum, schema)
        return merge_indexed_records(record_indexed, addendum_indexed, schema)
        #}}}

    #--------------------------------------------------------------------------

    def encode_indexed(self, sheet):
        #{{{
        """Encode a spreadsheet using the stored schema using indexed rows"""
        
        #......................................................................

        def encode_group(sheet, row_index, parent_field_def):
           
            group_value = {} 
 
            for schema_key, field_def in parent_field_def[KW_MEMBERS].items():
                
                if field_def[KW_TYPE] in ("group", "schema", "collection", "datasheet"):
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
                
                # TODO: handle warnings
                if field_contents.warnings:
                    Style.info.print(field_contents.datatype)
                    Style.warning.print(field_contents.warnings)

                group_value[schema_key] = field_contents.value
            
            if parent_field_def[KW_TYPE] in ('collection', 'datasheet'):
                key = ()
            else:
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

        return result
        #}}}    

    #--------------------------------------------------------------------------

    def encode(self, sheet):
        #{{{
        """Encode a spreadsheet using the stored schema"""

        encoded_data = self.encode_indexed(sheet)
        deindexed = self.deindex(encoded_data)
        
        return deindexed
        #}}}
    #--------------------------------------------------------------------------

    def decode(self, record):
        #{{{
        
        def make_row_template(schema):
            template = {}
            for schema_key, field_def in schema["members"].items():
                field_type = field_def["type"]

                if field_type == "group":
                    print("GROUP")
                    template.update(make_row_template(field_def))
                elif field_type == "datasheet":
                    print("DATASHEET")
                    template.update(make_row_template(field_def))
                elif field_type == "collection":
                    print("COLLECTION")
                    template.update(make_row_template(field_def))
                elif field_type == "schema":
                    template.update(make_row_template(field_def))
                else:
                    template[schema_key] = field_def

            return template


        template = make_row_template(self.schema)

        def make_rows(record, schema, current_row):
            # Use 'schema' to locate fields in 'record' and put them in 'current_row'
            # when the field type is 'group', recursively call make_rows to get a row
            # for each node in the group.
            #   * the leaf nodes should be the only ones adding rows, so make sure not
            #     to add a row if there's a group at this level
            #   * make sure to add all non-group fields before drilling down into a
            #     group, or all fields won't be picked up
            #   * if there's more than one group, there's no way to drill down into
            #     both simultaneously, so it's not allowed.
            
            next_group_key = None
            for schema_key, field_def in schema["members"].items():
                field_type = field_def[KW_TYPE]
                if field_type in ("group", "datasheet", "schema"):
                    # keep track of this, but process at the end
                    if next_group_key is not None:
                        ValueError("Decode found more than one group at the same level")
                    next_group_key = schema_key
                    continue
                elif field_type in ("collection",):
                    # This is a shallow group, so we can just interate
                    # through it and not have to process it recursively
                    for sub_schema_key, sub_field_def in field_def['members'].items():
                        current_row[sub_schema_key] = record[schema_key][sub_schema_key]
                    continue

                current_row[schema_key] = record[schema_key]

            # If there is a group, process it
            if next_group_key is not None:
                make_rows( 
                        record[next_group_key], 
                        schema['members'][next_group_key], 
                        current_row)        
                return

            rows.append(deepcopy(current_row))

            return


        record = deepcopy(record)
        rows = []
       
        #Style.fg(0x00ffff).print("SCHEMA:", json.dumps(self.schema, indent=4))

        #Style.fg(0xff9900).print("RECORD:", json.dumps(record, indent=4))
 
        current_row = {key: None for key in template}
        #Style.fg(0xff00ff).print("ROW TEMPLATE:", json.dumps(current_row, indent=4))
        
        make_rows(record, self.schema, deepcopy(current_row))
        #Style.fg(0x00ff00).print("ROWS:", json.dumps(rows, indent=4)) 
        
        return rows
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






















