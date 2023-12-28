#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApiV1/_RestApiV1.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.Configuration as Config # for keywords
from .exceptions import *
from .keywords import *

import json
import requests
import urllib.parse
import functools
import threading

# Define any key/value pairs here that you wish to add to all session
# requests by default.
# Example: to set requests to timeout after 10 seconds, add 
#     session_kwargs['timeout'] = 10
# (Don't add it here. Just set it after loading this module.) 
session_kwargs = {}

# Use this function when constructing a URL that uses some variable as 
# part of the URL itself, e.g.,
#    path = f"api/v1/components/{sanitize(part_id)}"
# DON'T use this function for paramters at the end of the URL if you're 
# using "params" to pass them, because the session.get() method will 
# do that for you, and doing it twice messes up things like postgres wildcards.
def sanitize(s, safe=""):
    return urllib.parse.quote(str(s), safe=safe)

# Initialize the session object with data from Configuration. This function
# may be safely called to re-initialize the session if needed.
def start_session():
    global session
    if config.cert_type == Config.KW_PEM:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        session.mount(f'https://{config.rest_api}', adapter)
        session.cert = config.certificate
    else:
        logger.warning("Unable to start session because a certificate was not available.")
        session = None
session = None
start_session()

log_lock = threading.Lock()

#######################################################################    

class retry:
    '''Wrapper for RestApi functions to permit them to retry on a connection failure'''

    def __init__(self, retries=1):
        self.default_retries = retries

    def __call__(self, function):

        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            retries = max(1, kwargs.pop("retries", self.default_retries))
            last_err = None
            for try_num in range(1, retries+1):
                try:
                    resp = function(*args, **kwargs)
                    break
                except ConnectionFailed as err:
                    msg = (f"Connection failure in '{function.__name__}' "
                            f"in thread '{threading.current_thread().name}' "
                            f"(attempt #{try_num})")
                    logger.warning(msg)
                    last_err = err
            else:
                logger.error(f"{msg}, max attempts reached")
                raise last_err

            return resp

        return wrapped_function


#######################################################################    

