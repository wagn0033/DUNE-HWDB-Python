#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__patch_hwitem.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    post_hwitem()
        (using REST API: POST /api/v1/component-types/{type_id}/components)
    patch_hwitem() 
        (using REST API: PATCH /api/v1/components/{part_id})
    get_hwitem()
        (using REST API: /api/v1/components/{part_id})
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitem, patch_hwitem, get_hwitem

class Test__patch_hwitem(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_patch(self):
        
        logger.info("Testing <patch_hwitem> (V1)")

        # Part 1, post a component
        ##########################
 
        part_type_id = "Z00100300001"
        serial_number = "S99999"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": serial_number,
            "specifications": {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Test: patch component, part 1"
            },
            "subcomponents": {}
        }

        logger.info(f"Posting new hwitem: part_type_id={part_type_id}, "
                    f"serial_number={serial_number}")
        resp = post_hwitem(part_type_id, data)
        logger.info(f"Response from post: {resp}") 
        self.assertEqual(resp["status"], "OK")

        component_id = resp["component_id"]
        part_id = resp["part_id"]

        logger.info(f"New hwitem result: part_id={part_id}, component_id={component_id}") 

        # Part 2, patch it
        ####################

        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"
        
        logger.info(f"Attempting to patch hwitem: part_id={part_id}, "
                    f"serial_number={serial_number}")

        data = {
            "comments": "this component has been patched",
            "manufacturer": {
                "id": 7
            },
            "part_id": part_id,
            "serial_number": serial_number,
            "specifications": {
                "Widget ID": serial_number,
                "Color": "green",
                "Comment": "Unit Test: patch component, part 2"
            },
        }

        resp = patch_hwitem(part_id, data)
        logger.info(f"Response from patch: {resp}")
        self.assertEqual(resp["status"], "OK")

        # Part 3, get it and check that the data has been updated
        ###########################################################

        logger.info(f"getting hwitem for comparison: part_id={part_id}")
        
        resp = get_hwitem(part_id)

        logger.info(f"result: {resp}")
        
        self.assertEqual(resp["status"], "OK")
        self.assertEqual(resp["data"]["part_id"], part_id)
        self.assertEqual(resp["data"]["serial_number"], serial_number)
        self.assertDictEqual(resp["data"]["specifications"][0], data["specifications"])



   
if __name__ == "__main__":
    unittest.main()
