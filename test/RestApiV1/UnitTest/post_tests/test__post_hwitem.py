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

from Sisyphus.Utils.UnitTest import LoggedTestCase

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitem
from Sisyphus import RestApiV1 as ra


class Test__post_hwitem(LoggedTestCase):
    """Tests posting Items"""
    
    #-------------------------------------------------------------------------

    def test__post_hwitem(self):
        #{{{
        """Tests posting an item"""

        try:
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
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        #}}}
    #-------------------------------------------------------------------------

    #@unittest.skip("fails")
    def test__post_hwitem__empty_spec(self):
        #{{{
        """Tests posting an item with an empty spec where it should be allowed"""

        try:
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

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        #}}}

    #-------------------------------------------------------------------------

    def test__post_hwitem__bad_spec(self):
        #{{{
        """Tests posting an item with a bad spec

        This should raise BadSpecificationFormat
        """

        try:
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
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = post_hwitem(part_type_id, data)

            #logger.info(f"The response was: {resp}")
            
            #self.assertEqual(resp["status"], "OK")
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        #}}}    

    #-------------------------------------------------------------------------

    #@unittest.skip("fails")
    def test__post_hwitem__extra_spec(self):
        #{{{
        """Tests posting an item with extra fields in the spec, which should be allowed"""

        try:
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
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        #}}}

    #-------------------------------------------------------------------------

    def test__post_hwitem__sparse(self):
        #{{{
        """Tests posting an item that's missing optional data"""

        try:
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

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        #}}}

    #-------------------------------------------------------------------------

    def test__post_hwitem__bad_fields(self):
        #{{{
        """Tests posting an item that has missing and extra fields"""

        try:
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
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = post_hwitem(part_type_id, data)

            #logger.info(f"The response was: {resp}")

            #self.assertEqual(resp["status"], "OK")

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
        #}}}

    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

