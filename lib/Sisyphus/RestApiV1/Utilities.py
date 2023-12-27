#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApiV1/Utilities.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
from Sisyphus.RestApiV1.keywords import *

import sys
from copy import deepcopy
import multiprocessing.dummy as mp # multiprocessing interface, but uses threads instead
from collections import namedtuple

#######################################################################

PartType = namedtuple('PartType', ['id', 'name'])

#######################################################################

def fetch_component_type(part_type_id=None, part_type_name=None, use_cache=True):
    #{{{
    '''Returns component type info for a part_type_id or a part_type_name.

    Does a lookup based on the ID or (full) name of a component type and
    returns a JSON record for that component type.

    The function will cache the result and return the cached result on 
    subsequent queries for the same component type. Setting use_cache to
    False will cause the function to fetch the data regardless of what's
    in the cache, but it will still cache its results to be available for
    future calls.

    Raises
    ------
    ra.MissingArguments
            Both part_type_id and part_type_name are None

    ra.IncompatibleArguments
            part type_id and part_type_name are both given, but they 
            do not resolve to the same component type.

    ra.NotFound
            The component type was not found in the database.

    ra.RestApiException
            This exception or exceptions inherited from this class may
            be raised for other errors during the execution of this
            function.
    ''' 
    
    logger.debug(f"looking up component type: part_type_id='{part_type_id}', "
                    f"part_type_name='{part_type_name}'")

    # Set up the caching
    def make_cache(fn, name, val):
        if not hasattr(fn, name):
            setattr(fn, name, val)
        return getattr(fn, name)
    _cache = make_cache(fetch_component_type, "_cache", {})

    # Make sure at least one argument is provided
    if part_type_id is None and part_type_name is None:
        msg = "at least one argument must be provided"        
        logger.error(msg)
        raise ra.MissingArguments(msg)
    
    # Since the HWDB expects part_type_id to be uppercase, and doesn't care
    # about the case of the part_type_name, we'll just make them both
    # uppercase for the sake of querying/caching. The actual data returned,
    # however, will have the correct case as stored in the HWDB.    
    if part_type_id is not None:
        part_type_id = part_type_id.upper()
    if part_type_name is not None:
        part_type_name = part_type_name.upper()

    # Because the name could contain wildcards (even unintentionally, because
    # unfortunately, the underscore is a wildcard), the safest thing to do is
    # to try to resolve the name (if given) and use that result along with
    # the id (if given) to see if the arguments are unambiguous. This might
    # result in one more call than necessary, but it's easier to just get
    # it out of the way.
    if part_type_name is not None:
        matches = [ rec.id for rec in lookup_part_type_by_name(part_type_name) ]
        if part_type_id is not None:
            # Since there's a part_type_id, we've already unambiguously
            # identified the component type. We just need to make sure
            # that it's somewhere in the matches.
            if part_type_id not in matches:
                msg = (f"part_type_name '{part_type_name}' is not consistent "
                        "with part_type_id '{part_type_id}")
                logger.error(msg)
                raise ra.IncompatibleArguments(msg)
        else:
            # No part_type_id, so the part_type_name MUST bring back 
            # EXACTLY one match. Set the part_type_id from that match,
            # and now we don't have to worry about it anymore.
            if len(matches) == 1:
                part_type_id = matches[0]
            else:
                msg = (f"No component type with part_type_name '{part_type_name}")
                logger.error(msg)
                raise ra.NotFound(msg)
                
    # Check for a cached result and use it if present
    if use_cache:
        if part_type_id in _cache:
            return _cache[part_type_id]
    
    # It was not in the cache, so now we'll have to look it up.
    retval = {}

    # Get the main component type record
    try:
        retval["ComponentType"] = ra.get_component_type(part_type_id)[ra.KW_DATA]
    except ra.DatabaseError as db_err:
        # Decide if this error was raised because there is no component
        # type with that part_type_id, or for some other reason we can't
        # anticipate
        if len(db_err.args) > 1 \
                and type(db_err.args[1]) == dict \
                and "No such component type" in db_err.args[1].get(ra.KW_DATA, ""):
            raise ra.NotFound(db_err.args[1][ra.KW_DATA]) from None
        else:
            raise db_err from None

    retval["TestTypes"] = ra.get_test_types(part_type_id)[ra.KW_DATA]
    
    
    retval["TestTypeDefs"] = {}
    for test_type in retval["TestTypes"]:
        retval["TestTypeDefs"][test_type["name"]] = \
                    ra.get_test_type(part_type_id, test_type["id"])

    _cache[part_type_id] = retval
    return retval
    #}}}

#######################################################################

