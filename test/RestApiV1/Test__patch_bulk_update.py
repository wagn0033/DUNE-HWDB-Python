#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__patch_hwitem.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    post_bulk_add()
        (using REST API: POST /api/v1/component-types/{part_type_id}/bulk-add)
    patch_bulk_update() 
        (using REST API: PATCH /api/v1/component-types/{part_type_id}/bulk-update)
    get_component_type()
        (using REST API: /api/v1/component-types/{part_type_id})
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_bulk_add, patch_bulk_update, get_component_type

class Test__patch_bulk_update(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 0x10000
    
    def tearDown(self):
        pass


    def test_patch_bulk_update(self):
        testname = "patch_bulk_update"
        logger.info(f"[TEST {testname}]") 

        try:
            #POST
            ##########
            part_type_id = "Z00100300001"
            data= {
                "comments": "Here are some comments",
                "component_type": {
                    "part_type_id": part_type_id
                },
                "count": 2,
                "country_code": "US",
                "institution": {
                "id": 186
                },
                "manufacturer": {
                    "id": 7
                }
            }

            logger.info(f"Posting bulk components: part_type_id={part_type_id}, ")
            resp = post_bulk_add(part_type_id, data)
            logger.info(f"Response from post: {resp}") 
            self.assertEqual(resp["status"], "OK")

            part_type_id = resp["component_type"]["part_type_id"][0]

            logger.info(f"New component type result: part_type_id={part_type_id}") 

            #PATCH
            ##########
            serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"
            data = {
                    "data": [
                    {
                        "batch": {
                            "id": 0
                        },
                        "comments": "Patched component types",
                        "manufacturer": {
                            "id": 7
                        },
                        "part_id": "Z00100300001",
                        "serial_number": serial_number,
                        "specifications": {
                            "Color": "Blue"
                        }
                    }
                ]
                }
            
            resp = patch_bulk_update(part_type_id, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")

            #GET/CHECK
            ##########
            logger.info(f"getting component type for comparison: part_type_id={part_type_id}")
            
            resp = get_component_type(part_type_id)

            logger.info(f"result: {resp}")
            
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp["data"]["part_type_id"], part_type_id)
            self.assertEqual(resp["data"]["serial_number"], serial_number)



        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")



if __name__ == "__main__":
    unittest.main()
