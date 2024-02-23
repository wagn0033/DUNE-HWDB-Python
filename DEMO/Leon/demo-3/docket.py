#!/usr/bin/env python
# -*- coding: utf-8 -*-

# When creating a docket as a Python script, you are free to do this however
# you like, as long as at the end of execution, there is a local variable
# named "contents" that contains the same structure you would have provided
# as a JSON file.

contents = \
{
    "Sources": [],
    "Encoders": [],
    "Values": {},
}

# Append some global values
# Values can also be set at the Source or Sheet level, but they must not 
# conflict with a value set higher up the chain. If a value needs to be
# different things in different places, set them at the level that they
# are needed, not at the global level.
# This was a design choice we made to reduce the chances of causing hidden
# problems that are hard for the end-user to track down. It would be easier
# to just allow overriding, so if this feature proves unpopular, we could
# change it.
contents["Values"].update(
    {
        "Part Type ID": "Z00100300025",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        "Institution Name": "Cal%Tech%",
        "Country Code": "US",
        "Manufacturer": "(50)%",
        #"Manufacturer Name": "Acme%",
        #"Manufacturer ID": 7,
        "Enabled": True,
    })

# Append some sources
src_item = {
        "Source Name": "Item Source",
        "Files": "bps-summary-item.csv",
        "Encoder": "Item Encoder",
    }

src_test_netconf = {
        "Source Name": "Net Config",
        "Files": "netconfig*.csv",
        "Encoder": "Net Config",
    }

src_test_bpssummary = {
        "Source Name": "BPS Summary",
        "Files": "bps-summary*.csv",
        "Encoder": "BPS-Summary",
    }

contents["Sources"].append(src_item)
contents["Sources"].append(src_test_bpssummary)
#contents["Sources"].append(src_test_netconf)
#contents["Sources"].append(src_test_bpssummary)

# Append some encoders
enc_item = {
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
                "DUNE HWDB Utility Version": "str",
                "DATA":
                {
                    "type": "obj",
                    "value": {},
                }
            }
        }
    }

enc_test_netconf = {
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
                    "key": "timestamp",
                    "members":
                    {
                        "timestamp": 
                        {
                            "column": "TestTime",
                            "type": "number",
                        },
                        "TestTime":
                        {
                            "column": "TestTime",
                            "type": "unixtime",
                        },
                        "init_chip_results": "int",
                    }
                }
            }
        }
    }

enc_test_bpssummary = {
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
                            }
                        }
                    }
                }
            }
        }
    }

contents["Encoders"].append(enc_item)
contents["Encoders"].append(enc_test_netconf)
contents["Encoders"].append(enc_test_bpssummary)


#import json
#print(json.dumps(contents, indent=4))
#breakpoint()


