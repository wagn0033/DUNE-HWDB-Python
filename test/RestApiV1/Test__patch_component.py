#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__post_component.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    Python: get_hwitem_by_part_id(part_id)
    REST API: /api/v1/components/{part_id}
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_component, patch_component


class Test__patch_component(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_patch(self):
        
        logger.info("Testing <patch_component> (V1)")
       

        # Part 1, post a component
        ##########################
 
        part_type_id = "Z00100300001"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": "Z00100300001"
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": "S99999",
            "specifications": {
                "Widget ID": "S99999",
                "Color": "red",
                "Comment": "Unit Test: patch component, part 1"
            },
            "subcomponents": {}
        }
        resp = post_component(part_type_id, data)
        logger.info(f"Response from post: {resp}") 
        self.assertEqual(resp["status"], "OK")

        component_id = resp["component_id"]
        part_id = resp["part_id"]

        # Part 2, patch it
        ####################

        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"
        #part_id = "Z00100300001-00030"

        data = {
            #"batch": {
            #    "id": 0
            #},
            "comments": "this component has been patched",
            "manufacturer": {
                "id": 7
            },
            #"part_id": part_id,
            "part_id": component_id,
            "serial_number": serial_number,
            #"specifications": {
            #    "Widget ID": serial_number,
            #    "Color": "green",
            #    "Comment": "Unit Test: patch component, part 2"
            #},
        }

        resp = patch_component(part_id, data)
        logger.info(f"Response from patch: {resp}")
        self.assertEqual(resp["status"], "OK")
   
if __name__ == "__main__":
    unittest.main()
