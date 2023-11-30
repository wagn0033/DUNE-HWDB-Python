#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bin/upload-docket.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""
import sys
#import json5, json
import json5 as json
import json as classic_json
import os
import socket
import pandas as pd
import argparse
from copy import copy, deepcopy
from glob import glob
import ast
hostname = socket.gethostname()

from Sisyphus import version 
from Sisyphus.Configuration import config
#from Sisyphus.Logging import logging
#logger = logging.getLogger(__name__)
logger = config.getLogger()

from Sisyphus import RestApi as api
from Sisyphus.RestApi.Multi import ItemList

from Sisyphus.RestApi import Lookup
from Sisyphus.Utils.Terminal import Style

def dj(colorfn, obj):
    print(colorfn(classic_json.dumps(obj, indent=4)))
    
def dumptofile(filename, obj):
    with open(os.path.join(filename), "w") as f:
         f.write(classic_json.dumps(obj, indent=4))    
     
#from inspect import currentframe, getframeinfo

#PROJECT_ROOT = config['project_root']
#DATA_ROOT = config['project_data']
#CONFIG_ROOT = os.path.expanduser("~/.sisyphus")
#CONFIG_FILE = os.path.join(CONFIG_ROOT, "config.json")
#CACHE_DATA = os.path.normpath(os.path.join(os.path.dirname(__file__), 'data'))

_META = "_meta"
_LOCKED = "_locked"
_INDEX = "_index"
_COLUMN_ORDER = "_column_order"
_IN_MANIFEST = "_in_manifest"
_IN_DATABASE = "_in_database"
DKW_ITEM_IDENTIFIER = "Item Identifier"
DKW_MEMBERS = "Members"
DKW_TEST_NAME = "Test Name"
DKW_GROUPING = "Grouping"
DKW_KEY = "Key"

style_info = Style()
style_notice = Style.fg("royalblue")
style_warning = Style.fg("goldenrod")
style_error = Style.fg("red")
style_success = Style.fg("green")
style_debug = Style.fg("magenta")


