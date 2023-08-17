#!/usr/bin/env python



import unittest
import os
import json
from Sisyphus.RestApiV1 import _get


class Test__get_tests(unittest.TestCase):

    def test_part_type_id_test_types(self):
        part_type_id = 'D00501341001'
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'ops_on_tests', 'test-types-D00501341001.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{part_type_id}/test-types")
        self.assertEqual(resp, expected_resp)

    def test_part_type_id_test_type_id(self):
        part_type_id = 'D00501341001'
        test_type_id = 465
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'ops_on_tests', 'part-id-test-type-id.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-types/{part_type_id}/test-types/{test_type_id}")
        self.assertEqual(resp, expected_resp)


    