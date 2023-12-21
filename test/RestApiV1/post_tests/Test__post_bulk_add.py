#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__patch_hwitem.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    post_bulk_add()
        (using REST API: POST /api/v1/component-types/{part_type_id}/bulk-add)

"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_bulk_add

class Test__post_bulk_add(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 0x10000
    
    def tearDown(self):
        pass


    def test_post_bulk_add(self):
        testname = "post_bulk_add"
        logger.info(f"[TEST {testname}]") 

        try:

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

            part_id = resp["data"][0]["part_id"]

            logger.info(f"New part result: part_id={part_id}") 

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")

    ##############################################################################

if __name__ == "__main__":
    unittest.main()



    
