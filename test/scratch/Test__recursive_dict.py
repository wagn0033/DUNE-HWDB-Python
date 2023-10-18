#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testing some features of unit tests
"""
import unittest

class Test__scratch(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 0x10000

    def test_scratch(self):
        d1 = {
            'root':
            {
                'name': 'root',
                'children':
                [
                    {
                        'name': 'child',
                        'parent': None,
                        'children': []
                    }
                ]
            }
        }
        d1['root']['children'][0]['parent'] = d1['root']

        d2 = {
            'root':
            {
                'name': 'root',
                'children':
                [
                    {
                        'name': 'child',
                        'parent': None,
                        'children': []
                    }
                ]
            }
        }
        d2['root']['children'][0]['parent'] = d2['root']

        self.assertDictEqual(d1, d2)

if __name__ == "__main__":
    unittest.main()

