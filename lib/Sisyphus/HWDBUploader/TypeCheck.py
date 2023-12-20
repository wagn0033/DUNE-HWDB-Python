#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/TypeCheck.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

casting types
-------------
any
    use value as interpreted by Pandas. Convert NaN to null
string or str
    use str(value). Convert NaN to null, give warning
integer or int
    use int(value). Convert NaN to null, give warning
    warn if casting truncates value
float
    use float(value). Convert NaN to null, give warning

number
    Attempt to cast as int. If unsuccessful, attempt to cast as float.

bool
    converts "true", "false", 0, 1, "yes", or "no" (all case-insensitive) to bool,
    warn if anything else

null or none
    null if value==NaN. otherwise, use value as interpreted by Pandas and warn
    (Pandas will set blanks to NaN, so use this to make them null instead)

nan
    NaN if value==NaN, otherwise cast to string and warn

empty
    "" if value==NaN, otherwise cast to string and warn


array or list
    use json.loads(value), warn if result type is not list, convert NaN to null.
object or obj or dict
    use json.loads(value), warn if result type is not dict, convert NaN to null.
json
    use json.loads(value), convert NaN to null.

type1,type2[,type3[...]]
    cast as type1. if casting gives warning, cast as type2. repeated as necessary.

array<[subtype]>
object<[subtype]><[subtype]>
    possible future enhancement.
    For now, ignores subtypes

group
    this "type" does not correspond to a column in the sheet.
    instead, it creates a group and defines which columns will be
    subordinate to this group.

"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re

from collections import namedtuple
import math

CastWarning = namedtuple("CastResult", ["dtype", "reason"])
CastResult = namedtuple("CastResult", ["warnings", "original_value", "value"])

# list of string to interpret a an empty/null/nan when asked explicity to
# convert to one of those types.
null_sentinels = ("", "na", "nan", "none", "nothing", "notanumber", "null")

def isnan(value):
    #{{{
    # Annoyingly, math.isnan() requires the argument to be a float or
    # castable as a float. It raises a TypeError if it's something
    # else, e.g., a string.
    return (type(value) is float and math.isnan(value))
    #}}}

def can_cast_null(value):
    return str(value).lower() in null_sentinels or value is None or isnan(value)

def cast_generic_blank(arg, blank_type_name, blank_type_value):
    #{{{
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg

    if can_cast_null(value):
        # This is a successful cast. No warnings.
        return CastResult(None, value, blank_type_value)
    else:
        warnings.append(CastWarning(blank_type_name,
                f"value '{value}' is not interpretable as {blank_type_name}"))
        return CastResult(warnings, value, value)
    #}}}

def cast_null(value):
    return cast_generic_blank(value, "null", None)
def cast_empty(value):
    return cast_generic_blank(value, "empty", "")
def cast_nan(value):
    return cast_generic_blank(value, "nan", math.nan)

def cast_str(arg):
    #{{{
    cast_type = "str"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    # Let's just say that everything can be cast as a string.
    return CastResult(None, value, str(value))
    #}}}

