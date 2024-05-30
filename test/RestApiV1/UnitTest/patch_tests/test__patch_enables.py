#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests setting "enabled" status in item
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)
from Sisyphus.Utils import UnitTest as unittest

import os
import json
import unittest
import random

from Sisyphus.RestApiV1 import post_hwitem
from Sisyphus.RestApiV1 import patch_hwitem
from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus.RestApiV1 import patch_hwitem_enable
from Sisyphus.RestApiV1 import patch_hwitem_status
from Sisyphus.RestApiV1 import post_hwitems_bulk
from Sisyphus.RestApiV1 import patch_hwitems_enable_bulk

class Test__patch_enables(unittest.TestCase):
    """Tests setting "enabled" status in item"""

    #post a new item, patch it to be enabled, check if it was enabled. 
    # Patch it again to disable it, check it was disabled
    def test__patch_hwitem_enable(self):
        #{{{
        """Tests setting "enabled" status in item"""

        #POST
        #########

        part_type_id = "Z00100300001"
        serial_number = "S99999"

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
            "specifications": {
                "Widget ID": serial_number,
                "Color": "red",
                "Comment": "Unit Testing"
            },
            "subcomponents": {},
            "status": {
                "id": 1
            }
        }

        logger.info(f"Posting new hwitem: part_type_id={part_type_id}, "
                    f"serial_number={serial_number}")
        resp = post_hwitem(part_type_id, data)
        logger.info(f"Response from post: {resp}") 
        self.assertEqual(resp["status"], "OK")

        component_id = resp["component_id"]
        part_id = resp["part_id"]

        logger.info(f"New hwitem result: part_id={part_id}, component_id={component_id}") 
    

        #PATCH ENABLE
        #########

        data = {
            "comments": "here are some comments",
            "component": {
            "id": component_id,
            "part_id": part_id
            },
            "enabled": True,
            "geo_loc": {
            "id": 0
            }
        }

        resp = patch_hwitem_enable(part_id, data)
        logger.info(f"Response from patch: {resp}")
        self.assertEqual(resp["status"], "OK")
        #self.assertTrue(resp["enabled"])

        #GET/CHECK
        ##########

        resp = get_hwitem(part_id)
        #self.assertTrue(resp["data"]["enabled"])
        self.assertEqual(resp["data"]["status"]["id"], 1)

        #PATCH DISABLE
        #########
        
        data = {
            "comments": "here are some comments",
            "component": {
            "id": component_id,
            "part_id": part_id
            },
            "enabled": False,
            "geo_loc": {
            "id": 0
            }
        }

        resp = patch_hwitem_enable(part_id, data)
        logger.info(f"Response from patch: {resp}")
        self.assertEqual(resp["status"], "OK")

        #GET/CHECK
        ##########

        resp = get_hwitem(part_id)
        #self.assertFalse(resp["data"]["enabled"])
        self.assertEqual(resp["data"]["status"]["id"], 2)

        #}}}

    #-------------------------------------------------------------------------

    #@unittest.skip("needs change to status")    
    def test__patch_hwitem_enable__enabled_persistence(self):
        #{{{
        """Tests whether patching an item resets 'enabled'

        When an item is patched, it should stay enabled or disabled, and
        not be automatically reset to disabled. This test verifies that the
        bug has been fixed.
        """

        part_id = "Z00100300001-00001"
        logger.info(f"Enabling item {part_id}")

        # Get an existing item
        orig_item = get_hwitem(part_id)
       
        def change_enabled(orig_item, enabled=True):
            new_comment = f"changing enabled to {enabled} ({random.randint(0, 999999):06d})"
            data = {
                "comments": new_comment,
                "component": {"part_id": orig_item['data']['part_id']},
                "enabled": enabled,
            }
            resp = patch_hwitem_enable(orig_item['data']['part_id'], data)

        # Enable it, if disabled
        #if not orig_item['data']['enabled']:
        if not orig_item['data']['status']['id'] == 1:
            change_enabled(orig_item, True)
            enabled_item = get_hwitem(part_id)
            #self.assertTrue(enabled_item['data']['enabled'], 'The item was not enabled')
            self.assertEqual(enabled_item['data']['status']['id'], 1)
            orig_item = enabled_item

        # Patch it
        data = {
            "part_id": part_id,
            "comments": "editing comment for item",
            "manufacturer": None,
            "serial_number": orig_item["data"]["serial_number"],
            "specifications": orig_item["data"]["specifications"][0],
        }
        resp = patch_hwitem(part_id, data)

        # Get the item again
        changed_item = get_hwitem(part_id)
        #self.assertTrue(changed_item['data']['enabled'], 'The item was disabled after patching')
        self.assertEqual(changed_item['data']['status']['id'], 1, 'The item was disabled after patching')

        #}}}
    
    #-------------------------------------------------------------------------
    
    @unittest.skip("we decided this behavior is okay for now")    
    def test__patch_hwitem_enable__comment_persistence(self):
        #{{{
        """Tests whether enabling alters the item's comment

        Enabling/disabling an item accepts a comment, but that comment
        should go somewhere else in the database instead of as one of
        the item properties. This test will verify whether this bug has
        been fixed.
        """

        part_id = "Z00100300001-00001"
        logger.info(f"Enabling item {part_id}")

        # Get an existing item
        orig_item = get_hwitem(part_id)
       
        def change_enabled(orig_item, enabled=True):
            new_comment = f"changing enabled to {enabled} ({random.randint(0, 999999):06d})"
            data = {
                "comments": new_comment,
                "component": {"part_id": orig_item['data']['part_id']},
                "enabled": enabled,
            }
            resp = patch_hwitem_enable(orig_item['data']['part_id'], data)

        # Disable it, if enabled 
        errors = []
        #if orig_item['data']['enabled']:
        if orig_item['data']['status']['id'] == 1:
            change_enabled(orig_item, False)
            disabled_item = get_hwitem(part_id)
            comment2, comment1 = disabled_item['data']['comments'], orig_item['data']['comments']
            #print(comment1, comment2)
            if comment1 != comment2:
                errors.append(f"Initial disable: comment changed from '{comment1}' to '{comment2}'")
            orig_item = disabled_item        

        # Enable it
        change_enabled(orig_item, True)
        enabled_item = get_hwitem(part_id)
        comment2, comment1 = enabled_item['data']['comments'], orig_item['data']['comments']
        #print(comment1, comment2)
        if comment1 != comment2:
            errors.append(f"On enabling, comment changed from '{comment1}' to '{comment2}'")
        orig_item = enabled_item

        # Disable it
        change_enabled(orig_item, False)
        disabled_item = get_hwitem(part_id)
        #print(comment1, comment2)
        comment2, comment1 = disabled_item['data']['comments'], orig_item['data']['comments']
        if comment1 != comment2:
            errors.append(f"On disabling, comment changed from '{comment1}' to '{comment2}'")
        orig_item = disabled_item        

        if errors:
            self.fail("; ".join(errors))

        #}}}

    #-------------------------------------------------------------------------
    
    #post (2) items in bulk, get part ids from response of post, 
    # use those part ids to enable them, check if they were enabled. 
    # Disable them, check if they were disabled
    #@unittest.skip("needs change to status")    
    def test_patch_enable_bulk(self):
        #{{{
        """Tests setting "enabled" status in several items at the same time"""

        #POST bulk
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

        logger.info(f"New part result: part_id={part_id1, part_id2}") 

        #ENABLE
        
        data = {
            "data": [{
                "comments": "string",
                "enabled": True,
                "part_id": part_id1
                },
                {
                "comments": "string",
                "enabled": True,
                "part_id": part_id2
                }
            ]}
        
        resp = patch_hwitems_enable_bulk(data)
        logger.info(f"Response from post: {resp}")
        
        
        #GET/CHECK

        resp = get_hwitem(part_id1)
        resp2 = get_hwitem(part_id2)
        #self.assertTrue(resp["data"]["enabled"])
        #self.assertTrue(resp2["data"]["enabled"])
        self.assertEqual(resp["data"]["status"]["id"], 1)
        self.assertEqual(resp2["data"]["status"]["id"], 1)
        logger.info(f"Response from post: {resp}") 


        #DISABLE

        data = {
            "data": [{
                "comments": "string",
                "enabled": False,
                "part_id": part_id1
                },
                {
                "comments": "string",
                "enabled": False,
                "part_id": part_id2
                }
            ]}
        
        resp = patch_hwitems_enable_bulk(data)
        logger.info(f"Response from post: {resp}")

        #GET/CHECK
        resp = get_hwitem(part_id1)
        resp2 = get_hwitem(part_id2)
        #self.assertFalse(resp["data"]["enabled"])
        #self.assertFalse(resp2["data"]["enabled"])
        self.assertNotEqual(resp["data"]["status"]["id"], 1)
        self.assertNotEqual(resp2["data"]["status"]["id"], 1)
        logger.info(f"Response from post: {resp}")
        #}}}

#=================================================================================

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)

        


    

