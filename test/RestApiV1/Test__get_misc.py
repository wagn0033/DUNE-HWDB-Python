#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__get_misc.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    get from under misc list
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import unittest
import os
import json
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


#from Sisyphus.RestApiV1._RestApiV1 import _get

class Test__get_misc_no_input(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 0x10000

    #-----------------------------------------------------------------------------

    #checks countries list
    def test_get_countries(self):
        testname = "get_countries"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'countries.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = get_countries()
             
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 
            
    #-----------------------------------------------------------------------------

    def test_whoami(self):
        testname = "whoami"
        logger.info(f"[TEST {testname}]")

        try:
            #will be broken eventually
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'alex_whoami.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = whoami() #currently alex

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 
        
    #-----------------------------------------------------------------------------
        
    def test_get_institutions(self):
        testname = "get_institutions"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'institutions.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = get_institutions()
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------
    
    def test_get_manufacturers(self):
        testname = "get_manufacturers"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'manufacturers.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            resp = get_manufacturers()
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------
    
    def test_get_projects(self):
        testname = "get_projects"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'projects.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            resp = get_projects()
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------
    
    def test_get_roles(self):
        testname = "get_roles"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'roles.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            
            resp = get_roles()            

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------
    
    def test_get_users(self):
        testname = "get_users"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'users.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            resp = get_users()
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 
    

   

class Test__get_misc_with_input(unittest.TestCase):
    
    def setUp(self):
        self.maxDiff = 0x10000
    
    #-----------------------------------------------------------------------------
    
    def test_get_user(self):
        testname = "get_user"
        logger.info(f"[TEST {testname}]")

        try:
            userid = 13615 #alex
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'alex_whoami.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            resp = get_user(userid)

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------

    def test_get_role(self):
        testname = "get_role"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__),
                    'ExpectedResponses', 'misc', 'role_id-4.json')
            with open(file_path, 'r') as file:
                expected_resp = json.load(file)
            role_id = 4
            
            resp = get_role(role_id)

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------

    def test_get_subsystems(self): #proj D; sys 1

        testname = "get_subsystems"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__), 
                    'ExpectedResponses', 'misc', 'proj-d_sys-1.json')
            with open(file_path , 'r') as file:
                expected_resp = json.load(file)
            proj_id = 'D'
            sys_id = 1
            
            resp = get_subsystems(proj_id, sys_id)

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)

            #checking if it throws return empty list/error
            file_path2 = os.path.join(os.path.dirname(__file__), 
                    'ExpectedResponses', 'misc', 'empty_list.json')
            with open(file_path2 , 'r') as file:
                err_expected_resp = json.load(file)
            
            err_proj_id = 's'
            
            # NOTE for Urbas: I changed this from "systems" to "subsystems" since I'm 
            # sure that's what was intended, but it means that the "expected result"
            # needs to be updated. (Delete this note when done!)
            #error_resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/systems/{err_proj_id}")
            error_resp = get_subsystems(err_proj_id, sys_id)          
            logger.debug(f"({testname}) response:\n{json.dumps(error_resp, indent=4)}")

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(error_resp, err_expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------
    
    def test_get_subsystem(self): #proj D; sys 1; subsys 1
        testname = "get_subsystem"
        logger.info(f"[TEST {testname}]")

        try:
            proj_id = 'D'
            sys_id = 1
            subsys_id = 1
            
            file_path = os.path.join(os.path.dirname(__file__), 
                    'ExpectedResponses', 'misc', 'proj-d_sys-1_subsys-1.json')
            with open(file_path , 'r') as file:
                expected_resp = json.load(file)
            
            
            resp = get_subsystem(proj_id, sys_id, subsys_id)

            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp, expected_resp)
            
            #checking if it throws error
            err_subsys_id = 9

            error_resp = get_subsystem(proj_id, sys_id, err_subsys_id)

            self.assertEqual(error_resp["status"], "Error")

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

    #-----------------------------------------------------------------------------
   
    def test_get_systems(self):
        testname = "get_systems"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__), 
                    'ExpectedResponses', 'misc', 'proj-d.json')
            with open(file_path , 'r') as file:
                expected_resp = json.load(file)
            proj_id = 'D'
            
            resp = get_systems(proj_id)
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp,expected_resp)

            #checking if it throws return empty list/error
            file_path2 = os.path.join(os.path.dirname(__file__), 
                'ExpectedResponses', 'misc', 'empty_list.json')
            with open(file_path2 , 'r') as file:
                err_expected_resp = json.load(file)
            err_proj_id = 's'

            error_resp = get_systems(err_proj_id)

            self.assertEqual(error_resp["status"], "OK")
            self.assertDictEqual(error_resp, err_expected_resp)

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 
    
    #-----------------------------------------------------------------------------

    def test_get_system(self):
        testname = "test_get_system"
        logger.info(f"[TEST {testname}]")

        try:
            file_path = os.path.join(os.path.dirname(__file__), 
                    'ExpectedResponses', 'misc', 'proj_sys.json')
            with open(file_path , 'r') as file:
                expected_resp = json.load(file)
            proj_id = 'D'
            sys_id = 1

            resp = get_system(proj_id, sys_id)
            
            self.assertEqual(resp["status"], "OK")
            self.assertDictEqual(resp,expected_resp)

            #checking if it throws error
            er_proj_id = 'X'
            er_sys_id = 80

            error_resp = get_system(er_proj_id, er_sys_id)
            self.assertEqual(error_resp["status"], "Error")

        except AssertionError as err:
            logger.error(f"[FAIL {testname}]")
            logger.info(err)
            logger.debug(f"({testname}) response:\n{json.dumps(resp, indent=4)}")
            raise err
        logger.info(f"[PASS {testname}]") 

##############################################################################

if __name__ == "__main__":
    unittest.main()
