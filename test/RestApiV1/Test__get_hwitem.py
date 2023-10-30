#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__get_hwitems_by_component_type_id.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    Python: get_hwitem_by_part_id(part_id)
    REST API: /api/v1/components/{part_id}
"""
import os
import json
import unittest
from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus.RestApiV1 import get_component_type_image_list

pp = lambda s: print(json.dumps(s, indent=4))

class Test__get_hwitem_by_part_id(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 0x10000
    def tearDown(self):
        pass
    
    def test_normal_item(self):
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 
                                'components', 'normal_item.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = get_hwitem("Z00100300001-00021")
        
        self.assertEqual(resp["status"], "OK")
        self.assertEqual(resp, expected_resp)
        
    
    def test_broken_item(self):
        #
        # The items added before Country/Institution were required will
        # cause the REST API to throw an internal server error in HTML
        # instead of JSON.
        #
        # This test is more for testing that the RestApiV1 python library
        # correctly figures this out and returns the info as JSON.
        
        resp = get_hwitem("Z00100200017-00001")
        self.assertEqual(resp["status"].upper(), "SERVER ERROR")
    
    
    def test_invalid_item(self):
        
        resp = get_hwitem("Z99999999999-99999")
        self.assertEqual(resp["status"].upper(), "ERROR")
    
    @unittest.skip("test later")
    def test_skip_example(self):
        pass
    
    @unittest.skip("get_image_by_part_id not working")
    def test_image_by_part_id(self):
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses',
                                'components', 'image_by_part_id.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = get_image_by_part_id("Z00100100048-00033")
        #print(resp)
        self.assertEqual(expected_resp, resp)
                                   

   
if __name__ == "__main__":
    unittest.main()
