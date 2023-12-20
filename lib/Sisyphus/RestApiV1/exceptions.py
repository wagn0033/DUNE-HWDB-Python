#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApiV1/exceptions.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

class RestApiException(Exception):
    """Base class for RestApi exceptions."""
    pass

class MissingArguments(RestApiException):
    """The function or method expected one or more parameters that were 
    not present.

    Example use case: a function expected an ID or a name, but
    received neither one.
    """

class IncompatibleArguments(RestApiException):
    """The arguments supplied were not compatible with each other

    Example use case: A function might allow a Part Type ID or a 
    Part Type Name, but permit being given both, as long as they
    resolve to the same Component Type. If they do not, raise this
    exception.
    """

class AmbiguousParameters(RestApiException):
    """The arguments supplied did not uniquely identify a resource

    Example use cases: 
      * attempting to look up an institution or
        manufacturer with a string containing a wildcard, and receiving
        more than one result, in a context where the institution or
        manufacturer was expected to be unique
      * trying to identify an item by serial number (and part type), but
        there is more than one item using that serial number
    """

class NoSessionAvailable(RestApiException):
    """The "session" object was not properly initialized

    This typically means that there's something wrong with the current
    configuration.
    """

class ServerError(RestApiException):
    """The REST API server returned an error"""

class InvalidResponse(RestApiException):
    """The REST API server returned invalid data

    The data returned by the server was not a valid format.
    Usually, the response is expected to be a JSON dictionary. If it
    returns something else, use this exception.
    """

class DatabaseError(RestApiException):
    """The REST API server returned an "ERROR" status"""

class NameResolutionFailure(RestApiException):
    """The URL of the server could not be resolved"""

class ConnectionFailed(RestApiException):
    """The REST API server could not be reached"""
    
class NotFound(RestApiException):
    """The function or method did not get a result"""
    
class MaxRecordsExceeded(RestApiException):
    """The query returned more records than is permitted in this context"""


