#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors:
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests updating an item
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

from Sisyphus.Utils.UnitTest import LoggedTestCase

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitem
from Sisyphus.RestApiV1 import patch_hwitem
from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus.RestApiV1 import patch_hwitem_subcomp
from Sisyphus.RestApiV1 import patch_hwitem_enable

class Test__patch_hwitem(LoggedTestCase):
    """Tests updating an item"""
    
    #-----------------------------------------------------------------------------

    #post new item, retrieve part id from post response, patch them item using 
    # part id, check if it was patched by checking the structure
    def test_patch_hwitem(self):
        """Tests updating an item

        Creates a new item, patches it, and retrieves it to compare with
        submitted data.
        """

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
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    #----------------------------------------------------------------------------- 
    
    #post an item under the part type id will be the subcomponent, 
    # retrieve part id and enable it. Patch the container item with the 
    # subcomponent , check status. Patch the container to remove subcomponent, 
    # check status
    def test_patch_hwitem_subcomp(self):
        """Set subcomponents for an item

        This test involves several steps. See source code for details.
        """

        try:
            
            #posting new item under Test Type 002
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
                        "Color":"Red"
                },
                "subcomponents": {}
            }

            resp = post_hwitem(part_type_id, data)
            logger.info(f"Response from post: {resp}") 
            self.assertEqual(resp["status"], "OK")

            part_id_subcomp = resp["part_id"]

            #patching to enable : True
            data = {
                "comments": "here are some comments",
                "component": {
                "part_id": part_id_subcomp
                },
                "enabled": True,
                "geo_loc": {
                "id": 0
                }
            }

            resp = patch_hwitem_enable(part_id_subcomp, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")


            #linking subcomponent to container
            part_id_container = "Z00100300001-00360"

            data = {
                "component": {
                    "part_id": part_id_container
                },
                "subcomponents": {
                    "Subcomp 1" : part_id_subcomp,
                }
            }

            resp = patch_hwitem_subcomp(part_id_container, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")
            
            #removing subcomponent from container
            data = {
                "component": {
                    "part_id": part_id_container
                },
                "subcomponents": {
                    "Subcomp 1": None,
                }
            }

            resp = patch_hwitem_subcomp(part_id_container, data)
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)
