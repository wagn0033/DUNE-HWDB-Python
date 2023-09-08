#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__get_tests.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
"""


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

    def test_comp_test_by_oid(self):
        oid = 1
        file_path = os.path.join(os.path.dirname(__file__),'ExpectedResponses', 'ops_on_tests', 'oid1.json')
        with open(file_path, 'r') as file:
            expected_resp = json.load(file)
        resp = _get(f"https://dbwebapi2.fnal.gov:8443/cdbdev/api/v1/component-test-types/{oid}")
        self.assertEqual(resp, expected_resp)



    