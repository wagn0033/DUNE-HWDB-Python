#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests setting "enabled" status in item
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitem
from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus.RestApiV1 import patch_hwitem_enable
from Sisyphus.RestApiV1 import post_hwitems_bulk
from Sisyphus.RestApiV1 import patch_hwitems_enable_bulk

class Test__patch_enables(unittest.TestCase):
    """Tests setting "enabled" status in item"""

    #post a new item, patch it to be enabled, check if it was enabled. 
    # Patch it again to disable it, check it was disabled
    def test__patch_hwitem_enable(self):
        """Tests setting "enabled" status in item"""

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

            resp = patch_hwitem_enable(part_id, data)
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

            resp = patch_hwitem_enable(part_id, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")

            #GET/CHECK
            ##########

            resp = get_hwitem(part_id)
            self.assertFalse(resp["data"]["enabled"])


        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

#-----------------------------------------------------------------------------
    

    #post (2) items in bulk, get part ids from response of post, 
    # use those part ids to enable them, check if they were enabled. 
    # Disable them, check if they were disabled
    def test_patch_enable_bulk(self):
        """Tests setting "enabled" status in several items at the same time"""

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
            resp = post_hwitems_bulk(part_type_id, data)
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
            
            resp = patch_hwitems_enable_bulk(data)
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
            
            resp = patch_hwitems_enable_bulk(data)
            logger.info(f"Response from post: {resp}")

            #GET/CHECK
            resp = get_hwitem(part_id1)
            resp2 = get_hwitem(part_id2)
            self.assertFalse(resp["data"]["enabled"])
            self.assertFalse(resp2["data"]["enabled"])
            logger.info(f"Response from post: {resp}")

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        
    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

        


    

