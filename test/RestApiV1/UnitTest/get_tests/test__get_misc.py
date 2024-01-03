#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Regents of the University of Minnesota
Authors: 
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Test 'miscellaneous' RestApiV1 functions
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.Utils.UnitTest import LoggedTestCase

import unittest
import os
import json
import sys

from Sisyphus.RestApiV1 import get_countries
from Sisyphus.RestApiV1 import whoami
from Sisyphus.RestApiV1 import get_institutions
from Sisyphus.RestApiV1 import get_manufacturers
from Sisyphus.RestApiV1 import get_projects
from Sisyphus.RestApiV1 import get_role
from Sisyphus.RestApiV1 import get_roles
from Sisyphus.RestApiV1 import get_user
from Sisyphus.RestApiV1 import get_users
from Sisyphus.RestApiV1 import get_system
from Sisyphus.RestApiV1 import get_systems
from Sisyphus.RestApiV1 import get_subsystem
from Sisyphus.RestApiV1 import get_subsystems
import Sisyphus.RestApiV1 as ra

#from Sisyphus.RestApiV1._RestApiV1 import _get

class Test__get_misc(LoggedTestCase):
    """Test 'miscellaneous' RestApiV1 functions"""

    #-----------------------------------------------------------------------------

    #checks countries list
    #by comparing to an expected json file
    def test_get_countries(self):
        """Get a list of countries"""

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    '..','ExpectedResponses', 'misc', 'countries.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = get_countries()
             
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
            
    #-----------------------------------------------------------------------------

    #checks structure of response: checks for string and integer where is expected 
    # in response
    def test_whoami(self):
        """Test 'whoami'"""

        try:
            resp = whoami() 

            self.assertEqual(resp["status"], "OK")
            self.assertIsInstance(resp["data"]["full_name"], str)
            self.assertIsInstance(resp["data"]["user_id"], int)
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
        
    #checks structure of response: checks if the first entry is US
    def test_get_institutions(self):
        """Get a list of institutions"""

        try:
            resp = get_institutions()
            
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp['data'][0]['country']['code'], "US")
            self.assertEqual(resp['data'][0]['country']['name'], "United States")
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
    
    #checks structure of response: checks is the first entry is Homenick Ltd, and 
    # that the last entry has an integer and string where it should be
    def test_get_manufacturers(self):
        """Get a list of manufacturers"""

        try:
            resp = get_manufacturers()
            
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp['data'][0]['id'], 1)
            self.assertEqual(resp['data'][0]['name'], "Homenick Ltd")

            self.assertIsInstance(resp['data'][-1]['id'], int)
            self.assertIsInstance(resp['data'][-1]['name'], str)
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
            
    #-----------------------------------------------------------------------------
    
    #checks structure of response: checks if DUNE is the second entry
    def test_get_projects(self):
        """Get a list of projects"""

        try:
            resp = get_projects()
            
            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp['data'][1]['id'], "D")
            self.assertEqual(resp['data'][1]['name'], "DUNE")
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
    
    #checks structure of response: checks if integer and string is where it is 
    # expected in response
    def test_get_roles(self):
        """Get a list of roles"""

        try:
            resp = get_roles()            

            self.assertEqual(resp["status"], "OK")
            self.assertIsInstance(resp["data"][-1]["id"], int)
            self.assertIsInstance(resp["data"][0]["component_types"][0]["name"], str)
            self.assertIsInstance(resp["data"][0]["users"][0]["user_id"], int)
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
    
    #checks structure of response: checks if integer and string is where it is 
    # expected in response
    def test_get_users(self):
        """Get a list of users"""

        try:
            resp = get_users()
              
            self.assertEqual(resp["status"], "OK")
            self.assertIsInstance(resp["data"][0]["user_id"],int )
            self.assertIsInstance(resp["data"][0]["username"], str)
            self.assertIsInstance(resp["data"][-1]["user_id"],int )
            self.assertIsInstance(resp["data"][-1]["username"], str)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
            
    #-----------------------------------------------------------------------------

    #compares response to expected json response 
    def test_get_user(self):
        """Get a specific user"""

        try:
            userid = 13615 #alex
            file_path = os.path.join(os.path.dirname(__file__),
                    '..','ExpectedResponses', 'misc', 'alex_whoami.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            resp = get_user(userid)

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
    
    #checks structure of response: if role id is correct and is assigned tester 
    # in response
    def test_get_role(self):
        """Get a specific role"""

        try:
            role_id = 4
            resp = get_role(role_id)

            self.assertEqual(resp["status"], "OK")

            
            self.assertEqual(resp["data"]["id"],role_id )
            self.assertEqual(resp["data"]["name"], "tester")
            
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------

    #checks structure of response: if integer is where is expected in response
    def test_get_subsystems(self): 
        """Get a list of subsystems from a project and system"""

        try:
            proj_id = 'Z'
            sys_id = 1
            
            resp = get_subsystems(proj_id, sys_id)

            self.assertEqual(resp["status"], "OK")
            self.assertIsInstance(resp["data"][0]["creator"]["id"],int )
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
    
    #-----------------------------------------------------------------------------

    def test_get_subsystems(self):
        """Get a list of subsystems from a project and system"""

        try:
            #checking if it throws return empty list/error
            file_path2 = os.path.join(os.path.dirname(__file__), 
                    '..','ExpectedResponses', 'misc', 'empty_list.json')
            with open(file_path2 , 'r') as file:
                err_expected_resp = json.load(file)
            
            proj_id = 's'
            sys_id = 1            

            resp = get_subsystems(proj_id, sys_id)          
            logger.debug(f"server response:\n{json.dumps(resp, indent=4)}")

            self.assertEqual(resp["status"], "OK")
            #self.assertDictEqual(error_resp, err_expected_resp)
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
    
    #compares response to expected json response
    def test_get_subsystem(self): 
        """Get a specific subsystem""" 
            
        try:
            proj_id = 'Z'
            sys_id = 1
            subsys_id = 1
            
            resp = get_subsystem(proj_id, sys_id, subsys_id)

            file_path = os.path.join(os.path.dirname(__file__),
                    '..','ExpectedResponses', 'misc', 'projZsys1subsys1.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(expected_resp, resp)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
    
    #-----------------------------------------------------------------------------
            
    def test_get_subsystem__bad(self):
        """Attempt to get a nonexistent subsystem

        This should raise a DatabaseError.
        """

        try:
            proj_id = 'Z'
            sys_id = 1
            subsys_id = 9

            with self.assertRaises(ra.exceptions.DatabaseError):
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = get_subsystem(proj_id, sys_id, subsys_id)

        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
   
    #checks structure of response: if string is where it is expected in response
    def test_get_systems(self):
        """Get a list of systems from a project"""

        try:
            proj_id = 'Z'
            
            resp = get_systems(proj_id)
            
            self.assertEqual(resp["status"], "OK")
            self.assertIsInstance(resp["data"][0]["comments"], str)
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err
        
    #-----------------------------------------------------------------------------

    def test_get_systems__nonexistent(self):
        """Attempt to get a list of systems from a non-existent project

        This should return an empty list and not raise an exception.
        """
           
        try: 
            proj_id = 's'

            resp = get_systems(proj_id)

            self.assertEqual(resp["status"], "OK")
            self.assertEqual(resp["pagination"]["total"], 0)
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    
    #-----------------------------------------------------------------------------

    #compares response to expected json response
    def test_get_system(self):
        """Get a system"""

        try:
            file_path = os.path.join(os.path.dirname(__file__), 
                    '..','ExpectedResponses', 'misc', 'projZsy.json')
            with open(file_path , 'r') as file:
                expected_resp = json.load(file)
            proj_id = 'Z'
            sys_id = 1

            resp = get_system(proj_id, sys_id)
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp,expected_resp)
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

    #-----------------------------------------------------------------------------
    
    def test_get_system__bad(self):
        """Attempt to get a non-existent system

        This should raise a DatabaseError.
        """

        try:
            #checking if it throws error
            proj_id = 'X'
            sys_id = 80

            with self.assertRaises(ra.exceptions.DatabaseError):
                logger.warning("NOTE: The following subtest raises an exception. This is normal.")
                resp = get_system(proj_id, sys_id)
            #self.assertEqual(error_resp["status"], "ERROR")
        
        except AssertionError as err:
            logger.error(f"Assertion Error: {repr(err)}")
            logger.info(f"server response:\n{json.dumps(resp, indent=4)}")
            raise err

##############################################################################

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)


