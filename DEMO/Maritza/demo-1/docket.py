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
        "Part Type ID": "Z00100300029",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.fribble",
    })

# Append some sources
src_item = {
        "Source Name": "Item Source",
        "Files": "SiPM-item-manifest.xlsx",
        "Encoder": "Item Encoder",
        "Values":
        {
            "Enabled": True,
        }
    }

src_dnsc = {
        "Source Name": "Dark Noise SiPM Counts",
        "Files": "Dark-noise-SiPM-counts.xlsx",
        "Encoder": "Dark Noise SiPM Counts Encoder",
    }

src_char = {
        "Source Name": "IV SiPM Characterization",
        "Files": "IV-SiPM-characterization.xlsx",
        "Encoder": "IV SiPM Characterization Encoder",
    }

src_noise = {
        "Source Name": "IV SiPM Noise Test",
        "Files": "IV-SiPM-noise-test.xlsx",
        "Encoder": "IV SiPM Noise Test Encoder",
    }

src_mass = {
        "Source Name": "SiPM Mass Test",
        "Files": "SiPM-mass-test-results.xlsx",
        "Encoder": "SiPM Mass Test Encoder",
    }

#contents["Sources"].append(src_item)
#contents["Sources"].append(src_dnsc)
#contents["Sources"].append(src_char)
#contents["Sources"].append(src_noise)
contents["Sources"].append(src_mass)

# Append some encoders
enc_item = {
        "Encoder Name": "Item Encoder",
        "Record Type": "Item",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.fribble",
        "Part Type ID": "Z00100300029",
        "Schema":
        {
            "Manufacturer Name":
            {
                "column": "Manufacturer",  
            },
            "Manufacturer":
            {
                "value": None,
            },
            "Specifications":
            {
                "SiPM_Strip_ID": "string",
                "Vendor": "string",
                "Vendor_Delivery_ID": "string",
                "Vendor_Box_Number": "integer",
                "Tray_Number": "integer",
                "Test_Box_ID": "string",
                "Documentation": "string",
            }
        }
    }

enc_dnsc = {
        "Encoder Name": "Dark Noise SiPM Counts Encoder",
        "Record Type": "Test",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        "Part Type ID": "Z00100300025",
        "Test Name": "Dark Noise SiPM Counts",
        "Schema":
        {
            "Serial Number":
            {
                "type": "null,string",
                "column": "SiPM_Strip_ID",
            },
            "Test Results":
            {
                "DATA":
                {
                    "type": "group",
                    "key": ["Date", "Location"],
                    "members":
                    {
                        "Date": "string",
                        "Location": "string",
                        "Operator": "string",
                        "Thermal_Cycle": "integer",
                        "Polarization": "string",
                        "Temperature": "string",
                        "Acquisition_Time": "integer",
                        "Weighted_Threshold_Charge": "integer",
                        "SiPM":
                        {
                            "type": "group",
                            "key": "SiPM_Location",
                            "members":
                            {
                                "SiPM_Location": "integer",
                                "OV": "integer",
                                "Status": "string",
                                "Comment": "string",
                            }
                        }
                    }
                }
            }
        }
    }

enc_char = {
        "Encoder Name": "IV SiPM Characterization Encoder",
        "Record Type": "Test",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        "Part Type ID": "Z00100300025",
        "Test Name": "IV SiPM Characterization",
        "Schema":
        {
            "Serial Number":
            {
                "type": "null,string",
                "column": "SiPM_Strip_ID",
            },
            "Test Results":
            {
                "DATA":
                {
                    "type": "group",
                    "key": ["Date", "Location"],
                    "members":
                    {
                        "Date": "string",
                        "Location": "string",
                        "Operator": "string",
                        "Thermal_Cycle": "integer",
                        "Polarization": "string",
                        "Temperature": "string",
                        "R_cable": "float",
                        "R_eff": "float",
                        "SiPM":
                        {
                            "type": "group",
                            "key": "SiPM_Location",
                            "members":
                            {
                                "SiPM_Location": "integer",
                                "V": "array",
                                "I": "array",
                                "Fit_range_low": "float,null",
                                "Fit_Polynomial_Degree": "integer,null",
                                "Status": "string",
                                "Comment": "string",
                            }
                        }
                    }
                }
            }
        }
    }

enc_noise = {
        "Encoder Name": "IV SiPM Noise Test Encoder",
        "Record Type": "Test",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        "Part Type ID": "Z00100300025",
        "Test Name": "IV SiPM Noise Test",
        "Schema":
        {
            "Serial Number":
            {
                "type": "null,string",
                "column": "SiPM_Strip_ID",
            },
            "Test Results":
            {
                "DATA":
                {
                    "type": "group",
                    "key": ["Date", "Location"],
                    "members":
                    {
                        "Date": "string",
                        "Location": "string",
                        "Operator": "string",
                        "Thermal_Cycle": "integer",
                        "Polarization": "string",
                        "Temperature": "string",
                        "SiPM":
                        {
                            "type": "group",
                            "key": "SiPM_Location",
                            "members":
                            {
                                "SiPM_Location": "integer",
                                "V": "array",
                                "I": "array",
                                "I_Range": "array",
                                "I_Mean": "float",
                                "I_Sigma": "float",
                                "I_End_Range": "float",
                                "Nsigma": "integer",
                                "Status": "string",
                                "Comment": "string",
                            }
                        }
                    }
                }
            }
        }
    }

enc_mass = {
        "Encoder Name": "SiPM Mass Test Encoder",
        "Record Type": "Test",
        "Part Type Name": "Z.Sandbox.HWDBUnitTest.wibble",
        "Part Type ID": "Z00100300025",
        "Test Name": "SiPM Mass Test",
        "Schema":
        {
            "Serial Number":
            {
                "type": "null,string",
                "column": "SiPM_Strip_ID",
            },
            "Test Results":
            {
                "DATA":
                {
                    "type": "group",
                    "key": ["Date", "Location"],
                    "members":
                    {
                        "Date": "string",
                        "Location": "string",
                        "Operator": "string",
                        "Thermal_Cycle": "integer",
                        "Polarization": "string",
                        "Temperature": "string",
                        "Manufacturer": "string",
                        "Measured_Attribute": "string",
                        "SiPM":
                        {
                            "type": "group",
                            "key": "SiPM_Location",
                            "members":
                            {
                                "SiPM_Location": "integer",
                                "Result": "float",
                                "Result_Err": "float",
                                "Strip_Avg_Result": "float",
                            }
                        }
                    }
                }
            }
        }
    }

contents["Encoders"].append(enc_item)
contents["Encoders"].append(enc_dnsc)
contents["Encoders"].append(enc_char)
contents["Encoders"].append(enc_noise)
contents["Encoders"].append(enc_mass)


# The following code is not necessary. It merely displays the resulting JSON
# version of the docket, if this script is run directly. It may be useful for
# troubleshooting.
if __name__ == '__main__':
    import json
    print(json.dumps(contents, indent=4))



























