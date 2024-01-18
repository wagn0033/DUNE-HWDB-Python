#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUtility/HWDBItem.py
Copyright (c) 2024 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut
from Sisyphus.Utils.Terminal.Style import Style

import json
import sys
import os
from copy import deepcopy
import re
import time
import random

_HWItem_cache = {}

class HWItem:

    #{{{
    # Map the "column" name to the "property" name
    _column_to_property = \
    {
        "Part Type ID": "part_type_id",
        "Part Type Name": "part_type_name",
        "Serial Number": "serial_number",
        "External ID": "part_id",
        "Institution": "institution",
        "Institution Name": "institution_name",
        "Institution ID": "institution_id",
        "Country": "country",
        "Country Name": "country_name",
        "Country Code": "country_code",
        "Manufacturer": "manufacturer",
        "Manufacturer Name": "manufacturer_name",
        "Manufacturer ID": "manufacturer_id",
        "Item Comments": "comments",
        "Subcomponents": "subcomponents",
        "Specifications": "specifications",
        "Enabled": "enabled",
    }
    _property_to_column = {v: k for k, v in _column_to_property.items()}
    #}}}

    # TODO: we need a bunch of property getters/setters, but 
    # we can get away without them for a while because we
    # aren't using this interactively.

    #--------------------------------------------------------------------------

    def __init__(self, *, AreYouSure=False):
        #{{{
        """Do not create new HWItem instances directly!

        The object needs to know where the data came from in order to
        function correctly. Use "fromUserData" to create a new instance
        from a user source such as a spreadsheet, and "fromHWDB" to pull
        an existing HWItem from the database.
        """        
        if not AreYouSure:
            raise ValueError("Don't create new HWItems this way "
                            "unless you know what you're doing!")

        self._last_commit = {k: None for k in self._property_to_column.keys()}
        self._current = deepcopy(self._last_commit)
        self._is_new = False    
        #}}}
    #--------------------------------------------------------------------------

    def toUserData(self):
        user_record = {col_name: self._current[prop_name] 
                for col_name, prop_name in self._column_to_property.items()}
        return user_record

    #--------------------------------------------------------------------------
    @classmethod
    def fromUserData(cls, user_record):
        #{{{
        #{{{
        """Create a HWItem from user data

        Typically, this means the data read from a spreadsheet and encoded
        by an Encoder.

        After creating the HWItem instance, it will attempt to find the item
        in the HWDB using the External ID or the Part Type and Serial Number.
        If it is found, it will keep an internal copy of the data in the
        HWDB so that it can be determined whether the data has changed and 
        needs to be updated.

        Because the REST API does not provide a means of updating the entire
        HWItem all at once, there are several methods for checking for changes
        and for making updates. This is helpful if you are adding a bunch of
        HWItems at the same time, and subcomponents for this HWItem may not 
        have been added yet. I.e., you can just update the 'core' part of the
        data and come back to finish it after all the other items have been
        added.

        "record" format:
        ================
        {
            "Part Type ID": "Z00100300022",
            "Part Type Name": "Z.Sandbox.HWDBUnitTest.biff",
            "Serial Number": "059313D3-B728-4C3D-857C-1AB9DAC93232",
            "External ID": "Z00100300022-00057",
            "Institution ID": 186,
            "Institution Name": "University of Minnesota Twin Cities",
            "Country Name": "United States",
            "Country Code": "US",
            "Manufacturer ID": 7,
            "Manufacturer Name": "Hajime Inc",
            "Item Comments": "generated 2023-10-17 09:39:48",
            "Enabled": true,
            "Specifications": [
                {
                    "Height": 97.42,
                    "Length": 119.76,
                    "Width": 85.56
                }
            ],
            "Subcomponents": {
                "Left Bongo": "Z00100300023-00104",
                "Right Bongo": "Z00100300023-00105"
            },
            "Country": "(US) United States",
            "Institution": "(186) University of Minnesota Twin Cities",
            "Manufacturer": "(7) Hajime Inc"
        }
        """
        #}}}
        new_hwitem = HWItem(AreYouSure=True)
        user_record = deepcopy(user_record)

        try:
            hwdb_record = cls._get_from_hwdb(
                    part_type_id=user_record.get("Part Type ID", None),
                    part_type_name=user_record.get("Part Type Name", None),
                    part_id=user_record.get("External ID", None),
                    serial_number=user_record.get("Serial Number", None))
            new_hwitem._is_new = False
            new_hwitem._last_commit = hwdb_record
        #except ra.AmbiguousParameters as exc:        
        except ra.NotFound:
            # This is fine. It just means that it's new!
            new_hwitem._is_new = True


        for col_name, prop_name in cls._column_to_property.items():
            if col_name not in user_record:
                logger.warning(f"{col_name} not in user_record")
            else:
                new_hwitem._current[prop_name] = user_record.pop(col_name)
        if len(user_record) > 0:
            logger.warning(f"extra columns in user_record: {tuple(user_record.keys())}")
        return new_hwitem
        #}}}

    #--------------------------------------------------------------------------

    @classmethod
    def fromHWDB(cls, part_type_id=None, part_type_name=None, part_id=None, serial_number=None):
        #{{{
        """Create a new HWItem instance by downloading an item from the HWDB

        The arguments supplied must be sufficient to uniquely describe one
        item in the HWDB.
        """

        hwdb_record = cls._get_from_hwdb(part_type_id, part_type_name, part_id, serial_number)
        new_hwitem = HWItem(AreYouSure=True)

        new_hwitem._last_commit = deepcopy(hwdb_record)
        new_hwitem._current = deepcopy(hwdb_record)
        return new_hwitem
        #}}}
    #--------------------------------------------------------------------------

    @classmethod
    def _get_from_hwdb(cls, part_type_id=None, part_type_name=None, part_id=None, serial_number=None):
        #{{{
        """(internal method) Load HWItem data from the HWDB"""

        hwitem_raw = ut.fetch_hwitems(
                part_type_id, part_type_name, part_id, serial_number, count=2)

        Style(fg="magenta").print(json.dumps(hwitem_raw, indent=4))

        # Raise an exception if no records are found, or more than one is found.
        if len(hwitem_raw) == 0:
            raise ra.NotFound("The arguments provided did not matchy any HWItems.")
        elif len(hwitem_raw) > 1:
            # TODO: we could still cache it for later.
            raise ra.AmbiguousParameters("The arguments provided matched more than one HWItem.")

      
        # We still need a bit of extra data before we can create the record  
        _, item_node = hwitem_raw.popitem()
        it = item_node["Item"]
        sc = item_node["Subcomponents"] 
        ct_all = ut.fetch_component_type(part_type_id=it["component_type"]["part_type_id"])
        ct = ct_all["ComponentType"]
       
        hwdb_record = (
        {
            "part_type_id": ct["part_type_id"],
            "part_type_name": ct["full_name"],
            "serial_number": it["serial_number"],
            "part_id": it["part_id"],
            "institution_id": it["institution"]["id"],
            "institution_name": it["institution"]["name"],
            "country_name": ut.lookup_country_name_by_country_code(it["country_code"]),
            "country_code": it["country_code"],
            "manufacturer_id": it["manufacturer"]["id"],
            "manufacturer_name": it["manufacturer"]["name"],
            "comments": it["comments"],
            "enabled": it["enabled"],
            "specifications": it["specifications"],
            "subcomponents": {k:v for k, v in sorted
                            ([(x["functional_position"], x["part_id"]) for x in sc])},
        })
        hwdb_record["country"] = (f"({hwdb_record['country_code']}) "
                                    f"{hwdb_record['country_name']}")
        hwdb_record["institution"] = (f"({hwdb_record['institution_id']}) "
                                    f"{hwdb_record['institution_name']}")
        hwdb_record["manufacturer"] = (f"({hwdb_record['manufacturer_id']}) "
                                    f"{hwdb_record['manufacturer_name']}")

        Style(fg="darkgoldenrod").print(json.dumps(hwdb_record, indent=4))

        return hwdb_record
        #}}}
    
    #--------------------------------------------------------------------------

    @classmethod
    def user_role_check(cls, part_type_id=None, part_type_name=None):
        #{{{
        """Checks if the user is permitted to work with this ComponentType"""
        # TODO: maybe this needs to be part of a ComponentType class instead?

        return ut.user_role_check(part_type_id, part_type_name)
        #}}}


    #--------------------------------------------------------------------------
    def is_new(self):
        """Tell whether this HWItem is new and is not in the HWDB yet"""
        return self._is_new
    #--------------------------------------------------------------------------

    def update_core(self):
        """Update the 'core' properties of this HWItem in the HWDB

        The 'core' properties are those properties that can be updated by the
        main REST API call, and does not include 'enabled' or subcomponents.
        """

    #--------------------------------------------------------------------------

    def update_enabled(self):
        """Update the 'enabled' property of this HWItem in the HWDB"""

    #--------------------------------------------------------------------------
    def update_subcomponents(self):
        """Update the subcomponents for this HWItem, if able

        Use subcomponents_updatable to check first before calling this
        method.
        """

    #--------------------------------------------------------------------------
    def subcomponents_updatable(self):
        """Check if the subcomponents for this HWItem are available

        Subcomponents are not updatable if:
            (1) They haven't been added to the HWDB yet
            (2) They aren't enabled in the HWDB yet
            (3) They already are attached to another HWItem and need to be
                released first
        """
    #--------------------------------------------------------------------------

    def validate(self):
        """Tests whether this HWItem appears to be valid

        Checks that all required 'core' data exists and appears to meet
        requirements in the ComponentType definition.
        """

    #--------------------------------------------------------------------------


    def update(self):
        """Update the 'core' properties, 'enabled', and subcomponents"""
    #--------------------------------------------------------------------------

    def resync(self):
        """Download this HWItem from the HWDB and overwrite current properties"""
        # TODO: maybe I don't need this at all

    #--------------------------------------------------------------------------

    def verify(self):
        """Download this HWItem from the HWDB and check for equivalence"""
        # TODO: maybe I don't need this at all

    #--------------------------------------------------------------------------

    def core_has_changed(self):
        """Tell whether the 'core' properties have changed since downloading"""
    
    #--------------------------------------------------------------------------

    def enabled_has_changed(self):
        """Tell whether the 'enabled' property has changed since downloading"""
    
    #--------------------------------------------------------------------------

    def subcomponents_have_changed(self):
        """Tell whether the subcomponents have changed since downloading"""
    
    #--------------------------------------------------------------------------

    def has_changed(self):
        """Tell whether anything has changed since downloading"""
    
    #--------------------------------------------------------------------------


class ComponentType:
    ...


class HWTest:
    ...


class HWTestDef:
    ...


if __name__ == "__main__":
    pass






