def lookup_part_type_by_name(part_type_name, max_records=100):
    #{{{
    '''Looks up part_types matching part_type_name

    Find all part_types that match the part_type_name given. The 
    part_type_name must correspond with the full name of the component type,
    starting with the single-character project ID and a period, but PostGreSQL 
    wildcards are permitted for the remainder. E.g., you may search for 
    "Z.%.biff", but not "%.biff".

    Returns a list of "PartType" named tuples, containing both the
    part_type_id (as "id") and part_type_name (as "name").

    Searches are not case-sensitive, but results will contain the correct
    casing of the part type name as contained in the HWDB.

    Raises
    ------
    ValueError
        The part_type_name does not start with a single-character project ID
        and a period separator.
    ra.MaxRecordsExceeded
        More than max_records records were found.
        (If a use case requires handling an unlimited number of results, it
        is recommended that a new function be written that incorporates 
        pagination for that purpose. This function is intended to either
        look up a single part_type, or to verify that the name of a part type
        is at least consistent with an exact part_type_id. It is not intended
        to enable browsing the entire database.) 
    '''

    logger.debug(f"looking up part_type: part_type_name='{part_type_name}'")
    
    # Set up the caching
    # Caching cannot be turned off for this function because since users cannot
    # change the name or ID via the REST API, there's no reason to specifically
    # look for a fresh copy.
    def make_cache(fn, name, val):
        if not hasattr(fn, name):
            setattr(fn, name, val)
        return getattr(fn, name)
    _cache = make_cache(lookup_part_type_by_name, "_cache", {})
    
    # Check cache for the result
    part_type_name = part_type_name.upper()
    if part_type_name in _cache:
        return _cache[part_type_name]

    # Validate formatting of fullname
    try:
        project_id, remainder = part_type_name.split('.', 1)
    except ValueError:
        msg = f"part_type_name '{part_type_name}' is invalidly formatted"
        logger.error(msg)
        raise ValueError(msg) from None 
    
    # Get the component type. We can use 0 for wildcards for proj and sys, because
    # the full name should be unambiguous anyway.
    resp = ra.get_component_types(project_id, 0, 0, full_name=part_type_name, size=max_records)

    if resp["pagination"]["total"] > resp["pagination"]["page_size"]:
        msg = (f"The part_type_name pattern '{part_type_name}' returned too many matches. "
                "Use a more restrictive pattern.")
        raise ra.MaxRecordsExceeded(msg)

    retval = [ PartType(rec["part_type_id"], rec["full_name"])
                for rec in resp["data"] ] 

    # Cache the specific pattern originally given (but capitalized)
    _cache[part_type_name] = retval

    # Cache each individual item in the list of results, in case the "exact"
    # pattern is looked for in the future. Note that underscores are a
    # wildcard, so if the thing a user looks for has an underscore, and they
    # don't escape it with a backslash, they could potentially (albeit 
    # likely) match more than they intended. So we want to cache the EXACT
    # name they would need to use if they didn't want wildcards, i.e, we
    # have to escape the unintended wildcards in the name.
    for part_type in retval:
        name = (part_type
                    .name 
                    .replace("\\", "\\\\") 
                    .replace("_", "\\_")
                    .replace("%", "\\%")
                    .upper())
        _cache[name] = [part_type]

    # We're done
    return retval
    #}}}

#######################################################################

