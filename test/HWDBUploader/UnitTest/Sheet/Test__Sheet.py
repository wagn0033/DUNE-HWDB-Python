#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/HWDBUploader/Test__000.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)
from Sisyphus.HWDBUploader import Sheet

import unittest

class Test__Sheet(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 0x10000
        logger.info(f"[TEST {self.id()}]")


    def tearDown(self):
        has_error = self._outcome.errors[-1][1] is not None

        if not has_error:
            logger.info(f"[PASS {self.id()}]")
        else:
            logger.error(f"[FAIL {self.id()}]")
    
    #-----------------------------------------------------------------------------

    def test__header_only__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "header-only.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 1)
            self.assertEqual(str(sheet.coalesce("Serial Number").value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Color").value), "Red")

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 1).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    
    def test__one_column_header__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "one-column-header.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(sheet.coalesce("Serial Number").value, None)
            self.assertEqual(sheet.coalesce("Serial Number", 0).value, 101)
            self.assertEqual(sheet.coalesce("Serial Number", 4).value, 105)
            self.assertEqual(sheet.coalesce("Inherited Value").value, 343)
            self.assertEqual(sheet.coalesce("Inherited Value", 0).value, 343)
            self.assertEqual(sheet.coalesce("Inherited Value", 4).value, 343)
            self.assertEqual(sheet.coalesce("Local Value").value, 'potato')
            self.assertEqual(sheet.coalesce("Local Value", 0).value, 'potato')

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------

    def test__one_column_noheader__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "one-column-noheader.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(sheet.coalesce("Serial Number").value, None)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(sheet.coalesce("Local Value").value, None)
            self.assertEqual(sheet.coalesce("Local Value", 0).value, None)

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    
    def test__two_column_header__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "two-column-header.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(sheet.coalesce("Serial Number").value, None)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(str(sheet.coalesce("Local Value").value), 'potato')
            self.assertEqual(str(sheet.coalesce("Local Value", 0).value), 'potato')

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    
    def test__two_column_noheader__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "two-column-noheader.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(sheet.coalesce("Local Value").value, None)
            self.assertEqual(sheet.coalesce("Local Value", 0).value, None)

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------
    
    def test__three_column_header__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "three-column-header.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(str(sheet.coalesce("Color", 0).value), "Red")
            self.assertEqual(str(sheet.coalesce("Color", 4).value), "Blue")
            self.assertEqual(str(sheet.coalesce("Local Value").value), 'potato')
            self.assertEqual(str(sheet.coalesce("Local Value", 0).value), 'potato')

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------
    
    def test__three_column_noheader__csv(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "three-column-noheader.csv",
                "File Type": "CSV",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(str(sheet.coalesce("Color", 0).value), "Red")
            self.assertEqual(str(sheet.coalesce("Color", 4).value), "Blue")
            self.assertEqual(sheet.coalesce("Local Value").value, None)
            self.assertEqual(sheet.coalesce("Local Value", 0).value, None)

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------

    def test__header_only__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "header-only.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 1)
            self.assertEqual(str(sheet.coalesce("Serial Number").value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Color").value), "Red")

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 1).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    
    def test__one_column_header__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "one-column-header.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(sheet.coalesce("Serial Number").value, None)
            self.assertEqual(sheet.coalesce("Serial Number", 0).value, 101)
            self.assertEqual(sheet.coalesce("Serial Number", 4).value, 105)
            self.assertEqual(sheet.coalesce("Inherited Value").value, 343)
            self.assertEqual(sheet.coalesce("Inherited Value", 0).value, 343)
            self.assertEqual(sheet.coalesce("Inherited Value", 4).value, 343)
            self.assertEqual(sheet.coalesce("Local Value").value, 'potato')
            self.assertEqual(sheet.coalesce("Local Value", 0).value, 'potato')

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------

    def test__one_column_noheader__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "one-column-noheader.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(sheet.coalesce("Serial Number").value, None)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(sheet.coalesce("Local Value").value, None)
            self.assertEqual(sheet.coalesce("Local Value", 0).value, None)

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    
    def test__two_column_header__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "two-column-header.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(sheet.coalesce("Serial Number").value, None)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(str(sheet.coalesce("Local Value").value), 'potato')
            self.assertEqual(str(sheet.coalesce("Local Value", 0).value), 'potato')

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    
    def test__two_column_noheader__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "two-column-noheader.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(sheet.coalesce("Local Value").value, None)
            self.assertEqual(sheet.coalesce("Local Value", 0).value, None)

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------
    
    def test__three_column_header__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "three-column-header.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(str(sheet.coalesce("Color", 0).value), "Red")
            self.assertEqual(str(sheet.coalesce("Color", 4).value), "Blue")
            self.assertEqual(str(sheet.coalesce("Local Value").value), 'potato')
            self.assertEqual(str(sheet.coalesce("Local Value", 0).value), 'potato')

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------
    
    def test__three_column_noheader__xlsx(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Item",
                "Source": "Sheet Test",
                "File": "three-column-noheader.xlsx",
                "Sheet": "Sheet1",
                "File Type": "Excel",
                "Values":
                {
                    "Inherited Value": 343,
                },
            }

            sheet = Sheet(sheet_info)
            self.assertEqual(sheet.rows, 5)
            self.assertEqual(str(sheet.coalesce("Serial Number", 0).value), "101")
            self.assertEqual(str(sheet.coalesce("Serial Number", 4).value), "105")
            self.assertEqual(str(sheet.coalesce("Inherited Value").value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 0).value), "343")
            self.assertEqual(str(sheet.coalesce("Inherited Value", 4).value), "343")
            self.assertEqual(str(sheet.coalesce("Flavor", 0).value), "Strawberry")
            self.assertEqual(str(sheet.coalesce("Flavor", 4).value), "Blueberry")
            self.assertEqual(str(sheet.coalesce("Color", 0).value), "Red")
            self.assertEqual(str(sheet.coalesce("Color", 4).value), "Blue")
            self.assertEqual(sheet.coalesce("Local Value").value, None)
            self.assertEqual(sheet.coalesce("Local Value", 0).value, None)

            with self.assertRaises(IndexError):
                v = sheet.coalesce("Serial Number", 5).value
        
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}

    #-----------------------------------------------------------------------------
    #============================================================================= 

if __name__ == "__main__":
    unittest.main()
