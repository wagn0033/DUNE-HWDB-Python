#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__get_tests.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import unittest
import os
import json

from Sisyphus.RestApiV1 import get_test_type
from Sisyphus.RestApiV1 import get_test_types
from Sisyphus.RestApiV1 import get_test_type_by_oid

#from Sisyphus.RestApiV1._RestApiV1 import _get


class Test__get_tests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 0x10000

    #-----------------------------------------------------------------------------

    def test_test_types(self):
        testname = "get_test_types"
        logger.info(f"[TEST {testname}]")

        try:
            part_type_id = 'D00501341001'
            file_path = os.path.join(os.path.dirname(__file__),
                    '..','ExpectedResponses', 'ops_on_tests', 
                    'test-types-D00501341001.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = get_test_types(part_type_id)            

            self.assertEqual(resp['status'], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]")


    #-----------------------------------------------------------------------------

    def test_test_type(self):
        testname = "get_test_type"
        logger.info(f"[TEST {testname}]")

        try:
            part_type_id = 'D00501341001'
            test_type_id = 465
            file_path = os.path.join(os.path.dirname(__file__),
                    '..','ExpectedResponses', 'ops_on_tests', 'part-id-test-type-id.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = get_test_type(part_type_id, test_type_id)            

            self.assertEqual(resp['status'], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]")
    
    #-----------------------------------------------------------------------------

    def test_test_type_by_oid(self):
        testname = "get_test_type_by_oid"
        logger.info(f"[TEST {testname}]")

        try:
            oid = 1
            file_path = os.path.join(os.path.dirname(__file__),
                    '..','ExpectedResponses', 'ops_on_tests', 'oid1.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            #resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-test-types/{oid}")
            resp = get_test_type_by_oid(oid)            

            self.assertEqual(resp['status'], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]")

##############################################################################

if __name__ == "__main__":
    unittest.main()


    
