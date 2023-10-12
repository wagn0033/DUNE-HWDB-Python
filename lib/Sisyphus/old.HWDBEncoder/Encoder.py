#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBEncoder/Encoder.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

class HWItem:
    pass

class HWItemTest:
    pass

class EncoderFile:
    pass


class Encoder:
    def __init__(self):
        self.encoder_type = None
        self.hw_type_id = None
        self.hw_test_name = None
        self.serial_number_proxy = None
        self.groups = None
        
    
    def load(self, filename):
        pass
    
    def save(self, filename=None):
        pass
    
    def encode(self, dataframe):
        pass

    def decode(self, hw_data_object):
        pass


class Group:
    def __init__(self):
        pass
    
'''
Encoder Format Example
======================
{
    "Encoder Name": "Item-Z001001999999",
    "Encoder Type": "Item", // ["Item" | "Test"]
    "Type ID": "Z00100199999",
    "Test Name": null, // only used if "Encoder Type" is "Test".
                       // (if "Encoder Type" is "Item", then this must either be 
                           omitted or set to null. Anything else is an error.)
    "Grouping":   
    [
        // list of "Group" types
    ],
}

Group Format Example
====================
{
    "Group Name": null, // The first group doesn't need a name
                        // the group name will become the dictionary key used for the 
                        // encoded data, if the data is hierarchical.
    "Key": ['keyname1', 'keyname2'], 
                        // The columns in the spreadsheet that indicate the context of the
                        // data in "Members". If there's only one column, the value is 
                        // allowed to be a single string instead of a list of strings.
    "Lock Keys": true,  // If true, this indicates that all data that belongs to this key
                        // is contained in the same spreadsheet, so if the same key is 
                        // encountered again in a later spreadsheet, the new data will
                        // not be added. The upload processor will display a warning.
    "Members":          // The columns in the spreadsheet that belong at the level indicated
    {                   // by "Key". 
        'keyname1': "string",   // Columns used in "Key" *MUST* be included in Members
        'keyname2': "integer",
        'member1': "float",
    }
}

Member Types
============
Member types may be specified as a string or as a dictionary. If 
"any"      Any value is allowed
"string"   Any value is allowed except null
"integer"  The value must be able to be cast as an integer without causing truncation.
"float"    The value must be able to be cast as a float
"null"     The field must not contain any value (but why would you do this??)
"json"     The value is interpreted as json-encoded data
"list<[subtype]>" The value is a json-encoded list, and every element in the list is [subtype]
"optional<[subtype]>" The value is [subtype] or null





    


'''
