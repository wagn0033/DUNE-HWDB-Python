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

import json
import unittest
from Sisyphus.RestApiV1 import get_hwitem_by_part_id

class Test__get_hwitem_by_part_id(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def test_normal_item(self):
        resp = get_hwitem_by_part_id("Z00100300001-00021")
        
        expected_resp = json.loads('''{
                "data": {
                    "batch": null,
                    "component_id": 44801,
                    "component_type": {
                        "name": "Test Type 001",
                        "part_type_id": "Z00100300001"
                    },
                    "country_code": "US",
                    "created": "2023-07-12T15:05:23.758470-05:00",
                    "creator": {
                        "id": 13615,
                        "name": "Alex Wagner",
                        "username": "awagner"
                    },
                    "institution": {
                        "id": 186,
                        "name": "University of Minnesota Twin Cities"
                    },
                    "manufacturer": {
                        "id": 7,
                        "name": "Hajime Inc"
                    },
                    "part_id": "Z00100300001-00021",
                    "serial_number": "S00021",
                    "specifications": [
                        {
                            "Color": "blue",
                            "Comment": "Third comment.",
                            "Widget ID": "S00021",
                            "_meta": {
                                "_column_order": [
                                    "Widget ID",
                                    "Color",
                                    "Comment"
                                ]
                            }
                        }
                    ],
                    "specs_version": null
                },
                "link": {
                    "href": "/cdbdev/api/v1/components/Z00100300001-00021",
                    "rel": "self"
                },
                "methods": [
                    {
                        "href": "/cdbdev/api/v1/components/Z00100300001-00021/container",
                        "rel": "Container Info"
                    },
                    {
                        "href": "/cdbdev/api/v1/components/Z00100300001-00021/subcomponents",
                        "rel": "Subcomponents"
                    },
                    {
                        "href": "/cdbdev/api/v1/components/Z00100300001-00021/tests",
                        "rel": "Component Tests"
                    },
                    {
                        "href": "/cdbdev/api/v1/components/Z00100300001-00021/attributes",
                        "rel": "Component Attributes"
                    },
                    {
                        "href": "/cdbdev/api/v1/components/Z00100300001-00021/images",
                        "rel": "Component Images"
                    },
                    {
                        "href": "/cdbdev/api/v1/components/Z00100300001-00021/enable",
                        "rel": "Allow the use of Component"
                    },
                    {
                        "href": "/cdbdev/api/v1/get-qrcode/Z00100300001-00021",
                        "rel": "Generate QR Code"
                    },
                    {
                        "href": "/cdbdev/api/v1/get-barcode/Z00100300001-00021",
                        "rel": "Generate Barode"
                    }
                ],
                "status": "OK"
            }
        ''')
 
        #print(json.dumps(resp, indent=4))   
 
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
        
        resp = get_hwitem_by_part_id("Z00100200017-00001")
        self.assertEqual(resp["status"], "Server Error")
    
    
    def test_invalid_item(self):
        
        resp = get_hwitem_by_part_id("Z99999999999-99999")
        self.assertEqual(resp["status"], "Error")
    
    @unittest.skip("test later")
    def test_skip_example(self):
        pass
    
    

if __name__ == "__main__":
    unittest.main()
