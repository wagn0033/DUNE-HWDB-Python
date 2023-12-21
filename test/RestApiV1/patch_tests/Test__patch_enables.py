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

from Sisyphus.RestApiV1 import post_hwitem, get_hwitem, patch_enable_item, post_bulk_add, patch_bulk_enable

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

#-----------------------------------------------------------------------------
    


    def test_patch_enable_bulk(self):
        testname = "patch_enable_bulk"
        logger.info(f"[TEST {testname}]")  

        try:
            #POST bulk
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

            part_id1 = resp["data"][0]["part_id"]
            part_id2 = resp["data"][1]["part_id"]

            logger.info(f"New part result: part_id={part_id1, part_id2}") 

            #ENABLE
            
            data = {
                "data": [{
                    "comments": "string",
                    "enabled": True,
                    "part_id": part_id1
                    },
                    {
                    "comments": "string",
                    "enabled": True,
                    "part_id": part_id2
                    }
                ]}
            
            resp = patch_bulk_enable(part_id1, data)
            resp = patch_bulk_enable(part_id2, data)
            logger.info(f"Response from post: {resp}")
            
            
            #GET/CHECK

            resp = get_hwitem(part_id1)
            resp2 = get_hwitem(part_id2)
            self.assertTrue(resp["data"]["enabled"])
            self.assertTrue(resp2["data"]["enabled"])
            logger.info(f"Response from post: {resp}") 


            #DISABLE

            data = {
                "data": [{
                    "comments": "string",
                    "enabled": False,
                    "part_id": part_id1
                    },
                    {
                    "comments": "string",
                    "enabled": False,
                    "part_id": part_id2
                    }
                ]}
            
            resp = patch_bulk_enable(part_id1, data)
            resp = patch_bulk_enable(part_id2, data)
            logger.info(f"Response from post: {resp}")

            #GET/CHECK
            resp = get_hwitem(part_id1)
            resp2 = get_hwitem(part_id2)
            self.assertFalse(resp["data"]["enabled"])
            self.assertFalse(resp2["data"]["enabled"])
            logger.info(f"Response from post: {resp}")

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")
        
    ##############################################################################



if __name__ == "__main__":
    unittest.main()


        


    