def fetch_hwitems(part_type_id = None,
                part_type_name = None,
                part_id = None,
                serial_number = None,
                count = 50):
    #{{{
    '''retrieve multiple items from the HWDB based on criteria

    Uses "get_hwitems", which unfortunately (1) can't be queried in reverse
    order, and (2) doesn't pull back the ENTIRE record like "get_hwitem"
    (singular) does. So, it has to do a fuckton of extra work and can take
    a horribly long time.
    '''
    NUM_THREADS = 50
    MIN_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 250


    save_session_kwargs = deepcopy(ra.session_kwargs)
    ra.session_kwargs["timeout"] = 16


    count = max(1, 100000 if (count == -1) else count)

    # "get_hwitems" doesn't permit part_type_name, so if it's present,
    # we have to look up the part_type_id for it, and ensure that
    # it is consistent with the given part_type_id, if there is one.
    if part_type_name is not None:
        # We don't need everything that this returns, but the function
        # does check for consistency, so we'll use it.
        component_type = fetch_component_type(
                                    part_type_id=part_type_id,
                                    part_type_name=part_type_name)
        # If the above didn't raise anything, we're good.
        # Let's grab the part_type_id from it, in case we don't
        # already have it.
        part_type_id = component_type["ComponentType"]["part_type_id"]

    retval = {}

    # We're going to use a thread pool to get things, but we need to wrap
    # the functions we need in order to pass the arguments correctly.
    pool = mp.Pool(processes=NUM_THREADS)
    get_hwitems = lambda args, kwargs: ra.get_hwitems(*args, **kwargs)
    get_hwitem = lambda args, kwargs: ra.get_hwitem(*args, **kwargs)
    get_subcomponents = lambda args, kwargs: ra.get_subcomponents(*args, **kwargs)

    # Let's first find out how many records we're dealing with

    # There's no sense in using a page size that's too small, because
    # we're more likely to capture the desired number of records if
    # the page is larger. Likewise, we don't want the page to be too
    # large, either.
    page_size = min(max(count, MIN_PAGE_SIZE), MAX_PAGE_SIZE)

    resp = ra.get_hwitems(
                part_type_id=part_type_id,
                part_id=part_id,
                serial_number=serial_number,
                size=page_size)
    total_records = resp["pagination"]["total"]
    num_pages = resp["pagination"]["pages"]

    pages = {1: resp["data"]}

    # If there's only one page, then we already have everything we need.
    if num_pages == 1:
        pass

    # If there's two pages, then grab the second page, and we have
    # everything we need
    elif num_pages == 2:
        resp = ra.get_hwitems(
                    part_type_id=part_type_id,
                    part_id=part_id,
                    serial_number=serial_number,
                    size=page_size,
                    page=2)
        pages[2] = resp["data"]

    # If there's more than two pages, then calculate how many pages we
    # need, and get them.
    else:
        items_on_last_page = total_records - page_size * (num_pages - 1)
        pages_needed = (count - 1) // page_size + 1
        if (pages_needed-1) * page_size + items_on_last_page < count:
            pages_needed += 1

        # Generate a bunch of async requests to get our data in parallel
        page_res = {}
        for page_num in range(num_pages, max(1, num_pages - pages_needed), -1):
            kwargs = \
            {
                "part_type_id": part_type_id,
                "part_id": part_id,
                "serial_number": serial_number,
                "size": page_size,
                "page": page_num,
            }
            page_res[page_num] = pool.apply_async(get_hwitems, ((), kwargs))

        # Read all the data that was gathered
        for page_num, res in page_res.items():
            pages[page_num] = res.get()["data"]

    # Iterate backwards through "pages" until we get the right number
    # of records
    part_ids = []
    for page_num in reversed(sorted(pages.keys())):
        page = pages[page_num]
        if len(part_ids) >= count: break
        for rec in reversed(page):
            part_ids.append(rec["part_id"])
            if len(part_ids) >= count: break

    # Generate more async requests
    hwitems = {part_id: {} for part_id in part_ids}
    hwitems_res = {}
    for part_id in part_ids:
        item_res = pool.apply_async(get_hwitem, ((), {"part_id": part_id}))
        subcomp_res = pool.apply_async(get_subcomponents, ((), {"part_id": part_id}))
        hwitems_res[part_id] = {"Item": item_res, "Subcomponents": subcomp_res}

    # Gather the collected data
    for part_id, res_dict in hwitems_res.items():
        hwitems[part_id] = \
        {
            "Item": res_dict["Item"].get()["data"],
            "Subcomponents": res_dict["Subcomponents"].get()["data"],
        }

    pool.close()
    pool.join()

    ra.session_kwargs = save_session_kwargs

    return hwitems

    #}}}


#######################################################################

def lookup_part_type_id_by_fullname(fullname):
    # TODO: this function is obsolete. Refactor to eliminate calls.
    #{{{
    # The full name should be formatted as [ProjID].[SystemName].[SubsytemName].[PartName],
    # so there should be exactly 3 periods.
    
    logger.debug(f"looking up part type by full name '{fullname}'")

    # If the value has been cached, return that instead
    myself = lookup_part_type_id_by_fullname
    fnu = fullname.upper()
    if not hasattr(myself, "_cache"):
        myself._cache = {}
    if fnu in myself._cache.keys():
        value = myself._cache[fnu]
        logger.debug(f"returning cached value {value}")
        return value

    # Validate formatting of fullname
    try:
        project_id, system_name, subsystem_name, part_name = fullname.split('.')
    except ValueError:
        msg = f"Part name '{fullname}' is invalidly formatted"
        logger.error(msg)
        raise ValueError(msg)


    # Get the component type. We can use 0 for wildcards for proj and sys, because
    # the full name should be unambiguous anyway.
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
        # This could happen because the "fullname" could contain PostgreSQL-style
        # wildcards, which is permitted by the REST API
        msg = f"The full part name '{fullname}' is ambiguous"
        logger.error(msg)
        raise ValueError(msg)

    value = (
            resp['data'][0]['part_type_id'],
            resp['data'][0]['full_name'], 
            )
    logger.debug(f"Found value {value}. Caching and returning.")
    myself._cache[value[0].upper()] = value
    return value
    #}}}

#######################################################################