class Docket:
    def __init__(self, filename=None):
        if filename is None:
            logger.error("Filename is required.")
            raise ValueError("Filename is required.")
        self.has_warnings = False
        self.hwitem_key = None
        self._load_docket(filename)
        self._validate_docket()
        
        self._process_docket(scan_only=True)
        
        #print(cyan(classic_json.dumps(self.hwitems, indent=4)))
        
        self.find_existing_hwitems()
        #dumptofile("_debug_after_match.json", self.hwitems)
        #sys.exit()
        
        self._process_docket(tests_only=True)
        #dumptofile("_debug_after_2nd_process.json", self.hwitems)


    def _deindex(self, node):
        if type(node) is list:
            
            new_node = []
            for child in node:
            
                new_node.append(copy(self._deindex(child)))
            return new_node
        elif type(node) is dict:
            if _META in node.keys() and _INDEX in node[_META].keys():

                meta = {_META: True} | node[_META]                

                new_node = [meta]
                #new_node = []
                for key, child in node.items():
                    #if key in ("_deindex", _COLUMN_ORDER):
                    #    continue
                    if key == _META:
                        continue
                    new_node.append(copy(self._deindex(child)))
                
                # TBD TBD TBD remove!
                if not new_node[0].get(_META, False):
                    print("?? lost _meta tag ??")
                    sys.exit() 
                    
                    
                #new_node.insert(0, meta)
                #new_node.append(meta)
                return new_node
            else:
                new_node = {}
                for key, child in node.items():
                    new_node[key] = copy(self._deindex(child))
                    
                return new_node
        else:
            return copy(node)
        
    def _reindex(self, node):
        if type(node) is list:
            if type(node[0]) is dict and _META in node[0].keys():
                meta = node.pop(0)
                meta.pop(_META)
                new_node = {_META: meta}
                group_key = meta[_INDEX]
                for listitem in node:
                    #print(classic_json.dumps(listitem, indent=4))
                    #print(group_key)
                    child_key = tuple(listitem[k] for k in group_key)
                    if len(child_key) == 1:
                        child_key = child_key[0]
                    new_node[child_key] = copy(self._reindex(listitem))
                return new_node
            else:
                new_node = []
                for child in node:
                    new_node.append(child)
                return new_node
        elif type(node) is dict:
            new_node = {}
            for key, child in node.items():
                new_node[key] = copy(self._reindex(child))
            return new_node
        else:
            return copy(node)

    def _lock(self, node):
        if type(node) is list:
            for child in node:
                if type(child) is dict and _META in child.keys() and _LOCKED in child[_META].keys():
                    child[_META][_LOCKED] = True
                else:
                    self._lock(child)
        elif type(node) is dict:
            for key, child in node.items():
                if key == _META and _LOCKED in child.keys():
                    child[_LOCKED] = True
                else:
                    self._lock(child)
        else:
            return

    def find_existing_hwitems(self):
        
        print(style_info("* Searching HW Database for existing HW Items"))
                
        #print(style_debug(set(self.hwitems.keys())))
        
        hwitem_list = ItemList(self.type_id, block=False, serial_numbers = set(self.hwitems.keys()))
        try:
            hwitem_list.wait()
        except ItemList.Abandon:
            print(style_error("There was an error fetching existing items of the given type. If this occurs on DEV,"
                              "it may indicate that older items may have been added in the past that have become "
                              "incompatible with more recent REST API changes. It may be possible to ignore this error."))

        #print(style_debug(hwitem_list.results))
        hwitems_found = 0
        for hwitem in hwitem_list.results:
            hwitem_record = {}
            hwitem_record[_IN_DATABASE] = True
            external_id = hwitem_record["External ID"] = hwitem["part_id"] 
            # hwitem_record["Country"] = country_lookup[hwitem["country_code"]]
            # hwitem_record["Institution"] = inst_lookup[hwitem["institution"]["id"]]
            # hwitem_record["Manufacturer"] = manu_lookup[hwitem["manufacturer"]["id"]]
            hwitem_record["Country"] = Lookup.Country(hwitem["country_code"])
            hwitem_record["Institution"] = Lookup.Institution(hwitem["institution"]["id"])
            #hwitem_record["Manufacturer"] = Lookup.Manufacturer(hwitem["manufacturer"]["id"])
            
            if hwitem["manufacturer"] is not None:
                hwitem_record["Manufacturer"] = Lookup.Manufacturer(hwitem["manufacturer"]["id"])
            else:
                hwitem_record["Manufacturer"] = None
            
            hwitem_record["Serial Number"] = hwitem["serial_number"]
            hwitem_record["Batch ID"] = hwitem["batch"]
            hwitem_record["Specifications"] = hwitem["specifications"][0]
            #print(cyan(classic_json.dumps(hwitem_record, indent=4)))

            hwitem_id = hwitem_record["Serial Number"] 
            
            if hwitem_id in self.hwitems.keys():
                print(style_info(f"    found {self.hwitem_key} \"{hwitem_id}\" (External ID = {external_id})"))
                hwitems_found += 1
                
            if hwitem_id in self.hwitems.keys() and self.hwitems[hwitem_id][_IN_MANIFEST]:
                dumptofile(os.path.join(self.docketdir, hwitem_id.replace("/","_")+".json"), self.hwitems[hwitem_id])
                self.hwitems[hwitem_id][_IN_DATABASE] = True
                self.hwitems[hwitem_id]["External ID"] = external_id 
                #print(self.hwitems[hwitem_id])
                
                hwitem_manifest = copy(self.hwitems[hwitem_id])
                #print(hwitem_manifest)
                hwitem_manifest["Country"] = Lookup.Country(hwitem_manifest["Country"])
                hwitem_manifest["Institution"] = Lookup.Institution(hwitem_manifest["Institution"]) 
                hwitem_manifest["Manufacturer"] = Lookup.Manufacturer(hwitem_manifest["Manufacturer"]) 
                
                #print(list(hwitem_record.keys()))
                #print(list(hwitem_manifest.keys()))
                
                for key in hwitem_record:
                    if key.startswith("_"):
                        continue
                    if key == "External ID" and hwitem_manifest[key] is None:
                        continue
                    if key == "Specifications":
                        # TBD: might need some special way of comparing, given _meta tags
                        continue
                    
                    if hwitem_manifest[key] != hwitem_record[key]:
                        self.has_warnings = True
                        print(style_warning(f"warning: for HW Item '{hwitem_id}', '{key}' is not the same as in the HWDB."))
                        print(style_warning(f"    manifest: {hwitem_manifest[key]}, hwdb: {hwitem_record[key]}"))
                        print(style_warning("    The HW Item cannot be updated through this utility."))
                
            if hwitem_id in self.hwitems:
                hwitem_manifest = self.hwitems[hwitem_id]
                if "Tests" in hwitem_manifest.keys():
                    #print(f"Tests: {hwitem_manifest['Tests']}")
                    for test_name in hwitem_manifest['Tests'].keys():
                        resp = api.get_test(external_id, test_name)
                    if resp["status"] != "OK":
                        msg = f"Error: An error occurred while searching for existing test data for {hwitem_id} " \
                                  f"test '{test_name}'"
                        logger.error(msg)
                        print(style_error(msg))
                        raise Exception(msg)
                    elif len(resp["data"]) > 0:
                        print(style_notice(f"    {hwitem_id} has an existing test '{test_name}' and will need to be merged."))
                        self.hwitems[hwitem_id]["Tests"][test_name] = self._reindex(resp["data"][0]["test_data"])
                        #print(magenta("Existing test data:"))
                        #dj(magenta, resp["data"][0]["test_data"])
            #print(style_debug(f"{external_id}"))
            self.hwitems[hwitem_id]["External ID"] = external_id
            self.hwitems[hwitem_id][_IN_DATABASE] = True
        result_ids = [x["serial_number"] for x in hwitem_list.results]
        
        #print(style_debug(self.hwitems.items()))
        for hwitem_id, hwitem in self.hwitems.items():
            if hwitem_id in result_ids:
                continue
            print(style_info(f"    {self.hwitem_key} \"{hwitem_id}\" is new."))
            
            if hwitem.get('Tests', None) is not None:
                print(style_info(f"    {self.hwitem_key} \"{hwitem_id}\" has tests: {list(hwitem['Tests'].keys())}."))
             
            if not hwitem.get(_IN_MANIFEST, False):
                msg = (f"Error: Tests were found for {self.hwitem_key} \"{hwitem_id}\", but the HW Item "
                       "is not in the docket.")
                logger.error(msg)
                print(style_error(msg))
                sys.exit(1)
                
        # print(cyan(classic_json.dumps(self.hwitems, indent=4)))

        # sys.exit()

        
    def upload(self):
        
        SIMULATE_ONLY = False
        
        print()
        
        #print(style_notice("self.hwitems just before upload:"))
        #dj(style_warning, self.hwitems)
        
        for hwitem_id, hwitem in self.hwitems.items():
            
            external_id = None
            
            if hwitem.get(_IN_MANIFEST, False) and not hwitem.get(_IN_DATABASE, False):
            
                new_component = \
                    {
                        "component_type": 
                        {
                            "part_type_id": self.type_id,
                        },
                        "country_code": Lookup.Country(hwitem["Country"]),
                        "institution": 
                        {
                            "id": Lookup.Institution(hwitem["Institution"])
                        },
                        "manufacturer": 
                        {
                            "id": Lookup.Manufacturer(hwitem["Manufacturer"])
                        },
                        "serial_number": hwitem.get("Serial Number", None),
                        "batch_id": hwitem.get("Batch ID", None),
                        "specifications": hwitem["Specifications"]
                    }
                       
                
                if SIMULATE_ONLY:
                    resp = {"part_id": "<simulated>"}
                    success = True
                else:
                    resp = api.post_component(self.type_id, new_component)
                    success = resp["status"] == "OK"
    
    
                if success:
                    external_id = resp["part_id"]
                    print(style_success(f"Item {hwitem_id} was added successfully and assigned external id {external_id}"))
                else:
                    print(style_error(f"Item {hwitem_id} failed to upload."))
                    
                    print(style_error("The message from the REST API is as follows:"))
                    print(style_error(classic_json.dumps(resp, indent=4)))
                    
                    
                    #print(classic_json.dumps(resp, indent=4))
                    external_id = None
                    continue
            
            else:
                if hwitem.get(_IN_DATABASE, False):
                    external_id = hwitem["External ID"]
                    print(style_success(f"Item {hwitem_id} ({external_id}) already exists and doesn't need to be added."))
                else:
                    msg = "Internal error. I don't even know how this would happen."
                    print(style_error(msg))
                    logger.error(msg)
                    raise Exception(msg)
            
            
            for test_name, test_contents in hwitem.get("Tests", {}).items():
                
                test_payload = {
                        "test_type": test_name,
                        "test_data": test_contents,
                        "comments": "added by upload-docket.py",
                        "update": False,
                    }
                
                if SIMULATE_ONLY:
                    success = True
                else:
                    resp = api.post_test(external_id, test_payload)
                    success = resp["status"] == "OK"

                if success:
                    print(style_success(f"Test '{test_name}' for {hwitem_id} ({external_id}) was added successfully"))
                else:
                    print(style_error(f"Test '{test_name}' for {hwitem_id} ({external_id}) failed to upload"))
                    print(style_error("The message from the REST API is as follows:"))
                    print(style_error(classic_json.dumps(resp, indent=4)))
                        
                #print(classic_json.dumps(test_payload, indent=4))
                #print(style_notice("***Payload:"))
                #dj(style_notice, test_payload) 
                    
                    
        print()        
        
    def _process_source(self, source, scan_only=False, tests_only=False):
       
        empty_hwitem = {
            _IN_MANIFEST: False,
            "External ID": None,
            "Country": None,
            "Institution": None,
            "Manufacturer": None,
            "Serial Number": None,
            "Batch ID": None,
            "Specifications": {}
        }
        
        data = source["data"]
        data = data.convert_dtypes()
        encoder = source["encoder"]
        
        if DKW_TEST_NAME in encoder.keys():
            source_type = "Test"
            test_name = encoder[DKW_TEST_NAME]
        else:
            source_type = "Item"
            if tests_only:
                return

        lockouts = {}            
        
        # Give status message to user about what's being processed.
        source_def = source['definition']
        if 'Sheet' in source_def.keys():
            source_data = f"\"{os.path.basename(source['file'])}\":\"{source_def['Sheet']}\""
            source_data = f"Sheet \"{source_def['Sheet']}\" from \"{os.path.basename(source['file'])}\""
        else:
            source_data = f"\"{os.path.basename(source['file'])}\""
        
        if 'Encoder Source' in source_def.keys():
            source_encoder = f"\"{source_def['Encoder Name']}\" from \"{os.path.basename(source_def['Encoder Source'])}\""
        else:
            source_encoder = f"\"{source_def['Encoder Name']}\""
        
        if scan_only and source_type == "Item":
            print(style_info(f"* Processing HW Items from {source_data}")) 
            print(style_info(f"    using encoder {source_encoder}"))
        elif tests_only and source_type == "Test":
            print(style_info(f"* Processing Tests from {source_data}")) 
            print(style_info(f"    using encoder {source_encoder}"))
        elif scan_only and source_type == "Test":
            print(style_info(f"* Scanning {source_data} for HW Items"))
            
        hwitems = self.hwitems = getattr(self, "hwitems", {})

        columns = list(data.columns)
        
        df1 = json.loads(data.transpose().to_json())
        df = list(df1.values())
        
        #print(classic_json.dumps(df, indent=4))
        self.hwitem_key = hwitem_key = encoder[DKW_ITEM_IDENTIFIER]
        self.hwitem_key = hwitem_key
        
        hwitems_found = set()
        prev_keys = None  # place to save keys from previous rows in case the sheet has
                          # rows that are blank up until a thing that changes
        
        # process all rows
        for row_index, row_data in enumerate(df):
            #print(row_data)     
            row = copy(row_data)
            
            if row[hwitem_key] is None:
                if prev_keys is None:
                    msg = f"File {source['file']}, row {row_index}: does not contain {hwitem_key}"
                    logger.error(msg)
                    print(style_error(msg))
                    raise Exception(msg)
                else:
                    hwitem_id = prev_keys[0]
                skip_fields = True
                #skip_set_at = getframeinfo(currentframe()).lineno
            else:
                hwitem_id = row[hwitem_key]
                prev_keys = [hwitem_id]
                skip_fields = False
                #skip_set_at = getframeinfo(currentframe()).lineno
            
            if hwitem_id not in hwitems_found:
                hwitems_found.add(hwitem_id)
                #print(f"Adding {hwitem_key} {hwitem_id}") 
            
            # Get the hwitem node if it exists, create it if it doesn't.
            hwitem = hwitems[hwitem_id] = hwitems.get(hwitem_id, deepcopy(empty_hwitem))
            #print(style_notice(f"row {row_index}, hwitem_id {hwitem_id}"))
            
            # Generate the appropriate structures
            if source_type == "Item":
                hwitem[_IN_MANIFEST] = True
                # Populate hwitem fields, unless this is a blank-for-repeat row
                if row[hwitem_key] is not None:
                    #print(cyan(f"row {row_index} has an item key"))
                    for k in hwitem.keys():
                        if k in columns:
                            hwitem[k] = row[k]
                root_node = hwitem["Specifications"] = hwitem.get("Specifications", {})
            else:
                hwitem[_IN_MANIFEST] |= False
                tests_node = hwitem["Tests"] = hwitem.get("Tests", {})
                test_node = tests_node[test_name] = tests_node.get(test_name, {})
                root_node = test_node
            
            # If we're only doing a quick scan (to see what's there and if we need to merge),
            # bail out here. Keep going if it's an item, though, so we can see if the item or
            # its specs have changed (which may be TBD)
            if scan_only and source_type == "Test":
                continue
            
            parent_group = root_node
            
            
            
            # Drill through the "grouping" rules to create substructures
            for group_index, group_rule in enumerate(encoder[DKW_GROUPING]):
                                          
                if group_index == 0:
                    group_name = "Specifications"
                    children = parent_group
                    children[_META] = {
                        #_INDEX: group_rule.get(DKW_KEY, None),
                        _COLUMN_ORDER: list(group_rule.get(DKW_MEMBERS, {}).keys()),
                        #"_source": (source["file"], row_index)
                    }
                    
                    #children["_rows"] = children.get("_rows", [])
                    #children["_rows"].append([row_index, skip_fields, skip_set_at])
                    group_key = None
                    child_key = None
                    child_group = parent_group
                    
                else:
                    group_name = group_rule.get("Name", "<Main>")
                    children = parent_group[group_name] = parent_group.get(group_name, {})
                    
                    #print(source_type)
                    #print(classic_json.dumps(children, indent=4))
                    children[_META] = children.get(_META, 
                        {
                            _INDEX: group_rule.get(DKW_KEY, None),
                            _COLUMN_ORDER: list(group_rule.get(DKW_MEMBERS, {}).keys()),
                            #"_source": (source["file"], row_index)
                        })
                    
                    if group_rule.get(DKW_KEY, None) is not None:
                        
                        if type(group_rule[DKW_KEY]) is str:
                            group_key = (group_rule[DKW_KEY],)
                        else:
                            group_key = tuple(group_rule[DKW_KEY])

                        child_key = tuple(row[k] for k in group_key)
                        
                        is_blank_row = all([x is None for x in child_key])

                        if len(group_key) == 1:
                            group_key = group_key[0]
                            child_key = child_key[0]

                        if is_blank_row:                        
                            child_key = prev_keys[group_index]
                            skip_fields = True
                        else:
                            prev_keys = prev_keys[:group_index] + [child_key]
                            skip_fields = False
                    else:
                        child_key = row_index
                        
                    #child_group = children[hash(child_key)] = children.get(hash(child_key), {})
                    child_group = children[child_key] = children.get(child_key, {})
                
                #print(row_index, group_index, skip_fields, skip_set_at)
                
                if _META in child_group.keys():
                    if child_group[_META].get(_LOCKED, False):
                        
                        lockout_key = tuple(prev_keys)
                        if lockout_key in lockouts.keys():
                            lockouts[lockout_key]["count"] += 1
                        else:
                            lockouts[lockout_key] = (
                                {
                                    "first": row_index,
                                    "count": 1
                                })
                        
                        #print(style_warning(f"row {row_index} locked out of key {prev_keys}"))
                        break
                elif group_rule.get("Lock Keys", False):            
                    child_group[_META] = (
                        {
                            _LOCKED: False
                            #"_source": (source["file"], row_index)
                        })
                
                if not skip_fields:
                    
                    for field, field_rules in group_rule[DKW_MEMBERS].items():
                        if type(field_rules) is dict and "value" in field_rules.keys():
                            #print(style_error(f"const {field}"))
                            child_group[field] = field_rules["value"]
                        elif type(field_rules) is str and field_rules.startswith("list"):
                            child_group[field] = ast.literal_eval(row[field])
                        else:
                            
                            try:
                                child_group[field] = row[field]
                            except Exception:
                                print(f"child_group: {child_group}")
                                print(f"field: {field}")
                                print(f"row: {row}")
                                raise
                else:
                    pass
                
                parent_group = child_group
        
        if len(lockouts) > 0:
            for lockout_key, lockout_info in lockouts.items():
                self.has_warnings = True
                print(style_warning(f"    Warning: Locked key {lockout_key}\n"
                             f"        has excluded {lockout_info['count']}" 
                             f" rows, starting at row {lockout_info['first']}"))
        
        ###
        # We're done with all rows, so it's time to lock.
        self.hwitems = hwitems
        self._lock(self.hwitems)
        
    def _process_docket(self, scan_only=False, tests_only=False):
        
        self.hwitems = getattr(self, "hwitems", {})
        #self.tests = {}
        
        for source in self.sources:
            self._process_source(source, scan_only, tests_only)
         
         
        if scan_only:
            return
        
        self.hwitems = self._deindex(self.hwitems)
        
        print(style_info("* Writing item-receipt.json"))
        #with open(os.path.join(self.docketdir, "_debug_preprocessed_item-receipt.json"), "w") as f:
        #     f.write(classic_json.dumps(self.hwitems, indent=4))    
        
        with open(os.path.join(self.docketdir, "item-receipt.json"), "w") as f:
             f.write(classic_json.dumps(self.hwitems, indent=4))    
        
        
        #reindexed = self._reindex(self.hwitems)
        #with open(os.path.join(self.docketdir, "_debug_reconstructed_item-receipt.json"), "w") as f:
        #     f.write(classic_json.dumps(reindexed, indent=4))    
        
        
        # self._process_source(self.sources[0])
        # self._process_source(self.sources[1])
        # for hwitem in self.hwitems.values():
        #     hwitem["Specifications"] = list(hwitem["Specifications"].values())[0]
        
        #self._process_source(self.sources[2])
        #self._process_source(self.sources[3])
        
        #print(self.tests)
        
        # def process_node(node):
        #     if type(node) is list:
                
        #         new_node = []
        #         for child in node:
                
        #             new_node.append(process_node(child))
        #         return new_node
        #     elif type(node) is dict:
        #         if _META in node.keys():
                                   
        #             new_node = [node[_META]]
        #             #new_node = []
        #             for key, child in node.items():
        #                 #if key in ("_deindex", _COLUMN_ORDER):
        #                 #    continue
        #                 if key == _META:
        #                     continue
        #                 new_node.append(process_node(child))
                    
        #             #new_node.insert(0, meta)
        #             #new_node.append(meta)
        #             return new_node
        #         else:
        #             new_node = {}
        #             for key, child in node.items():
        #                 new_node[key] = process_node(child)
                        
        #             return new_node
        #     else:
        #         return node
            
            
        
        
        # def finalize_hwitems():
        #     hwitems = self.hwitems
        #     hwitems = process_node(hwitems)
        #     for key, hwitem in hwitems.items():
                
        #         #spec_key = list(hwitem["Specifications"].keys())[-1]
        #         #hwitem["Specifications"] = hwitem["Specifications"][spec_key]
        #         hwitem["Specifications"] = hwitem["Specifications"][-1]
        #     self.hwitems = hwitems
            
            
        # def finalize_tests():
        #     tests = process_node(self.tests)
            
        #     #self.tests = tests
        #     #return
            
            
        #     new_tests = {}
            
        #     for test_name, alt_id_tests in tests.items():
        #         for alt_id, test_contents in alt_id_tests.items():
        #             #print(alt_id, test_name)
        #             if alt_id not in new_tests.keys():
        #                 new_tests[alt_id] = {}
        #             #node_key = list(test_contents["<Main>"].keys())[-1]
        #             #new_tests[alt_id][test_name] = test_contents["<Main>"][node_key]
        #             new_tests[alt_id][test_name] = test_contents["<Main>"][-1]
            
        #     self.tests = new_tests
        
        # with open(os.path.join(self.docketdir, "_debug_preprocessed_item-receipt.json"), "w") as f:
        #     f.write(classic_json.dumps(self.hwitems, indent=4))
        
        # #with open(os.path.join(self.docketdir, "_debug_preprocessed_test-receipt.json"), "w") as f:
        # #    f.write(classic_json.dumps(self.tests, indent=4))
        
        # return
        # finalize_hwitems()
        # finalize_tests()
        
        # with open(os.path.join(self.docketdir, "item-receipt.json"), "w") as f:
        #     f.write(classic_json.dumps(self.hwitems, indent=4))
        
        # with open(os.path.join(self.docketdir, "test-receipt.json"), "w") as f:
        #     f.write(classic_json.dumps(self.tests, indent=4))
        
        # #self.find_existing_items()
        # with open(os.path.join(self.docketdir, "test-merge-receipt.json"), "w") as f:
        #     f.write(classic_json.dumps(self.existing_tests, indent=4))
        

    def _validate_docket(self):
        def validate_typeid():
            if "Type ID" not in self.contents.keys():
                msg = "Docket file must contain 'Type ID'"
                logger.error(msg)
                print(style_error(msg))
                raise Exception(msg)
            self.type_id = self.contents["Type ID"]
            
            resp = api.get_component_type(self.type_id, timeout=5)
            
            if resp["status"] == "ERROR":
                if resp.get("data", "").startswith("No such component type"):
                    msg = f"Component Type ID {self.type_id} was not found in the HWDB"
                    logger.error(msg)
                    print(style_error(msg))
                    raise Exception(msg)
                elif "No required SSL certificate was sent" in resp.get("addl_info", "{}").get("response", ""):
                    msg = "The HWDB requires an SSL certificate."
                    logger.error(msg)
                    print(style_error(msg))
                    raise Exception(msg)
                else:
                    msg = "Application encountered an error connecting to the HWDB. Check log for details."
                    logger.error(msg)
                    #logger.error(resp)
                    print(style_error(msg))
                    raise Exception(msg)

            #print("DATA", resp["data"])
            #print("PROP", resp["data"]["properties"])
            #print("SPEC", resp["data"]["properties"]["specifications"])


            # TBD: should we validate the datasheet?
            #self.hwitem_datasheet = resp["data"]["properties"]["specifications"][0]["datasheet"]
            self.available_manufacturers = resp["data"]["manufacturers"]
        
        def validate_sources():
            
            # Check for 'Sources'
            if "Sources" not in self.contents.keys():
                msg = "Docket file must contain 'Sources'"
                logger.error(msg)
                print(style_error(msg))
                raise Exception(msg)    
            self.sources = []
            
            # # Check for 'Encoders'
            # if "Encoders" not in self.contents.keys():
            #     msg = "Docket file must contain 'Encoders'"
            #     logger.error(msg)
            #     print(style_error(msg))
            #     raise Exception(msg)    

            
            self.encoder_sources = {"<local>": self.contents.get("Encoders", {})}
            
            
            for source_node in self.contents["Sources"]:
                filename = source_node["File"] #TBD: check if node exists first
                
                # Try to find the file
                candidates = [
                        #filename,
                        os.path.join(self.docketdir, filename),
                        #os.path.join(os.path.abspath(os.curdir), filename)
                    ]
                fileresults = []
                for name in candidates:
                    globbed = glob(name)
                    for globname in globbed:
                        if os.path.isfile(globname):
                            fileresults.append(globname)
                            
                if len(fileresults) == 0:
                    msg = f"Cannot locate {filename}, or {filename} is not a file." 
                    logger.error(msg)
                    print(style_error(msg))
                    raise Exception(msg)
                
                #print(cyan(fileresults))
                
                for fullname in fileresults:
                    # Try to read the file
                    data = None
                    try:
                        if fullname.endswith(".xlsx") or fullname.endswith(".ods"):
                            sheet = source_node.get("Sheet", 0)
                            data = pd.read_excel(fullname, sheet_name=sheet)
                        else: # assume it's a csv file
                            data = pd.read_csv(fullname)
                    except Exception:
                        msg = f"Could not read {fullname}"
                        logger.error(msg)
                        print(style_error(msg))
                        raise Exception(msg)
    
                    # Locate the encoding
                    # TBD: future: default encoding?
                    
                    #print(cyan(f"locating encoder for {fullname}"))
                    
                    if "Encoder Source" in source_node.keys():
                        encoder_source_filename = source_node["Encoder Source"]
                        
                        
                        if encoder_source_filename in self.encoder_sources.keys():
                            current_encoder_source = self.encoder_sources[encoder_source_filename]
                        else:
                            try:
                                with open(os.path.join(self.docketdir, encoder_source_filename), "r") as fp:
                                    contents = fp.read()
                                self.curdir = os.path.dirname(os.path.abspath(filename))
                            except Exception:
                                msg = f"Could not open file {encoder_source_filename}"
                                logger.error(msg)
                                print(style_error(msg))
                                raise
                            try:
                                external_docket = json.loads(contents)
                            except Exception:
                                msg = f"{encoder_source_filename} is not valid JSON format."
                                logger.error(msg)
                                print(style_error(msg))
                                raise
                            if "Encoders" not in external_docket.keys():
                                msg = f"External docket '{encoder_source_filename}' does not contain 'Encoders'"
                                logger.error(msg)
                                print(style_error(msg))
                                raise Exception(msg)
                            else:
                                self.encoder_sources[encoder_source_filename] = external_docket["Encoders"]
                                current_encoder_source = self.encoder_sources[encoder_source_filename]
                    else:
                        current_encoder_source = self.encoder_sources["<local>"]
                        encoder_source_filename = "<local>"
                        
                    if "Encoder Name" not in source_node.keys():
                        msg = "Each source must specify 'Encoder Name'"
                        logger.error(msg)
                        print(style_error(msg))
                        raise Exception(msg)
                    
                    matches = [x for x in current_encoder_source if x['Encoder Name'] == source_node["Encoder Name"]]
                    if len(matches) == 0:
                        if encoder_source_filename == "<local>":
                            msg = f"Encoder Name '{source_node['Encoder Name']}' not found."
                        else:
                            msg = (f"Encoder Name '{source_node['Encoder Name']}' not found in external "
                                f"Encoder Source '{encoder_source_filename}'")
                        logger.error(msg)
                        print(style_error(msg))
                        raise Exception(msg)
                    elif len(matches) > 1:
                        if encoder_source_filename == "<local>":
                            msg = f"More than one Encoder Name '{source_node['Encoder Name']}' was found."
                        else:
                            msg = (f"More than one Encoder Name '{source_node['Encoder Name']}' was found."
                                   f"in Encoder Source '{encoder_source_filename}'")
                        logger.error(msg)
                        print(style_error(msg))
                        raise Exception(msg)
                    encoder = matches[0]
                    
                    #print(cyan(f"using encoder {encoder_source_filename}"))
                    
                    self.sources.append(
                        {
                            "definition": source_node,
                            "file": fullname,
                            "data": data,
                            "encoder": encoder
                        })
                    
            #print(list(self.sources[0].keys()))
            #sys.exit()


        validate_typeid()
        validate_sources()
        
    def _load_docket(self, filename):
        try:
            with open(filename, "r") as fp:
                contents = fp.read()
            self.docketdir = os.path.dirname(os.path.abspath(filename))
            #self.curdir = os.path.abspath(os.path.curdir)
        except Exception:
            msg = f"Could not open file {filename}"
            logger.error(msg)
            print(style_error(msg))
            raise

        try:
            self.contents = json.loads(contents)
        except Exception:
            msg = f"{filename} is not valid JSON format."
            logger.error(msg)
            print(style_error(msg))
            raise

