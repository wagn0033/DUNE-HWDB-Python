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
logger = config.getLogger()

import Sisyphus.Configuration as Config
import json
from requests import Session
import requests.adapters
import urllib.parse


KW_STATUS = "status"
KW_ERROR = "ERROR"
KW_SERVER_ERROR = "SERVER ERROR"

class ServerError(Exception):
    """thrown when the server is not returning a response"""

raise_server_errors = False

session_kwargs = {}

# ##########
# Use this function when constructing a URL that uses some variable as 
# part of the URL itself, e.g.,
#    path = f"api/v1/components/{sanitize(part_id)}"
# DON'T use this function for paramters at the end of the URL if you're 
# using "params" to pass them, because the session.get() method will 
# do that for you, and doing it twice messes up things like postgres wildcards.
def sanitize(s, safe=""):
    return urllib.parse.quote(str(s), safe=safe)


def start_session():
    global session
    if config.cert_type == Config.KW_PEM:
        session = Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        session.mount(f'https://{config.rest_api}', adapter)
        session.cert = config.certificate
    else:
        logger.warning("Unable to start session because a certificate was not available.")
        session = None

session = None
start_session()

#######################################################################    

def _get(url, *args, **kwargs):

    logger.debug(f"<_get> Calling REST API with url='{url}'")

    
   
    if session is None:
        msg = "No session available"
        logger.error(msg)
        raise RuntimeError(msg)
 
    # kwargs["timeout"]=10
    
    #
    #  Send the "get" request.
    #  If an error occurs, create a JSON response explaining the problem
    #  and return it.
    #
    try:
        resp = session.get(url, *args, **{**kwargs, **session_kwargs})
    except Exception as exc:
        msg = ("An exception occurred while attempting to retrieve data from "
                     f"the REST API. Exception details: {exc}")
        logger.error(msg)
        logger.info(f"The exception type was {type(exc)}")

        if raise_server_errors:
            raise ServerError(msg)
        resp_data = {
            "status": KW_SERVER_ERROR,
            "addl_info": {
                "msg": msg,
            }
        }
        return resp_data
    
    #
    #  Convert the response to JSON and return.
    #  If the response cannot be converted to JSON, construct an alternate
    #  JSON response stating the problem and return that instead.
    #
    try:
        resp_data = resp.json()

        if type(resp_data) != dict:
            err = {
                "status": "Server Error",
                "addl_info": {
                    "msg": "The server returned invalid data",
                    "response": f"{resp_data}",
                }
            }
            return err
        else:
            return resp_data
    
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page 
        # instead of JSON text. Package it up to have the same 
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        logger.error("The server returned content that was not valid JSON")
        err = {
            "status": "Server Error",
            "addl_info":
            {
                "msg": "The server returned content that was not valid JSON",
                "http_response_code": resp.status_code,
                "url" : url,
                "response": resp.text,
            },
        }
        logger.info(f"response: {resp.text}")
        return err

#######################################################################

def _get_binary(url, write_to_file, *args, **kwargs):
     
    logger.debug(f"<_get_binary> Calling API with url='{url}'")
    
    if session is None:
        msg = "No session available"
        logger.error(msg)
        raise RuntimeError(msg)
    
    # kwargs["timeout"]=10
    
    #
    #  Send the "get" request.
    #  If an error occurs, create a JSON response explaining the problem
    #  and return it.
    #
    try:
        resp = session.get(url, *args, **{**kwargs, **session_kwargs})
    except Exception as exc:
        logger.error("An exception occurred while attempting to retrieve data from "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "status": KW_SERVER_ERROR,
            "addl_info": {
                "msg": "An exception occurred while retrieving data",
                "exception_details": f"{exc}",
            }
        }
        return resp_data
    
    if resp.status_code in (200, 201):
        try:
            with open(write_to_file, "wb") as f:
                    f.write(resp.content)
        except Exception as exc:
            logger.error("An exception occurred while attempting to write binary "
                         f"data to {write_to_file}. Exception details: {exc}")
    else:
        logger.error("The request to the REST API failed. HTTP status code "
                     f"{resp.status_code}")
        raise RuntimeError("the request failed: status code %d" 
                                 % resp.status_code)

#######################################################################


def _post(url, data, *args, **kwargs):
    
    logger.debug(f"<_post> Calling REST API with url='{url}'")
    
    if session is None:
        msg = "No session available"
        logger.error(msg)
        raise RuntimeError(msg)
   
    #kwargs["timeout"]=10
    
    #
    #  Send the "post" request.
    #  If an error occurs, create a JSON response explaining the problem
    #  and return it.
    #
    try:
        resp = session.post(url, json=data, *args, **{**kwargs, **session_kwargs})
    except Exception as exc:
        logger.error("An exception occurred while attempting to post data to "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "status": "ERROR",
            "addl_info": {
                "msg": "An exception occurred while posting data",
                "exception_details": f"{exc}",
            }
        }
        return resp_data
    
    if resp.status_code not in (200, 201):
        logger.warning(f"RestApiV1._post method returned status code {resp.status_code}")
        logger.info(f"The response was: {resp.text}")
    
    #
    #  Interpret the response as JSON and return.
    #  If the response cannot be interpreted as JSON, construct an alternate
    #  JSON response stating the problem and return that instead.
    #
    try:
        resp_data = resp.json()
        return resp_data
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page 
        # instead of JSON text. Package it up to have the same 
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        logger.error("The server returned content that was not valid JSON")
        err = {
            "status": "Server Error",
            "addl_info":
            {
                "msg": "The server returned content that was not valid JSON",
                "http_response_code": resp.status_code,
                "url" : url,
                "response": resp.text,
            },
        }
        logger.info(f"response: {resp.text}")
        return err
    
#######################################################################

def _patch(url, data, *args, **kwargs):
    
    logger.debug(f"<_patch> Calling REST API with url='{url}'")
    
    if session is None:
        msg = "No session available"
        logger.error(msg)
        raise RuntimeError(msg)

    #kwargs["timeout"]=10

    #
    #  Send the "patch" request.
    #  If an error occurs, create a JSON response explaining the problem
    #  and return it.
    #
    try:
        resp = session.patch(url, json=data, *args, **{**kwargs, **session_kwargs})
    except Exception as exc:
        logger.error("An exception occurred while attempting to patch data to "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "status": "ERROR",
            "addl_info": {
                "msg": "An exception occurred while patching data",
                "exception_details": f"{exc}",
            }
        }
        return resp_data

    if resp.status_code not in (200, 201):
        logger.warning(f"RestApiV1._patch method returned status code {resp.status_code}")
        logger.info(f"The data was: {data}")
        logger.info(f"The response was: {resp.text}")
    
    try:
        resp_data = resp.json()
        return resp_data
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page
        # instead of JSON text. Package it up to have the same
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        err = {
            "status": "ERROR",
            "addl_info":
            {
                "msg": "The server returned an error.",
                "http_response_code": resp.status_code,
                "url" : url,
                "response": resp.text,
            },
        }
        logger.info(f"response: {resp.text}")
        return err

#######################################################################

def get_component_image(part_id, **kwargs):
    logger.debug(f"<get_image_by_part_id>")
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
