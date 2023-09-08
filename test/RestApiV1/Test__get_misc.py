#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__get_misc.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Tests: 
    get from under misc list
"""

import unittest
import os
import json
from Sisyphus.RestApiV1 import _get, get_countries



class Test__get_misc_no_input(unittest.TestCase):
    #checks countries list
    def test_countries(self):
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'countries.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        
        resp = get_countries()
         
        #self.assertEqual(resp["status"], "OK")
        self.assertEqual(resp, expected_resp)
        

    def test_whoami(self):
        #will be broken eventually
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'alex_whoami.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get("https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/users/whoami") #currently alex
        
        self.assertEqual(resp, expected_resp)
        
        
    def test_institutions(self):
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'institutions.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get("https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/institutions")
        self.assertEqual(resp, expected_resp)

    def test_manufacturers(self):
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'manufacturers.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get("https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/manufacturers")
        self.assertEqual(resp, expected_resp)

    def test_projects(self):
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'projects.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get("https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/projects")
        self.assertEqual(resp, expected_resp)

    
    def test_roles(self):
        resp = _get("https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/roles")
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'roles.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        self.assertEqual(resp, expected_resp)
        

    def test_users(self):
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'users.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get("https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/users")
        self.assertEqual(resp, expected_resp)

    

   

class Test__get_misc_with_input(unittest.TestCase):
    def test_userid(self):
        userid = 13615 #alex
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'alex_whoami.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/users/{userid}")
        self.assertEqual(resp, expected_resp)


    def test_role_id(self):
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'misc', 'role_id-4.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        role_id = 4
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/roles/{role_id}")

        self.assertEqual(resp, expected_resp)

    def test_subsys_by_projid_sys(self): #proj D; sys 1
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'misc', 'proj-d_sys-1.json')
        with open(file_path , 'r') as file:
            expected_resp = json.load(file)
        proj_id = 'D'
        sys_id = 1
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/subsystems/{proj_id}/{sys_id}")

        self.assertEqual(resp,expected_resp)

        #checking if it throws return empty list/error
        file_path2 = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'misc', 'empty_list.json')
        with open(file_path2 , 'r') as file:
            err_expected_resp = json.load(file)
        err_proj_id = 's'
        error_resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/systems/{err_proj_id}")
        self.assertEqual(error_resp, err_expected_resp)

    def test_subsys_by_projid_sys_subsys(self): #proj D; sys 1; subsys 1
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'misc', 'proj-d_sys-1_subsys-1.json')
        with open(file_path , 'r') as file:
            expected_resp = json.load(file)
        proj_id = 'D'
        sys_id = 1
        subsys_id = 1
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/subsystems/{proj_id}/{sys_id}/{subsys_id}")

        self.assertEqual(resp,expected_resp)
        #checking if it throws error
        er_subsys_id = 9
        error_resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/subsystems/{proj_id}/{sys_id}/{er_subsys_id}")

        self.assertEqual(error_resp["status"], "Error")

    def test_projid(self):
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'misc', 'proj-d.json')
        with open(file_path , 'r') as file:
            expected_resp = json.load(file)
        proj_id = 'D'
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/systems/{proj_id}")

        self.assertEqual(resp,expected_resp)

        #checking if it throws return empty list/error
        file_path2 = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'misc', 'empty_list.json')
        with open(file_path2 , 'r') as file:
            err_expected_resp = json.load(file)
        err_proj_id = 's'
        error_resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/systems/{err_proj_id}")
        self.assertEqual(error_resp, err_expected_resp)
    
    def test_projid_sysid(self):
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'misc', 'proj_sys.json')
        with open(file_path , 'r') as file:
            expected_resp = json.load(file)
        proj_id = 'D'
        sys_id = 1
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/systems/{proj_id}/{sys_id}")

        self.assertEqual(resp,expected_resp)

        #checking if it throws error
        er_proj_id = 'X'
        er_sys_id = 80
        error_resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/systems/{er_proj_id}/{er_sys_id}")

        self.assertEqual(error_resp["status"], "Error")
    
if __name__ == "__main__":
    unittest.main()
