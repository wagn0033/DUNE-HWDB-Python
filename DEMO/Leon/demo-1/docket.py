#!/usr/bin/env python
# -*- coding: utf-8 -*-

src_netconfig = \
        {
            "Source Name": "Net Config",
            "Files": "netconfig*.csv",
            "Values":
            {
                "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                "Part Type ID": "Z00100300025",
                "Institution Name": "Cal%Tech%",
                "Manufacturer ID": 50,
                "Enabled": True,
            },
            "Encoder": "Net Config",
        }

enc_netconfig = \
        {
            "Encoder Name": "Net Config",
            "Record Type": "Test",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Test Name": "Net Config",
            "Schema":
            {
                "Serial Number":
                {
                    "type": "null,string",
                    "column": "ChipSN",
                },
                "Test Results":
                {
                    "DUNE HWDB Utility Version": "str",
                    "DATA":
                     {
                        "type": "group",
                        "key": "TestTime",
                        "members":
                        {
                            "TestTime": "number",
                            "init_chip_results": "int",
                        }
                    }
                }
            }
        }


contents = \
{
    "Sources":
    [
        {
            "Source Name": "Item Source",
            "Files": "bps-summary*-truncated.csv",
            "Values":
            {
                "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                "Part Type ID": "Z00100300025",
                "Country Code": "US",
                "Institution Name": "Cal%Tech%",
                "Manufacturer ID": 50,
                "Enabled": True,
            },
            "Encoder": "Item Encoder",
        },
        {
            "Source Name": "BPS Summary",
            "Files": "bps-summary*-truncated.csv",
            "Values":
            {
                "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
                "Part Type ID": "Z00100300025",
            },
            "Encoder": "BPS-Summary",
        },
        src_netconfig,
    ],
    "Encoders":
    [
        {
            "Encoder Name": "Item Encoder",
            "Record Type": "Item",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Schema": 
            {
                "Serial Number":
                {
                    "type": "null,string",
                    "column": "ChipSN",
                },
                "Specifications":
                {
                    "DATA":
                    {
                        "type": "obj",
                        "value": 
                        {
                            "testing 1": "1234", 
                            "testing 2": "ABC"
                        },
                    }
                }
            }
        },
        {
            "Encoder Name": "BPS-Summary",
            "Record Type": "Test",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
            "Part Type ID": "Z00100300025",
            "Test Name": "BPS Summary",
            "Schema": 
            {
                "Serial Number":
                {
                    "type": "null,string",
                    "column": "ChipSN",
                },
                "Test Results":
                {
                    "DUNE HWDB Utility Version": "str",
                    "DATA":
                     {
                        "type": "group",
                        "key": "runtime",
                        "members":
                        {
                            "runtime": "number",
                            "channels":
                            { 
                                "type": "group",
                                "key": "ChanName",
                                "members":
                                {
                                    "ChanName": "str",
                                    "Chan": "int",
                                    "Mean": "float",
                                    "Std": "float",
                                    "Nent": "int",
                                    "io_group": "int",
                                    "io_channel": "int",
                                },
                            },
                        },
                    }
                }
            }
        },
        enc_netconfig,
    ]
}






