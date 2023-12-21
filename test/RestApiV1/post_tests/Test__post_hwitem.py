#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__post_component.py
Copyright (c) 2023 Regents of the University of Minnesota
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

from Sisyphus.RestApiV1 import post_hwitem


class Test__post_hwitem(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 0x10000
    def tearDown(self):
        pass

    def test_post_hwitem(self):
        testname = "post_hwitem"
        logger.info(f"[TEST {testname}]")

        try:
            logger.info("Testing <post_component> (V1)")
            
            part_type_id = "Z00100300001"
            serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

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
                "specifications": 
                {
                    "Widget ID": serial_number,
                    "Color": "red",
                    "Comment": "Unit Test: post component"
                },
                "subcomponents": {}
            }

            resp = post_hwitem(part_type_id, data)

            logger.info(f"The response was: {resp}")
            
            self.assertEqual(resp["status"], "OK")
            
        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")
    
    ##############################################################################

if __name__ == "__main__":
    unittest.main()
