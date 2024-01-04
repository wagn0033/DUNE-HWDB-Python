#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors:
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Tests bulk adding items
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

from Sisyphus.Utils.UnitTest import LoggedTestCase

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitems_bulk

class Test__post_hwitems_bulk(LoggedTestCase):
    """Tests bulk adding items"""

    #post (2) items in bulk, check status of post, retrieve part ids of items posted
    def test_post_hwitems_bulk(self):
        """Tests bulk adding items"""

        try:
            part_type_id = "Z00100300001"
            data= {
                "comments": "Here are some comments",
                "component_type": {
                    "part_type_id": part_type_id
                },
                "count": 2,
                "country_code": "US",
                "institution": {
                "id": 186
                },
                "manufacturer": {
                    "id": 7
                }
            }

            logger.info(f"Posting bulk components: part_type_id={part_type_id}, ")
            resp = post_hwitems_bulk(part_type_id, data)
            logger.info(f"Response from post: {resp}") 
            self.assertEqual(resp["status"], "OK")

            part_id1 = resp["data"][0]["part_id"]
            part_id2 = resp["data"][1]["part_id"]

            logger.info(f"New parts result: part_id1={part_id1}, part_id2={part_id2} ") 

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            raise err


    ##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

