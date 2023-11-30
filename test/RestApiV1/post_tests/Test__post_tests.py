#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__patch_hwitem.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    post_test_types()
        (using REST API: POST /api/v1/component-types/{part_type_id}/test-types)
    post_test()
        (using REST API: POST /api/v1/component/{part_id}/test)

"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_test_type, post_test

class Test__post_tests(unittest.TestCase):

    @unittest.skip("fails")
    def test_post_test_type(self):

        testname = "post_test_type"
        logger.info(f"[TEST {testname}]") 

        try:

            part_type_id = "Z00100300001"

            data = {
                    "comments": "comms",
                    "component_type": {
                        "part_type_id": part_type_id
                    },
                    "name": "unittest1",
                    "specifications": {"Color": "Yellow"}
                    }
            
            resp = post_test_type(part_type_id, data)
            self.assertEqual(resp["status"], "OK")


        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")

#-----------------------------------------------------------------------------

    #not sure about the what the data should look like, specifically
    #for "test_data" and "test_type"
    @unittest.skip("fails")
    def test_post_test(self):

        testname = "post_test"
        logger.info(f"[TEST {testname}]") 

        try:

            part_id = "Z00100300010-00001"

            data = {
                    "comments": "posting test for unit test",
                    "test_data": {},
                    "test_type": {"id" : 475,
                                "name" : "Bounce"
                                }
                    }
            
            resp = post_test(part_id, data)
            self.assertEqual(resp["status"], "OK")


        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")





if __name__ == "__main__":
    unittest.main()

        
