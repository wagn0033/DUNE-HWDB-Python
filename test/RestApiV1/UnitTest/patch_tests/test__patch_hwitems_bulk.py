#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors:
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Test bulk update of items
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.Utils.UnitTest import LoggedTestCase

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitems_bulk
from Sisyphus.RestApiV1 import patch_hwitems_bulk
from Sisyphus.RestApiV1 import get_hwitem

class Test__patch_hwitems_bulk(LoggedTestCase):
    """Test bulk update of items"""

    def test_patch_hwitems_bulk(self):
        """Test bulk update of items

        Posts a bulk-add of items, changes them through bulk-update,
        then retrieves the items from the database for comparison.
        """

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
            resp = post_hwitems_bulk(part_type_id, data)
            logger.info(f"Response from post: {resp}") 
            self.assertEqual(resp["status"], "OK")

            part_id1 = resp["data"][0]["part_id"]
            part_id2 = resp["data"][1]["part_id"]

            logger.info(f"New component type result: part_id={part_id1}") 
            logger.info(f"New component type result: part_id={part_id2}")

            #PATCH
            ##########
            serial_number1 = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"
            serial_number2 = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"
            data = \
            {
                "data": 
                [
                    {
                        #"batch": {
                        #    "id": 0
                        #},
                        "comments": "Patched component types",
                        "manufacturer": {
                            "id": 7
                        },
                        "part_id": part_id1,
                        "serial_number": serial_number1,
                        "specifications": {
                            "Color": "Blue"
                        }
                    },
                    {
                        #"batch": {
                        #    "id": 0
                        #},
                        "comments": "Patched component types",
                        "manufacturer": {
                            "id": 7
                        },
                        "part_id": part_id2,
                        "serial_number": serial_number2,
                        "specifications": {
                            "Color": "Red"
                        }
                    }
                ]
            }
            
            logger.info(f"Patching bulk components: {part_id1}, {part_id2}")
            resp = patch_hwitems_bulk(part_type_id, data)
        
            logger.info(f"Response from patch: {resp}")
            self.assertEqual(resp["status"], "OK")
            
            #GET/CHECK
            ##########
            logger.info(f"getting component type for comparison: part_type_id={part_type_id}")
            
            resp = get_hwitem(part_id1)

            logger.info(f"result: {resp}")
            
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp["data"]["part_id"], part_id1)
            self.assertEqual(resp["data"]["serial_number"], serial_number1)

            resp = get_hwitem(part_id2)

            logger.info(f"result: {resp}")
            
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp["data"]["part_id"], part_id2)
            self.assertEqual(resp["data"]["serial_number"], serial_number2)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

