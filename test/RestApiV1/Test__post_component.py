#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__post_component.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    Python: get_hwitem_by_part_id(part_id)
    REST API: /api/v1/components/{part_id}
"""
import os
import json
import unittest
from Sisyphus.RestApiV1 import _post, post_component
from Sisyphus.Configuration import config
logger = config.getLogger()


class Test__post_component(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_post(self):
        
        logger.info("Testing <post_component>")
        
        part_type_id = "Z00100300001"
        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": "Z00100300001"
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": "S99999",
            "specifications": {},
            "subcomponents": {}
        }
        resp = post_component(part_type_id, data)
        

        
        self.assertEqual(resp["status"], "OK")
        #self.assertEqual(resp, expected_resp)


   
if __name__ == "__main__":
    unittest.main()
