#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors:
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Test RestApi functions related to Item Tests
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)
from Sisyphus.Utils import UnitTest as unittest

import unittest
import os
import json

from Sisyphus.RestApiV1 import get_test_type
from Sisyphus.RestApiV1 import get_test_types
from Sisyphus.RestApiV1 import get_test_type_by_oid

#from Sisyphus.RestApiV1._RestApiV1 import _get


class Test__get_tests(unittest.TestCase):
    """Test RestApi functions related to Item Tests"""

    #-----------------------------------------------------------------------------

    #checks structure of response: if the last test is Bounce
    def test_test_types(self):
        """Get a list of test types for a component type"""

        try:
            part_type_id = 'Z00100300001'
            
            resp = get_test_types(part_type_id)            

            self.assertEqual(resp['status'], "OK")
            self.assertEqual(resp["data"][-1]["name"], "Bounce")
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
            

    #-----------------------------------------------------------------------------

    #checks structure of response: if the name of the 
    # component type is Test Type 001, and has the correct part type id
    def test_test_type(self):
        """Get a specific test type definition"""

        try:
            part_type_id = 'Z00100300001'
            test_type_id = 492
            
            
            resp = get_test_type(part_type_id, test_type_id)            

            self.assertEqual(resp['status'], "OK")
            self.assertEqual(resp["component_type"]["name"], "Test Type 001")
            self.assertEqual(resp["component_type"]["part_type_id"], part_type_id)
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    
    #-----------------------------------------------------------------------------

    #compares response to expected json response
    def test_test_type_by_oid(self):
        """Get a specific test type definition by oid"""

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
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err


##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

    