@retry(retries=5)
def _request(method, url, *args, return_type="json", **kwargs):
    '''Does a session.request() with some extra error handling

    "Master" function for all gets, posts, and patches. If the return
    type is "json" (which is the default), it will enforce that the 
    response is a valid JSON dictionary that contains a "status" of 
    "OK" otherwise.

    Raises
    ------
    NameResolutionFailure
            The "get" returned a ConnectionError that is most likely
            due to not being able to resolve the URL.
    
    ConnectionFailed
            The "get" returned a ConnectionError for other reasons
    
    InvalidResponse
            The server returned something that wasn't JSON, or wasn't a
            dictionary, or the dictionary not have a "status"

    DatabaseError
            The server returned a valid response, but returned a
            status other than "OK"
    '''
    threadname = threading.current_thread().name
    msg = (f"<_request> thread='{threadname}' "
            f"url='{url}' method='{method.lower()}'")
    if method.lower() in ("post", "patch"):
        # Make it stand out more in the logs if this is actually updating
        # the database
        logger.info(msg)
    else:
        logger.debug(msg)  
 
    if session is None:
        msg = "No session available"
        logger.error(msg)
        raise NoSessionAvailable(msg)
 
    #
    #  Send the "get" request and handle possible errors
    #
    augmented_kwargs = {**session_kwargs, **kwargs}
        
    extra_info = \
    [
        "Additional Information about the error:",
        f"| thread: {threadname}",
        f"| url: {url}",
        f"| method: {method}",
        f"| args: {args}, kwargs: {augmented_kwargs}",
    ]
    
    try:
        resp = session.request(method, url, *args, **augmented_kwargs)

    except requests.exceptions.ConnectionError as conn_err:
        extra_info.append(f"| exception: {repr(conn_err)}")
        if "[Errno -2]" in str(conn_err):
            msg = ("The server URL appears to be invalid.")
            with log_lock:
                logger.error(msg)
                logger.info('\n'.join(extra_info))
            raise NameResolutionFailure(msg) from None
        elif "[Errno -3]" in str(conn_err):
            msg = ("The server could not be reached. Check your internet connection.")
            with log_lock:
                logger.error(msg)
                logger.info('\n'.join(extra_info))
            raise ConnectionFailed(msg) from None
        else:
            msg = ("A connection error occurred while attempting to retrieve data from "
                     f"the REST API.")
            with log_lock:
                logger.error(msg)
                logger.info('\n'.join(extra_info))
            raise ConnectionFailed(msg) from None
    except requests.exceptions.ReadTimeout as timeout_err:
        extra_info.append(f"| exception: {repr(timeout_err)}")
        msg = ("A read timeout error occurred while attempting to retrieve data from "
                 f"the REST API.")
        with log_lock:
            logger.error(msg)
            logger.info('\n'.join(extra_info))
        raise ConnectionFailed(msg) from None

    extra_info.append(f"| status code: {resp.status_code}")
    extra_info.append(f"| response: {resp.text}")

    if return_type.lower() == "json":
        #  Convert the response to JSON and return.
        #  If the response cannot be converted to JSON, raise an exception
        try:
            resp_json = resp.json()
        except json.JSONDecodeError as json_err:
            # This is probably a 4xx or 5xx error that returned an HTML page 
            # instead of JSON. These are hard to figure out until we actually
            # encounter them and look for some distinguishing characteristics,
            # but we'll do what we can.
            if "The SSL certificate error" in resp.text:
                msg = "The certificate was not accepted by the server."
                with log_lock:
                    logger.error(msg)
                    logger.info('\n'.join(extra_info))
                raise CertificateError(msg) from None    
        
            else:
                msg = "The server response was not valid JSON. Check logs for details."
                with log_lock:
                    logger.error(msg)
                    logger.info('\n'.join(extra_info))
                raise InvalidResponse(msg) from None

        #  Look at the response and make sure it complies with the expected
        #  data format and does not indicate an error.
        if type(resp_json) == dict and resp_json.get(KW_STATUS, None) == KW_STATUS_OK:
            return resp_json

        #  Now we know we're going to have to raise an exception, but let's
        #  try to be more specific.
        if type(resp_json) != dict or KW_STATUS not in resp_json:
            msg = "The server response was not valid. Check logs for details."
            with log_lock:
                logger.error(msg)
                logger.info('\n'.join(extra_info))
            raise InvalidResponse(msg) from None

        if KW_DATA in resp_json:
            database_errors = \
            [
                {
                    "signature": "The test specifications do not match the "
                                   "test type definition!",
                    "message": "The Test Results format does not match the "
                                 "test type definition",
                    "ex_type": BadSpecificationFormat,
                },
            ]
            
            for database_error in database_errors:
                if (database_error["signature"] in resp_json['data']):
                    msg = database_error["message"]
                    with log_lock:
                        logger.error(msg)
                        logger.info('\n'.join(extra_info))
                    raise database_error["ex_type"](msg)

        # Fallthrough if no other conditions raised an error
        msg = "The server returned an error. Check logs for details."
        with log_lock:
            logger.error(msg)
            logger.info('\n'.join(extra_info))
        raise DatabaseError(msg, resp_json) from None
    else:
        return resp.contents


#######################################################################    

def _get(url, *args, **kwargs):
    return _request("get", url, *args, **kwargs)

#######################################################################

def _post(url, data, *args, **kwargs):
    return _request("post", url, json=data, *args, **kwargs)

#######################################################################

def _patch(url, data, *args, **kwargs):
    return _request("patch", url, json=data, *args, **kwargs)

#######################################################################
#######################################################################

def get_hwitem_image_list(part_id, **kwargs):
    logger.debug(f"<get_hwitem_images>")
    path = f"api/v1/components/{sanitize(part_id)}/images"
    url = f"https://{config.rest_api}/{path}"

    resp = _get(url, **kwargs)
    return resp

def get_component_type_image_list(part_type_id, **kwargs):
    logger.debug(f"<get_component_images>")
    path = f"api/v1/component-types/{part_type_id}/images"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp

def get_image(image_id, write_to_file, **kwargs):
    logger.debug(f"<get_image>")
    path = f"api/v1/img/{image_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get_binary(url, write_to_file, **kwargs)
    return resp

##############################################################################
#
#  HW ITEMS
#
##############################################################################

