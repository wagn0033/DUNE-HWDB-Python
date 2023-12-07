#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__post_component_types.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_component

class Test__post_component_types(unittest.TestCase):
    
    def test_post_component(self):
        testname = "post_component"
        logger.info(f"[TEST {testname}]")

        try:
            part_type_id = "Z00100300001"
            serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"
            data = {
                "comments": "unit testing",
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
            resp = post_component(part_type_id, data)
            logger.info(f"response was {resp}")
            self.assertEqual(resp["status"], "OK")
        
        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")
   
if __name__ == "__main__":
    unittest.main()

