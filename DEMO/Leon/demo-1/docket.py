#!/usr/bin/env python
# -*- coding: utf-8 -*-

contents = \
{
    "Sources":
    [
        {
            "SourcE Name": "BPS Summary (as item source)",
            "FileS": "bps-summary*.csv",
            "ValUes":
            {
                "Record Type": "Item",
                "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                "Part Type ID": "Z00100300025",
                "Country Code": "US",
                "Institution ID": 129,
                "Manufacturer ID": 50,
                "SpecData": None,
            }
        },
        #{
        #    "Source Name": "BPS Summary (as test)",
        #    "Files": "bps-summary*.csv",
        #    "Values":
        #    {
        #        "Record Type": "Test",
        #        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        #        "Part Type ID": "Z00100300025",
        #        "Test Name": "BPS-Summary",
        #        "Encoder": "BPS-Summary",
        #    }
        #},
        #{
        #    "Source Name": "Net Config",
        #    "Files": "netconfig*.csv",
        #    "Values":
        #    {
        #        "Record Type": "Test",
        #        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        #        "Part Type ID": "Z00100300025",
        #        "Test Name": "Net-Config",
        #        "Encoder": "Net-Config",
        #    }
        #},
        {
            "Source Name": "Fake",
            "Files": "fake.xlsx",
            "Sheets":
            [
                {
                    "Sheet Name": "Sheet1",
                    "Values":
                    {
                        "Record Type": "Test",
                        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                        "Part Type ID": "Z00100300025",
                        "Test Name": "Fake",
                    }
                }
            ],
            "Values": {'a': 1, 'Record Type': 'Test'},

        },
        {
            "Source Name": "Fake",
            "Files": "fake.xlsx",
        },


    ],
    "Encoders":
    [
        {
            "Encoder Name": "BPS-Summary",
            "Record Type": "Test",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Test Name": "BPS-Summary",
            "Schema": {}
        },
        {
            "Encoder Name": "Net-Config",
            "Record Type": "Test",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Test Name": "Net-Config",
            "Schema": {}
        }
    ]
}






