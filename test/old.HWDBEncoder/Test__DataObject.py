#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/HWDBEncoder/Test__DataObject.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest

from Sisyphus.HWDBEncoder.DataObject import *


class Test__encoder(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 0x10000
        logger.info(f"[TEST {self.id()}]")


    def tearDown(self):
        has_error = self._outcome.errors[-1][1] is not None

        if not has_error:
            logger.info(f"[PASS {self.id()}]")
        else:
            logger.error(f"[FAIL {self.id()}]")
    
    #-----------------------------------------------------------------------------
    
    def test_01(self):
        try:

            print("Original Dict:")
            print(orig_dict)
                
            d = DO_Dict.from_dict(orig_dict)

            print(d.to_hwdb())
            print(json.dumps(d.to_hwdb(), indent=4))


        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
    
##############################################################################
 
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
#    "field_4":
#    {
#        ("abc", 1):
#        {
#            "field_4_1": "abc",
#            "field_4_2": 1,
#        },
#        ("cde", 2):
#        {
#            "field_4_1": "cde",
#            "field_4_2": 2,
#        },
#    }
    "field_5":
    {
        "_meta":
        {
            "_index": ["field_5_1"],
        },
        "abc":
        {
            "field_5_1": "abc",
            "field_5_2": 1,
        },
        "cde":
        {
            "field_5_1": "cde",
            "field_5_2": 2,
        },
    },
    "field_6":
    {
        "_meta":
        {
            "_index": False, # unindexed"
        }
        0:
        {
            "field_6_1": "fgh",
        },
        1:
        {
            "field_6_1": "ijk",
        },
    }
}

   
if __name__ == "__main__":
    unittest.main()
