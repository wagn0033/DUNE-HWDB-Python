#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBEncoder/DataObject.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""


class DO_Dict():
    def __init__(self):
        self.fields = []
        self.keys = []
        self.data = {}

    @classmethod
    def from_dict(cls, data):
        if type(data) != dict:
            raise ValueError("Expected dict")
       
        obj = cls()

        for key, value in data.items():
            obj.fields.append(key)

            if type(value) == dict:
                if "_meta" in data.keys():
                    # this is an indexed list
                    obj.data[key] = None
                else: 
                    # just a "normal" object
                    obj.data[key] = cls.from_dict(value)
            else:
                obj.data[key] = value

        return obj

    def to_hwdb(self):
        obj = {}
        obj["_meta"] = {
            "_column_order": self.fields
        }
        for field in self.fields:
            if type(self.data[field]) == DO_Dict:
                obj[field] = self.data[field].to_hwdb()
            else:
                obj[field] = self.data[field]

        return obj

class DO_IndexedList():
    pass

class DO_List():
    pass



orig_dict = \
{
    "field_1": "value_1",
    "field_2": [1, 2, 3],
    "field_3":
    [
        {
            "field_3_1": "value_2",
            "field_3_2": "value_3",
        },
        {
            "field_3_1": "value_4",
            "field_3_2": "value_5",
        },
    ],
    "field_4":
    {
        ("abc", 1):
        {
            "field_4_1": "abc",
            "field_4_2": 1,
        },    
        ("cde", 2):
        {
            "field_4_1": "cde",
            "field_4_2": 2,
        },    
    }
}