def cast_int(arg):
    #{{{
    cast_type = "int"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if can_cast_null(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is NaN or interpretable as NaN")
        return CastResult([warning, *warnings], value, math.nan)
    else:
        # try to cast it and see what happens
        try:
            return CastResult(None, value, int(str(value)))
        except ValueError as err:
            warning = CastWarning(cast_type, err.args[0])
            return CastResult([warning, *warnings], value, value)
    #}}}

def cast_float(arg):
    #{{{
    cast_type = "float"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if can_cast_null(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is NaN or interpretable as NaN")
        return CastResult([warning, *warnings], value, None)
    else:
        # try to cast it and see what happens
        try:
            return CastResult(None, value, float(value))
        except ValueError as err:
            warning = CastWarning(cast_type, err.args[0])
            return CastResult([warning, *warnings], value, str(value))
    #}}}

def cast_number(arg):
    #{{{
    cast_type = "number"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if can_cast_null(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is NaN or interpretable as NaN")
        return CastResult([warning, *warnings], value, None)
    else:
        # try to cast it and see what happens
        try:
            return CastResult(None, value, int(value))
        except ValueError as err:
            try:
                return CastResult(None, value, float(value))
            except ValueError as err:
                warning = CastWarning(cast_type, err.args[0])
                return CastResult([warning, *warnings], value, str(value))
    #}}}

def cast_bool(arg):
    #{{{
    cast_type = "bool"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if isnan(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is null")
        return CastResult([warning, *warnings], value, None)
    else:
        if str(value).upper() in ("TRUE", "T", "YES", "Y", "1"):
            return CastResult(None, value, True)
        elif str(value).upper() in ("FALSE", "F", "NO", "N", "0"):
            return CastResult(None, value, False)
        else:
            warning = CastWarning(cast_type, f"Could not interpret as boolean: {value}")
            return CastResult([warning, *warnings], value, str(value))
    #}}}

def cast_list(arg):
    #{{{
    cast_type = "list"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if isnan(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is null")
        return CastResult([warning, *warnings], value, None)
    else:
        try:
            L = json.loads(str(value))
        except json.JSONDecodeError as err:
            L = None
        if type(L) is list:
            return CastResult(None, value, L)
        else:
            warning = CastWarning(cast_type, f"Could not interpret as list: {value}")
            return CastResult([warning, *warnings], value, str(value))
    #}}}

def cast_dict(arg):
    #{{{
    cast_type = "dict"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if isnan(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is null")
        return CastResult([warning, *warnings], value, None)
    else:
        try:
            L = json.loads(str(value))
        except json.JSONDecodeError as err:
            warning = CastWarning(cast_type, err.args[0])
            return CastResult([warning, *warnings], value, str(value))

        if type(L) is dict:
            return CastResult(None, value, L)
        else:
            warning = CastWarning(cast_type, f"Could not interpret as dict: {value}, type={type(L)}")
            return CastResult([warning, *warnings], value, str(value))
    #}}}

def cast_json(arg):
    #{{{
    cast_type = "json"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if isnan(value):
        # This is an UNSUCCESSFUL cast.
        warning = CastWarning(cast_type, "value is null")
        return CastResult([warning, *warnings], value, None)
    else:
        try:
            L = json.loads(str(value))
            return CastResult(None, value, L)
        except json.JSONDecodeError as err:
            warning = CastWarning(cast_type, err.args[0])
            return CastResult([warning, *warnings], value, str(value))
    #}}}

def cast_any(arg):
    #{{{
    cast_type = "any"
    if type(arg) is CastResult:
        warnings, value, unused = arg
    else:
        warnings, value = [], arg
    if isnan(value):
        return CastResult(None, value, None)
    else:
        return CastResult(None, value, value)
    #}}}

def cast(value, typedef):
    #{{{
    for typedef in typedef.split(','):
        if typedef in ('str', 'string', 'text'):
            value = cast_str(value)
        elif typedef in ('int', 'integer'):
            value = cast_int(value)
        elif typedef in ('float', 'real'):
            value = cast_float(value)
        elif typedef in ('number', 'numeric'):
            value = cast_number(value)
        elif typedef in ('bool', 'bit'):
            value = cast_bool(value)
        elif typedef in ('null', 'none'):
            value = cast_null(value)
        elif typedef in ('empty'):
            value = cast_empty(value)
        elif typedef in ('nan', 'NaN'):
            value = cast_nan(value)
        elif typedef in ('list', 'array'):
            value = cast_list(value)
        elif typedef in ('dict', 'obj', 'object'):
            value = cast_dict(value)
        elif typedef in ('json',):
            value = cast_json(value)
        elif typedef in ('any'):
            value = cast_any(value)
        else:
            value = CastResult(
                            [CastWarning(typedef, f"unknown type '{typedef}'")], value, value)
        if value.warnings is None:
            break

    return value
    #}}}

