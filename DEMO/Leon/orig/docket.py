#!/usr/bin/env python
# -*- coding: utf-8 -*-

contents = \
{
    "Sources":
    [
        {
            "Source Name": "BPS Summary (as item source)",
            "Files": "bps-summary*.csv",
            "Values":
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
        {
            "Source Name": "BPS Summary (as test)",
            "Files": "bps-summary*.csv",
            "Values":
            {
                "Record Type": "Test",
                "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                "Part Type ID": "Z00100300025",
                "Test Name": "BPS-Summary",
                "Encoder": "BPS-Summary",
            }
        },
        {
            "Source Name": "Net Config",
            "Files": "netconfig*.csv",
            "Values":
            {
                "Record Type": "Test",
                "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                "Part Type ID": "Z00100300025",
                "Test Name": "Net-Config",
                "Encoder": "Net-Config",
            }
        },
    ],
    "Encoders":
    [
        {
            "Encoder Name": "BPS-Summary",
            "Record Type": "Test",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Test Name": "BPS-Summary"
        },
        {
            "Encoder Name": "Net-Config",
            "Record Type": "Test",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Test Name": "Net-Config"
        }
    ]
}