def lookup_component_type_defs(part_type_id):
    # TODO: this function is obsolete. Refactor to eliminate calls.
    #{{{
    logger.debug(f"looking up component type definition information for '{part_type_id}'")

    # TBD: NEED SOME ERROR HANDLING!!!
    
    # If the value has been cached, return that instead
    myself = lookup_component_type_defs
    pt_id = part_type_id.upper()
    if not hasattr(myself, "_cache"):
        myself._cache = {}
    if pt_id in myself._cache.keys():
        value = myself._cache[pt_id]
        logger.debug(f"returning cached value {value}")
        return value

    type_info = {"part_type_id": pt_id}

    resp = ra.get_component_type(pt_id) 
    if resp["status"] != "OK":
        raise ValueError("Component type lookup failed.")
    
    type_info["full_name"] = resp['data']['full_name']
    type_info["spec_def"] = resp['data']['properties']['specifications'][0]['datasheet']
    type_info["subcomponents"] = resp['data']['connectors']

    resp = ra.get_test_types(pt_id)
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
        resp = ra.get_test_type(pt_id, node["test_type_id"])
        if resp["status"] != "OK":
            raise ValueError("Test type definition lookup failed.")
        node["test_def"] = resp['data']['properties']['specifications'][0]['datasheet']
    
    myself._cache[pt_id] = type_info

    return type_info
    #}}}

#######################################################################

def lookup_institution_by_id(inst_id):
    #{{{
    if not hasattr(lookup_institution_by_id, "_cache"):
        inst_list = ra.get_institutions()['data']
        lookup_institution_by_id._cache = { inst_item['id']: inst_item for inst_item in inst_list }

    return lookup_institution_by_id._cache[inst_id]
    #}}}

#######################################################################

def bulk_add_hwitems(part_type_id, count, *, 
                    institution_id = None,
                    country_code = None, 
                    manufacturer_id = None,
                    comments = None):
    #{{{
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
    #}}}

#######################################################################

def enable_hwitem(part_id, *,
                    enable=True,
                    comments=None):
    #{{{
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
    #}}}

#######################################################################

def set_subcomponents(part_id, subcomponents):
    #{{{
    data = \
    {
        "component": {"part_id": part_id},
        "subcomponents": subcomponents,
    }

    resp = ra.patch_subcomponents(part_id, data)
    if resp["status"] != "OK":
        raise RuntimeError("Error setting subcomponents")

    return resp
    #}}}

#######################################################################

def get_hwitem_complete(part_id):
    #{{{
    logger.debug(f"getting part_id {part_id}")
    resp = ra.get_hwitem(part_id)
    if resp[RA_STATUS] != RA_STATUS_OK:
        raise RuntimeError("Error getting hwitem")
    data = resp[RA_DATA]

    resp = ra.get_subcomponents(part_id)
    if resp[RA_STATUS] != RA_STATUS_OK:
        raise RuntimeError("Error getting subcomponents")

    data[RA_SUBCOMPONENTS] = { item[RA_FUNCTIONAL_POSITION]: item[RA_PART_ID] for item in resp[RA_DATA] }

    return data
    #}}}

#######################################################################

class _SN_Lookup:
    #{{{
    _cache = {}
    @classmethod
    def __call__(cls, part_type_id, serial_number):
        logger.debug(f"looking up {part_type_id}:{serial_number}")
        if (part_type_id, serial_number) not in cls._cache.keys():
            resp = ra.get_hwitems(part_type_id, serial_number=serial_number)
            if resp[RA_STATUS] != RA_STATUS_OK:
                msg = f"Error looking up serial number '{serial_number}' for " \
                            "part type '{part_type_id}'"
                logger.error(msg)
                raise ValueError(msg)
            if len(resp[RA_DATA]) == 1:
                part_id = resp[RA_DATA][0][RA_PART_ID]
                data = get_hwitem_complete(part_id)
                cls._cache[part_type_id, serial_number] = part_id, data

            elif len(resp[RA_DATA]) == 0:
                cls._cache[part_type_id, serial_number] = None
            elif len(resp[RA_DATA]) > 1:
                msg = f"Serial number '{serial_number}' for part type '{part_type_id}' " \
                            "is assigned to {len(resp[RA_DATA])} parts."
                logger.error(msg)
                raise ValueError(msg)
        return cls._cache[part_type_id, serial_number]
    @classmethod
    def update(cls, part_type_id, serial_number, data):
        cls._cache[(part_type_id, serial_number)] = (data[RA_PART_TYPE_ID], data)
    @classmethod
    def delete(cls, part_type_id, serial_number):
        if (part_type_id, serial_number) in cls._cache.keys():
            del cls._cache[(part_type_id, serial_number)]
    #}}}
SN_Lookup = _SN_Lookup()


#######################################################################









