#!/usr/bin/env python



import unittest
import os
import json
from Sisyphus.RestApiV1 import _get



class Test__get_component_type(unittest.TestCase):
    def test_part_type_id(self):
        part_type_id = 'D00501341001'
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'componentTypes', 'part-type-id-D00501341001.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{part_type_id}")
        self.assertEqual(resp, expected_resp)

    def test_part_type_id_components(self):
        part_type_id = 'D00501341001'
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'componentTypes', 'components_page1.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{part_type_id}/components?page=1")
        self.assertEqual(resp, expected_resp)

    def test_part_type_id_connectors(self):
        part_type_id = 'D00501341001'
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'componentTypes', 'connectors.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{part_type_id}/connectors")
        self.assertEqual(resp, expected_resp)
    
    def test_part_type_id_specifications(self):
        part_type_id = 'D00501341001'
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'componentTypes', 'specifications.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{part_type_id}/specifications")
        self.assertEqual(resp, expected_resp)

    def test_component_type_by_proj_sys(self):
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'componentTypes', 'list-components-by-sys.json')
        with open(file_path , 'r') as file:
            expected_resp = json.load(file)
        proj_id = 'D'
        sys_id = 1
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{proj_id}/{sys_id}?page=1")

        self.assertEqual(resp,expected_resp)

    def test_component_type_by_proj_sys_subsys(self):
        file_path = os.path.join(os.path.dirname(__file__), 'ExpectedResponses', 'componentTypes', 'comp-types-D-1-1.json')
        with open(file_path , 'r') as file:
            expected_resp = json.load(file)
        proj_id = 'D'
        sys_id = 1
        subsys_id = 1
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{proj_id}/{sys_id}/{subsys_id}")

        self.assertEqual(resp,expected_resp)