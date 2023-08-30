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

from Sisyphus.RestApiV1 import post_component


class Test__post_component(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_post(self):
        
        logger.info("Testing <post_component> (V1)")
        
        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

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
            "serial_number": serial_number,
            "specifications": 
            {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Test: post component"
            },
            "subcomponents": {}
        }
        resp = post_component(part_type_id, data)

        logger.info(f"The response was: {resp}")
        
        self.assertEqual(resp["status"], "OK")
        #self.assertEqual(resp, expected_resp)
   
if __name__ == "__main__":
    unittest.main()
