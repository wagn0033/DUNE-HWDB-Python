#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Regents of the University of Minnesota
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


class Test__post_hwitem(LoggedTestCase):
    """Tests posting an item"""

    #posts item, checks status
    def test_post_hwitem(self):
        """Tests posting an item"""

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

    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

