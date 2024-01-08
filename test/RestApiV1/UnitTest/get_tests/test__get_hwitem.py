#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Test RestApiV1 functions related to Items
"""

from Sisyphus.Configuration import config
logger = config.getLogger()
from Sisyphus.Utils import UnitTest as unittest

import os
import json
import unittest

from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus import RestApiV1 as ra

class Test__get_hwitems(unittest.TestCase):
    """Test RestApiV1 functions related to Items"""
 
    def test_normal_item(self):
        """Get an item"""

        try:
            file_path = os.path.join(os.path.dirname(__file__), '..','ExpectedResponses', 
                                    'components', 'normal_item.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)

            resp = get_hwitem("Z00100300001-00021")
            logger.info(f"Response from post: {resp}")
        
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp['data']['component_id'],44801)
            self.assertEqual(resp['data']['component_type']['part_type_id'], 'Z00100300001')
            #self.assertEqual(resp, expected_resp)
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err 


    #-----------------------------------------------------------------------------     
        
    def test_broken_item(self):
        """Get 'corrupt' item

        The items added before Country/Institution were required will have 
        nulls for these values. This used to cause the REST API to crash and 
        return an HTML page with a 500 error. This has been fixed. This test
        will check that the fix is still working.
        """        

        try:
            resp = get_hwitem("Z00100200017-00001")
            self.assertEqual(resp['status'], "OK")
            self.assertIsNone(resp['data']['country_code'])
            self.assertIsNone(resp['data']['institution'])
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err 


    #----------------------------------------------------------------------------- 
    
    #check if getting an invalid item throws an error
    def test_invalid_item(self):
        """Attempt to get an invalid item"""        

        try:
            with self.assertRaises(ra.exceptions.DatabaseError):
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = get_hwitem("Z99999999999-99999")
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err 
    
    
    ##############################################################################                                
if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