def parse_args():
    
    description = "TBD"
    
    arg_table = [
        (('docket',), {"metavar": "filename", "nargs": 1}),  
        #(('--docket',), {"dest": "docket", "required": True, "metavar": "filename"}),
        (('--submit',), {"dest": "submit", "action": "store_true"}),
        (('--ignore-warnings',), {"dest": "ignore", "action": "store_true"}),
    ]
    
    parser = argparse.ArgumentParser(description=description)
    
    for args, kwargs in arg_table:
        parser.add_argument(*args, **kwargs)
    args = parser.parse_args()
    return args

def main():
    print(style_warning(f"HWDB Upload Docket Tool version {version}"))

    args = parse_args()
    
    docket = Docket(args.docket[0])  
    
    if args.submit:
        if docket.has_warnings and not args.ignore:
            print("\nThere were warnings during processing of the docket. Use \n"
                  "--submit --ignore-warnings to submit despite these warnings.")
        else:
            print(style_info("* Submitting requests to HWDB"))
            docket.upload()
    else:
        print("\nThe docket has been processed but not submitted. Use --submit \n"
              "to add the items and/or tests to the database. You may review \n"
              "the processed contents in item-receipt.json.")

if __name__ == "__main__":
    sys.exit(main())

'''
flow:
    validate docket
    pick out item ids
    check for existing data
    process docket (w/ merge)
    upload data








'''
