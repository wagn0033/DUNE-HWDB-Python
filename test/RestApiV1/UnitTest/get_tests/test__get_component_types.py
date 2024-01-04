#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors: 
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Test RestApiV1 functions related to Component Types
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.Utils.UnitTest import LoggedTestCase

import unittest
import os
import json

from Sisyphus.RestApiV1 import get_component_type
from Sisyphus.RestApiV1 import get_hwitems
from Sisyphus.RestApiV1 import get_component_type_connectors
from Sisyphus.RestApiV1 import get_component_type_specifications
from Sisyphus.RestApiV1 import get_component_types

class Test__get_component_type(LoggedTestCase):
    """Test RestApiV1 functions related to Component Types"""
 
    #-----------------------------------------------------------------------------    

    def test_get_component_type(self):
        """Get component type"""
        
        try:
            part_type_id = 'Z00100300001'
            
            resp = get_component_type(part_type_id)

            self.assertEqual(resp['status'], "OK")
            self.assertEqual(resp['data']['connectors']['Subcomp 1'], 'Z00100300002')
 
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
    
    #-----------------------------------------------------------------------------    

    def test_get_hwitems(self):
        """Get a list of items"""

        try:
            part_type_id = 'Z00100110001'
            page, size = 1, 20

            resp = get_hwitems(part_type_id, page=page, size=size)            
            
            self.assertEqual(resp['status'], "OK")
            self.assertIsInstance(resp['data'][0]['component_id'], int)
            self.assertIsInstance(resp['data'][0]['creator']['id'], int)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------    
    
    def test_component_type_connectors(self):
        """Get subcomponents for component type"""
        
        try:
            part_type_id = 'Z00100300001' 
            
            resp = get_component_type_connectors(part_type_id)
            
            self.assertEqual(resp['status'], "OK")
            self.assertEqual(resp['data']['Subcomp 1'], 'Z00100300002')
        
        except AssertionError as err:
            logger.debug(f"server response:\n{json.dumps(resp, indent=4)}")
            logger.error(f"Assertion Error: {repr(err)}")
            raise err
    
    #-----------------------------------------------------------------------------    
    
    def test_component_type_specifications(self):
        """Get specification definition for component type"""
    
        try:
            part_type_id = 'Z00100300001'
            
            resp = get_component_type_specifications(part_type_id)
            logger.info(f"response from HWDB:{resp}")
            self.assertEqual(resp['status'], "OK")

            self.assertEqual(resp['data'][0]['creator'], "Alex Wagner")
            self.assertEqual(resp['data'][0]['datasheet']['Widget ID'], None)
            
        except AssertionError as err:
            logger.debug(f"server response:\n{json.dumps(resp, indent=4)}")
            logger.error(f"Assertion Error: {repr(err)}")
            raise err


    #-----------------------------------------------------------------------------    
    
    def test_component_types_by_proj_sys(self):
        """Get a list of component types by project and system"""    
    
        try:
            proj_id = 'Z'
            sys_id = 1

            page, size = 1, 100
            fields = [] 
 
            resp = get_component_types(proj_id, sys_id, page=page, size=size)

            self.assertEqual(resp['status'], "OK")
            self.assertIsInstance(resp['data'][0]['category'], str)
            self.assertIsInstance(resp['data'][0]['creator']['id'], int)

        except AssertionError as err:
            logger.debug(f"server response:\n{json.dumps(resp, indent=4)}")
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

    #-----------------------------------------------------------------------------    
    
    def test_component_types_by_proj_sys_subsys(self):
        """Get a list of component types by project, system, and subsystem"""
        try:
            proj_id = 'Z'
            sys_id = 1
            subsys_id = 1
            page, size = 1, 100
            fields = []
 
            resp = get_component_types(proj_id, sys_id, subsys_id, page=page, size=size)

            self.assertEqual(resp['status'], "OK")
            self.assertIsInstance(resp['data'][0]['category'], str)
            self.assertIsInstance(resp['data'][0]['creator']['id'], int)

        except AssertionError as err:
            logger.debug(f"server response:\n{json.dumps(resp, indent=4)}")
            logger.error(f"Assertion Error: {repr(err)}")
            raise err

##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)
