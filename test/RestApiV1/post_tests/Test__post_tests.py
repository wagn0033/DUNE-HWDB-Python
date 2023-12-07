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

    @unittest.skip("creates new test-- works but too much for daily cron job")
    def test_post_test_type(self):

        testname = "post_test_type"
        logger.info(f"[TEST {testname}]") 

        try:

            part_type_id = "Z00100300001"

            data = {
                    "comments": "adding new test",
                    "component_type": {
                        "part_type_id": part_type_id
                    },
                    "name": "unittest2",
                    "specifications": {"Speed": ["slow", "medium", "fast"]}
                    }
            
            resp = post_test_type(part_type_id, data)
            logger.info(f"Response from post: {resp}") 
            self.assertEqual(resp["status"], "OK")


        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")

#-----------------------------------------------------------------------------

    
    def test_post_test(self):

        testname = "post_test"
        logger.info(f"[TEST {testname}]") 

        try:

            part_id = "Z00100300001-00360"

            data = {
                    
                    "comments": "posting test for unit test",
                    "test_data": {"Any": "slow",
                                  "Color": "Yellow",
                                  "Flavor": "vanilla"
                                  },
                    "test_type": "unittest1"
                    }
            
            resp = post_test(part_id, data)
            logger.info(f"Response from post: {resp}")
            self.assertEqual(resp["status"], "OK")

            #test for error
            data = {
                    
                    "comments": "posting test for unit test",
                    "test_data": {"Any": "slow",
                                  "Flavor": "vanilla"
                                  },
                    "test_type": "unittest1"
                    }
            
            resp = post_test(part_id, data)
            logger.info(f"Response from post: {resp}")
            self.assertEqual(resp["status"], "ERROR")



        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            raise err

        logger.info(f"[PASS {testname}]")





if __name__ == "__main__":
    unittest.main()

        
