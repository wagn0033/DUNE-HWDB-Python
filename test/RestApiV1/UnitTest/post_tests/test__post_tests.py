#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Regents of the University of Minnesota
Authors:
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Test POST methods in RestApiV1
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

from Sisyphus.Utils.UnitTest import LoggedTestCase

import os
import json
import unittest
import random

import Sisyphus.RestApiV1 as ra
from Sisyphus.RestApiV1 import post_test_type, post_test

class Test__post_tests(LoggedTestCase):
    """Test POST methods in RestApiV1"""

    @unittest.skip("adds too much data to be run daily")
    def test_post_test_type(self):

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
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    #-----------------------------------------------------------------------------

    def test_post_test_good(self):
        """Post a test to an item with valid data"""

        try:

            part_id = "Z00100300001-00360"

            data = \
            {        
                "comments": "posting good test for unit test",
                "test_data": 
                {
                    "Any": "slow",
                    "Color": "Yellow",
                    "Flavor": "vanilla"
                },
                "test_type": "unittest1"
            }
            
            resp = post_test(part_id, data)
            logger.info(f"Response from post: {resp}")
            self.assertEqual(resp["status"], "OK")

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    #-----------------------------------------------------------------------------
    
    def test_post_test_missing(self):
        """Post a test to an item with missing data"""

        try:

            part_id = "Z00100300001-00360"

            data = \
            {
                "comments": "posting test for unit test",
                "test_data": 
                {
                    "Any": "slow",
                    # Missing "Color" field from definition
                    "Flavor": "vanilla"
                },
                "test_type": "unittest1"
            }
          
            with self.assertRaises(ra.exceptions.BadSpecificationFormat): 
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = post_test(part_id, data)
                logger.info(f"Response from post: {resp}")

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    #-----------------------------------------------------------------------------
    
    def test_post_test_bad(self):
        """Post a test to an item with an invalid selection"""

        try:

            part_id = "Z00100300001-00360"

            data = \
            {
                "comments": "posting test for unit test",
                "test_data": 
                {
                    "Any": "slow",
                    "Color": "Green",
                    "Flavor": "blueberry" # Not an option in the definition
                },
                "test_type": "unittest1"
            }
          
            with self.assertRaises(ra.exceptions.BadSpecificationFormat): 
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = post_test(part_id, data)
                logger.info(f"Response from post: {resp}")

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    #-----------------------------------------------------------------------------
    
    def test_post_test_extra(self):
        """Post a test to an item with extra data"""

        try:

            part_id = "Z00100300001-00360"

            data = \
            {
                "comments": "posting test for unit test",
                "test_data": 
                {
                    "Any": "slow",
                    "Color": "Yellow",
                    "Flavor": "vanilla",
                    "_meta": {},
                },
                "test_type": "unittest1"
            }
          
            resp = post_test(part_id, data)
            logger.info(f"Response from post: {resp}")
            self.assertEqual(resp["status"], "OK")

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)
        
