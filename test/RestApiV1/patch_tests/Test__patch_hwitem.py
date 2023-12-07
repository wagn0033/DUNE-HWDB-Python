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

from Sisyphus.RestApiV1 import post_hwitem, patch_hwitem, get_hwitem, patch_hwitem_subcomp, patch_enable_item

class Test__patch_hwitem(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 0x10000
    
    def tearDown(self):
        pass

    #-----------------------------------------------------------------------------

    def test_patch_hwitem(self):
        testname = "patch_hwitem"
        logger.info(f"[TEST {testname}]")    

        try:
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
                "subcomponents": {},
                #"enabled": True,
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
                #"enabled": True,
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
            self.assertEqual(resp["data"]["enabled"], False)
            self.assertDictEqual(resp["data"]["specifications"][0], data["specifications"])

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")

  
    #enable sub component, then attach
    def test_patch_hwitem_subcomp(self):
        testname = "patch_hwitem_subcomp"
        logger.info(f"[TEST {testname}]") 

        try:
            

            part_type_id = "Z00100300002"
            serial_number = "S99999"

            data = {
                "comments": "posting for sub comp",
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
                    "DATA": f"serial number:{serial_number}"
                },
                "subcomponents": {}
            }

            resp = post_hwitem(part_type_id, data)
            logger.info(f"Response from post: {resp}") 
            self.assertEqual(resp["status"], "OK")

            #component_id = resp["component_id"]
            part_id_subcomp = resp["part_id"]




            part_id_container = "Z00100300001-00360"

            data = {
                "component": {
                    "part_id": part_id_container
                },
                "subcomponents": {
                    "SubComp 1" : part_id_subcomp,
                }
            }

            resp = patch_hwitem_subcomp(part_id_container, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")
            """
            data = {
                "component": {
                    "part_id": part_id_container
                },
                "subcomponents": {
                    "SubComp 1": None,
                }
            }

            resp = patch_hwitem_subcomp(part_id_container, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")
            """


        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")


if __name__ == "__main__":
    unittest.main()