def get_hwitem(part_id, **kwargs):
    logger.debug(f"<get_hwitem> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs) 
    return resp

def get_hwitems(part_type_id, *,
                page=None, size=None, fields=None, 
                serial_number=None,
                part_id=None,
                **kwargs):
    
    logger.debug(f"<get_component_types> part_type_id={part_type_id},"
                f"page={page}, size={size}, fields={fields}, "
                f"serial_number={serial_number}, part_id={part_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/components"
    url = f"https://{config.rest_api}/{path}"

    params = []
    if page is not None:
        params.append(("page", page))
    if size is not None:
        params.append(("size", size))
    if serial_number is not None:
        params.append(("serial_number", serial_number))
    if part_id is not None:
        params.append(("part_id", part_id))
    ## *** currently broken in REST API
    if fields is not None:
        params.append(("fields", ",".join(fields)))

    resp = _get(url, params=params, **kwargs) 
    return resp

def post_hwitem(part_type_id, data, **kwargs):
    logger.debug(f"<post_hwitem> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/components" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _post(url, data=data, **kwargs)
    return resp

def patch_hwitem(part_id, data, **kwargs):
    logger.debug(f"<patch_hwitem> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}" 
    url = f"https://{config.rest_api}/{path}"
    
    resp = _patch(url, data=data, **kwargs)
    return resp

def post_bulk_hwitems(part_type_id, data, **kwargs):
    logger.debug(f"<post_bulk_hwitems> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/bulk-add"
    url = f"https://{config.rest_api}/{path}"
                
    resp = _post(url, data=data, **kwargs)
    return resp

def patch_part_id_enable(part_id, data, **kwargs):
    logger.debug(f"<patch_part_id_enable> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}/enable" 
    url = f"https://{config.rest_api}/{path}"
    
    resp = _patch(url, data=data, **kwargs)
    return resp


def patch_enable_item(part_id, data, **kwargs):
    logger.debug(f"<patch_enable_item> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}/enable" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _patch(url, data=data, **kwargs)
    return resp
   
#def patch_hwitem_enable

 
def get_subcomponents(part_id, **kwargs):
    logger.debug(f"<get_subcomponents> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}/subcomponents" 
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp

def patch_subcomponents(part_id, data, **kwargs):
    logger.debug(f"<patch_subcomponents> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}/subcomponents" 
    url = f"https://{config.rest_api}/{path}"
    
    resp = _patch(url, data=data, **kwargs)
    return resp

##############################################################################
#
#  COMPONENT TYPES
#
##############################################################################

def get_component_type(part_type_id, **kwargs):
    logger.debug(f"<get_component_type> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs) 
    return resp

def get_component_type_connectors(part_type_id, **kwargs):
    logger.debug(f"<get_component_type_connectors> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/connectors"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs) 
    return resp

def get_component_type_specifications(part_type_id, **kwargs):
    logger.debug(f"<get_component_type_specifications> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/specifications"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs) 
    return resp

def get_component_types(project_id, system_id, subsystem_id=None, *,
                        full_name=None, comments=None,
                        #part_type_id=None,
                        page=None, size=None, fields=None, **kwargs):
    logger.debug(f"<get_component_types> project_id={project_id}, "
                    f"system_id={system_id}, subsystem_id={subsystem_id}")
    
    # There are actually two different REST API methods for this, one that
    # takes proj/sys/subsys and the other that takes only proj/sys. You 
    # can use a wildcard "0" for subsys for the first one and get the same
    # results as the second, so there really was no need. But, we'll go ahead
    # and use both, switching based on if subsystem_id is or isn't None.
    if subsystem_id is None:
        path = (f"api/v1/component-types/{sanitize(project_id)}/"
                f"{sanitize(system_id)}")
    else:
        path = (f"api/v1/component-types/{sanitize(project_id)}/"
                f"{sanitize(system_id)}/{sanitize(subsystem_id)}")
    url = f"https://{config.rest_api}/{path}"
    
    params = []
    if page is not None:
        params.append(("page", page))
    if size is not None:
        params.append(("size", size))
    if full_name is not None:
        params.append(("full_name", full_name))
    if comments is not None:
        params.append(("comments", comments))
    if fields is not None:
        params.append(("fields", ",".join(fields)))

    resp = _get(url, params=params, **kwargs) 
    return resp

def post_component(part_type_id, data, **kwargs):
    logger.debug(f"<post_component> type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/components" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _post(url, data=data, **kwargs)
    return resp

def patch_hwitem_subcomp(part_id, data, **kwargs):
    logger.debug(f"<patch_hwitem_subcomp> part_id={part_id}")
    path = f"api/v1/components/{sanitize(part_id)}/subcomponents" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _patch(url, data=data, **kwargs)
    return resp

def post_bulk_add(part_type_id, data, **kwargs):
    logger.debug(f"<post_bulk_add> type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/bulk-add" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _post(url, data=data, **kwargs)
    return resp

def patch_bulk_update(part_type_id, data, **kwargs):
    logger.debug(f"<patch_bulk_update> type_id={part_type_id}")
    path = f"api/v1/component-types/{sanitize(part_type_id)}/bulk-update" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _patch(url, data=data, **kwargs)
    return resp

def patch_bulk_enable(part_id, data, **kwargs):
    logger.debug(f"<patch_bulk_enable> part_id={part_id}")
    path = f"api/v1/components/bulk-enable" 
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _patch(url, data=data, **kwargs)
    return resp

##############################################################################
#
#  TESTS
#
##############################################################################

def get_test_types(part_type_id, **kwargs):
    logger.debug(f"<get_test_types> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{part_type_id}/test-types"
    url = f"https://{config.rest_api}/{path}"

    resp = _get(url, **kwargs)
    return resp

def get_test_type(part_type_id, test_type_id, **kwargs):
    logger.debug(f"<get_test_type> part_type_id={part_type_id}, "
                f"test_type_id={test_type_id}")
    path = f"api/v1/component-types/{part_type_id}/test-types/{test_type_id}"
    url = f"https://{config.rest_api}/{path}"

    resp = _get(url, **kwargs)
    return resp

def get_test_type_by_oid(oid, **kwargs):
    logger.debug(f"<get_test_type_by_oid> oid={oid}")
    path = f"api/v1/component-test-types/{oid}"
    url = f"https://{config.rest_api}/{path}"

    resp = _get(url, **kwargs)
    return resp

def post_test_type(part_type_id, data, **kwargs):
    logger.debug(f"<post_test_types> part_type_id={part_type_id}")
    path = f"api/v1/component-types/{part_type_id}/test-types"
    url = f"https://{config.rest_api}/{path}"

    resp = _post(url, data=data, **kwargs)
    return resp

def post_test(part_id, data, **kwargs):
    logger.debug(f"<post_test> part_id={part_id}")
    path = f"api/v1/components/{part_id}/tests"
    url = f"https://{config.rest_api}/{path}"

    resp = _post(url, data=data, **kwargs)
    return resp


##############################################################################
#
#  MISCELLANEOUS
#
##############################################################################

def whoami(**kwargs):
    logger.debug(f"<whoami>")
    path = "api/v1/users/whoami"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 


def get_countries(**kwargs):
    logger.debug(f"<get_countries>")
    path = "api/v1/countries"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_institutions(**kwargs):
    logger.debug(f"<get_institutions>")
    path = "api/v1/institutions"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_manufacturers(**kwargs):
    logger.debug(f"<get_manufacturers>")
    path = "api/v1/manufacturers"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_projects(**kwargs):
    logger.debug(f"<get_projects>")
    path = "api/v1/projects"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_roles(**kwargs):
    logger.debug(f"<get_roles>")
    path = "api/v1/roles"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_users(**kwargs):
    logger.debug(f"<get_users>")
    path = "api/v1/users"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 


def get_user(user_id, **kwargs):
    logger.debug(f"<get_user> user_id={user_id}")
    path = f"api/v1/users/{user_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_role(role_id, **kwargs):
    logger.debug(f"<get_role> role_id={role_id}")
    path = f"api/v1/roles/{role_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_subsystems(project_id, system_id, **kwargs):
    logger.debug(f"<get_subsystems> project_id={project_id}, system_id={system_id}")
    path = f"api/v1/subsystems/{project_id}/{system_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp

def get_subsystem(project_id, system_id, subsystem_id, **kwargs): 
    logger.debug(f"<get_subsystem> project_id={project_id}, "
                    "system_id={system_id}, subsystem_id={subsystem_id}")
    path = f"api/v1/subsystems/{project_id}/{system_id}/{subsystem_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp

def get_systems(project_id, **kwargs):
    logger.debug(f"<get_systems> project_id={project_id}")
    path = f"api/v1/systems/{project_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 

def get_system(project_id, system_id, **kwargs):
    logger.debug(f"<get_system> project_id={project_id}, system_id={system_id}")
    path = f"api/v1/systems/{project_id}/{system_id}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 



##############################################################################


#######################################################################
#######################################################################

    
if __name__ == "__main__":
    pass
