#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Author: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.HWDBUploader import Sheet
from Sisyphus.HWDBUploader import Encoder

import unittest
import json


#{{{
encoder_DNSC = \
{
    "Encoder Name": "Dark Noise SiPM Counts",
    "Record Type": "Test",
    "Part Type Name": "Z.Sandbox.HWDBUnitTest.snork",
    #"Part Type ID": "Z00100300022",
    "Test Name": "Dark Noise SiPM Counts",

    "Options":
    {
        "Create Missing Item": False,
        "Case Lenience": False,
        "Space Lenience": False,
        "Item Key Duplication": "warning", # "overwrite", "disallow"
        "Test Key Duplication": "warning", # "overwrite", "disallow"
        "Sparse Sheet": False,
    },
    
    "Schema": # Indicates where to find the values to populate the record
    {
        # "Implied" fields don't need to be stated unless they're being
        # pulled from another column.
        "Serial Number":
        {
            "type": "string,null",
            "column": "SiPM_Strip_ID",
            "value": "${SiPM_Strip_ID}"
            #"default": None,
        },
        # "External ID":
        # {
        #     "type": "string",
        #     "column": ("External ID", "External_ID", "Part ID", "Part_ID"), 
        # },

        ## For "Item" type only
        # "Institution": 186
        # "Country": "US",
        # "Manufacturer": "??", # Name? ID? 
        # "Comments": "",
        # "Subcomponents": {},
        # "Specifications": {},
        # "Enabled": True, # defaults to True

        ## For "Test" type only
        #"Comments": "",
        "Test Results":
        {
            # implied that this is a type "group" and these are the members
            # there are no keys, except possibly the SN/EID might be considered one

            "SiPM_Strip_ID": "string",
            "Content Manager":
            {
                "type": "string",
                "value": "HWDB Python Utility",
            },
            "Contents":
            {
                "type": "group",
                "key": ["Date", "Location"],
                "members":
                {
                    "SiPM_Strip_ID": "string",
                    "Date": "string",
                    "Location": "string",
                    "Operator": "string",
                    "Thermal_Cycle": "integer",
                    "Polarization": "string",
                    "Temperature": "string",
                    "Acquisition_Time": "float",
                    "Weighted_Threshold_Charge": "integer",
                    "(SiPM Location)":
                    {
                        "type": "group",
                        "key": ["SiPM_Location"],
                        "members":
                        {
                            "SiPM_Location": "integer",
                            "OV": "float",
                            "Counts": "integer",
                            "Status": "string",
                            "Comment": "string"
                        },
                    }
                },
            }
        }
    }
}
#}}}

class Test__Encoder(unittest.TestCase):

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

    def test__Encoder_encode(self):
        #{{{
        try:
            sheet_info = \
            {
                "Record Type": "Test",
                "Source": "Encoder Test",
                "File": "Dark-noise-SiPM-counts.xlsx",
                "File Type": "Excel",
                "Sheet": "Sheet1",
                "Values":
                {
                    "Part Type Name": "Z.Sandbox.HWDBUnitTest.snork",
                },
            }

            sheet = Sheet.Sheet(sheet_info)

            #print(sheet.dataframe)

            encoder = Encoder.Encoder(encoder_DNSC)

            result = encoder.encode(sheet)
            print(json.dumps(result, indent=4))
 
        except AssertionError as err:
            logger.error(f"AssertionError: {err}")
            raise err
        #}}}
    
    #-----------------------------------------------------------------------------
    #============================================================================= 

if __name__ == "__main__":
    unittest.main()
