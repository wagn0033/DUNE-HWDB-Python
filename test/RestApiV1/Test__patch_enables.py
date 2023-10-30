#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__patch_hwitem.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    post_hwitem()
        (using REST API: POST /api/v1/component-types/{type_id}/components)
    patch_enable_item()
        (using REST API: /api/v1/components/{part_id}/enable)
    get_hwitem()
        (using REST API: /api/v1/components/{part_id})
    post_bulk_add()
        (using REST API: POST /api/v1/component-types/{part_type_id}/bulk-add)
    patch_bulk_enable()

    get_component_type()
        (using REST API: /api/v1/component-types/{part_type_id})
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitem, get_hwitem, patch_enable_item

class Test__patch_enables(unittest.TestCase):

    def test_patch_enable_item(self):
        testname = "patch_enable_item"
        logger.info(f"[TEST {testname}]")    

        try:
            #POST
            #########

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
                    "Comment": "Unit Testing"
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
        

            #PATCH ENABLE
            #########

            data = {
                "comments": "here are some comments",
                "component": {
                "id": component_id,
                "part_id": part_id
                },
                "enabled": True,
                "geo_loc": {
                "id": 0
                }
            }

            resp = patch_enable_item(part_id, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")
            #self.assertTrue(resp["enabled"])

            #GET/CHECK
            ##########

            resp = get_hwitem(part_id)
            self.assertTrue(resp["data"]["enabled"])

            #PATCH DISABLE
            #########
            
            data = {
                "comments": "here are some comments",
                "component": {
                "id": component_id,
                "part_id": part_id
                },
                "enabled": False,
                "geo_loc": {
                "id": 0
                }
            }

            resp = patch_enable_item(part_id, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")

            #GET/CHECK
            ##########

            resp = get_hwitem(part_id)
            self.assertFalse(resp["data"]["enabled"])


        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")


if __name__ == "__main__":
    unittest.main()


        


    

