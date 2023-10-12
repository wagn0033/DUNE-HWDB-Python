#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApiV1/Utilities.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import Sisyphus.RestApiV1 as ra


#######################################################################

def lookup_part_type_id_by_fullname(fullname):

    # The full name should be formatted as [ProjID].[SystemName].[SubsytemName].[PartName],
    # so there should be exactly 3 periods.
    try:
        project_id, system_name, subsystem_name, part_name = fullname.split('.')
    except ValueError:
        msg = f"Part name '{fullname}' is invalidly formatted"
        logger.error(msg)
        raise ValueError(msg)


    resp = ra.get_component_types(project_id.upper(), 0, 0, full_name=fullname)

    if resp["status"] != "OK":
        msg = "There was a problem obtaining the part type ID from the server"
        logger.error(msg)
        raise RuntimeError(msg)

    if len(resp['data']) == 0:
        msg = f"The full part name '{fullname}' cannot be found"
        logger.error(msg)
        raise ValueError(msg)

    if len(resp['data']) > 1:
        msg = f"The full part name '{fullname}' is ambiguous"
        logger.error(msg)
        raise ValueError(msg)

    return (resp['data'][0]['full_name'], resp['data'][0]['part_type_id'])

#######################################################################

def lookup_component_type_defs(part_type_id):

    # TBD: NEED SOME ERROR HANDLING!!!

    type_info = {"part_type_id": part_type_id}

    resp = ra.get_component_type(part_type_id) 
    if resp["status"] != "OK":
        raise ValueError("Component type lookup failed.")
    
    type_info["full_name"] = resp['data']['full_name']
    type_info["spec_def"] = resp['data']['properties']['specifications'][0]['datasheet']
    type_info["subcomponents"] = resp['data']['connectors']

    resp = ra.get_test_types(part_type_id)
    if resp["status"] != "OK":
        raise ValueError("Test type lookup failed.")
    type_info["tests"] = [
        {
            "test_name": node["name"],
            "test_type_id": node["id"]
        }
        for node in resp['data']
    ]

    for node in type_info["tests"]:
        resp = ra.get_test_type(part_type_id, node["test_type_id"])
        if resp["status"] != "OK":
            raise ValueError("Test type definition lookup failed.")
        node["test_def"] = resp['data']['properties']['specifications'][0]['datasheet']
    return type_info

#######################################################################

def lookup_institution_by_id(inst_id):
    if not hasattr(lookup_institution_by_id, "_cache"):
        inst_list = ra.get_institutions()['data']
        lookup_institution_by_id._cache = { inst_item['id']: inst_item for inst_item in inst_list }

    return lookup_institution_by_id._cache[inst_id]


#######################################################################

def bulk_add_hwitems(part_type_id, count, *, 
                    institution_id = None,
                    country_code = None, 
                    manufacturer_id = None,
                    comments = None):
    data = {
        'component_type': {'part_type_id': part_type_id}, 
        'count': count,
    }

    if comments is not None:
        data['comments'] = comments

    if institution_id is None:
        raise ValueError("institution_id is required")
    else:
        data['institution'] = {'id': institution_id}

    if country_code is None:
        country_code = lookup_institution_by_id(institution_id)["country"]["code"]
    data['country_code'] = country_code

    if manufacturer_id is not None:
        data['manufacturer'] = {'id': manufacturer_id}

    resp = ra.post_bulk_hwitems(part_type_id, data)
    
    if resp["status"] != "OK":
        raise ValueError("Bulk add failed")

    return [item["part_id"] for item in resp['data']]

#######################################################################

def enable_hwitem(part_id, *,
                    enable=True,
                    comments=None):
    data = {
        'component': {'part_id': part_id},
        'enabled': enable,
    }

    if comments is not None:
        data["comments"] = comments
    
    resp = ra.patch_part_id_enable(part_id, data)

    if resp["status"] != "OK":
        raise ValueError(f"Enable '{part_id}' failed")

    return resp

#######################################################################

def set_subcomponents(part_id, subcomponents):

    data = \
    {
        "component": {"part_id": part_id},
        "subcomponents": subcomponents,
    }

    resp = ra.patch_subcomponents(part_id, data)
    if resp["status"] != "OK":
        raise RuntimeError("Error setting subcomponents")

    return resp
