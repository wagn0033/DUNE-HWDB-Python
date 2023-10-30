#!/usr/bin/env python
# -*- coding: utf-8 -*-
# """
# test/HWDBUploader/001/docket.py
# Copyright (c) 2023 Regents of the University of Minnesota
# Author: 
#     Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
# """

contents = \
{
    "Docket Name": "Docket 001",
    "Sources":
    [
        {
            "Source Name": "Bongos and Biffs",
            "Files": "Upload_SN.xlsx",
            "Sheets": 
            [   
                {
                    "Sheet Name": "Bongo-Items",
                    "Sheet Type": "Item",
                    "Values":
                    {
                        "Type ID": "Z00100300023"
                    }
                },
                {
                    "Sheet Name": "Biff-Items",
                    "Sheet Type": "Item",
                    "Values":
                    {
                        "Type Name": "Z.Sandbox.HWDBUnitTest.biff"
                    }
                }
            ]
        }
    ],
    "Encoders": []
}
