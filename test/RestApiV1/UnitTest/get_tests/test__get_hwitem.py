#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Regents of the University of Minnesota
Authors: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Test RestApiV1 functions related to Items
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

from Sisyphus.Utils.UnitTest import LoggedTestCase

import os
import json
import unittest

from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus.RestApiV1 import get_hwitem_image_list
from Sisyphus.RestApiV1 import exceptions as raex

class Test__get_hwitem(LoggedTestCase):
   
    #gets normal item
    #tests by checking the structure: checks if component id is expected, 
    #and if part type id is expected
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
            with self.assertRaises(raex.DatabaseError):
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = get_hwitem("Z99999999999-99999")
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err 
    
    #----------------------------------------------------------------------------- 
    
    def test_item_image_list(self):
        """Get a list of images stored for an item

        Tests that a particular item in the database has at least one image,
        and that the entries representing each image has the correct fields.
        """

        try:
            expected_fields = {
                "comments", "created", "creator", "image_id", "image_name",
                "library", "link"
            }

            resp = get_hwitem_image_list("Z00100300006-00001")
            
            self.assertEqual(resp["status"], "OK")
            self.assertGreater(len(resp["data"]), 0)
            for image_node in resp["data"]:
                self.assertSetEqual(set(image_node.keys()), expected_fields)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err 
    
    ##############################################################################                                
if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

