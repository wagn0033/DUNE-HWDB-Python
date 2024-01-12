#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors:
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests posting an item
"""

from Sisyphus.Configuration import config
logger = config.getLogger()
from Sisyphus.Utils import UnitTest as unittest

import os
import json
import random

from Sisyphus.RestApiV1 import post_hwitem
from Sisyphus import RestApiV1 as ra


class Test__post_hwitem(unittest.TestCase):
    """Tests posting Items"""
    
    #-------------------------------------------------------------------------

    def test__post_hwitem(self):
        #{{{
        """Tests posting an item"""

        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": serial_number,
            "specifications": 
            {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Test: post component"
            },
            "subcomponents": {}
        }

        resp = post_hwitem(part_type_id, data)

        logger.info(f"The response was: {resp}")
        
        self.assertEqual(resp["status"], "OK")
        
        #}}}
    #-------------------------------------------------------------------------

    def test__post_hwitem__user_lacks_role(self):
        #{{{
        """Tests posting an item where the user doesn't have the right roles"""

        part_type_id = "Z00100300010"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 50
            },
            "serial_number": serial_number,
            "specifications": 
            {
                "Data": None
            },
            "subcomponents": {}
        }

        with self.assertRaises(ra.InsufficientPermissions):
            resp = post_hwitem(part_type_id, data)
    
        #}}}
    
    #-------------------------------------------------------------------------
    def test__post_hwitem__bad_spec_choice(self):
        #{{{
        """Tests posting an item where an illegal choice was made in spec

        If a field in the spec def is a list, then hwitems can only
        have a value from that list in their specs.

        This test attempts to use "yellow" for the "Color" field, when it
        should only be allowed to use "red", "green", or "blue".
        """

        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": serial_number,
            "specifications": 
            {
                "Widget ID": serial_number,
                "Color": "yellow",
                "Comment": "Unit Test: post component"
            },
            "subcomponents": {}
        }

        with self.assertRaises(ra.BadSpecificationFormat):
            resp = post_hwitem(part_type_id, data)

        #}}}
    #-------------------------------------------------------------------------
    
    #@unittest.skip("fails")
    def test__post_hwitem__empty_spec(self):
        #{{{
        """Tests posting an item with an empty spec where it should be allowed"""

        part_type_id = "Z00100300006"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": serial_number,
            "specifications": {},
            "subcomponents": {}
        }

        resp = post_hwitem(part_type_id, data)

        logger.info(f"The response was: {resp}")

        self.assertEqual(resp["status"], "OK")

        #}}}

    #-------------------------------------------------------------------------

    def test__post_hwitem__bad_spec(self):
        #{{{
        """Tests posting an item with a bad spec

        This should raise BadSpecificationFormat
        """
            
        logger.info("Testing <post_component> (V1)")
            
        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": serial_number,
            "specifications": 
            {
                "Widget-ID": serial_number, # The key is misspelled
                "Color": "red",
                "Comment": "Unit Test: post component"
            },
            "subcomponents": {}
        }

        with self.assertRaises(ra.BadSpecificationFormat):
            resp = post_hwitem(part_type_id, data)
        #}}}    

    #-------------------------------------------------------------------------

    #@unittest.skip("fails")
    def test__post_hwitem__extra_spec(self):
        #{{{
        """Tests posting an item with extra fields in the spec, which should be allowed"""

        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            "comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            "manufacturer": {
                "id": 7
            },
            "serial_number": serial_number,
            "specifications": 
            {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Test: post component",
                "Extra": 3
            },
            "subcomponents": {}
        }

        resp = post_hwitem(part_type_id, data)

        logger.info(f"The response was: {resp}")
        
        self.assertEqual(resp["status"], "OK")
        #}}}

    #-------------------------------------------------------------------------

    def test__post_hwitem__sparse(self):
        #{{{
        """Tests posting an item that's missing optional data"""

        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            #"comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            "country_code": "US",
            "institution": {
                "id": 186
            },
            #"manufacturer": {
            #    "id": 7
            #},
            #"serial_number": serial_number,
            "specifications":
            {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Test: post component",
            },
            #"subcomponents": {}
        }

        resp = post_hwitem(part_type_id, data)

        logger.info(f"The response was: {resp}")

        self.assertEqual(resp["status"], "OK")
        #}}}

    #-------------------------------------------------------------------------

    def test__post_hwitem__bad_fields(self):
        #{{{
        """Tests posting an item that has missing and extra fields"""

        part_type_id = "Z00100300001"
        serial_number = f"SN{random.randint(0x00000000, 0xFFFFFFFF):08X}"

        data = {
            #"comments": "Here are some comments",
            "component_type": {
                "part_type_id": part_type_id
            },
            #"country_code": "US",
            "bad_field": "abc",
            "institution": 186,
            #"institution": {
            #    "id": 186
            #},
            #"manufacturer": {
            #    "id": 7
            #},
            #"serial_number": serial_number,
            "specifications":
            {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Test: post component",
            },
            #"subcomponents": {}
        }

        with self.assertRaises(ra.BadDataFormat):
            resp = post_hwitem(part_type_id, data)

        #}}}

    ##############################################################################

if __name__ == "__main__":
    unittest.main()

