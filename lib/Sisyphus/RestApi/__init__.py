#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApi/__init__.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config

#from Sisyphus.Logging import logging, log_execution_time
#logger = logging.getLogger(__name__)
logger = config.getLogger()



#from Sisyphus.Config import config
#config.validate()


import json
from requests import Session
import requests.adapters

# Get API and certificate information from config
_api = config.rest_api
_pem_filename = config.certificate

_session = Session()

adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
_session.mount(f'https://{_api}', adapter)
_session.cert = _pem_filename

# def set_api(path):
#     auth._api = path
    
# def set_credentials(p12_data, p12_file, password):
#     auth._p12_data = p12_data
#     auth._password = b64encode(password.encode("utf-8"))
 

# This is just a utility function for testing.
def _raw_get(path):
    if path.startswith("https://"):
        url = path
    else:
        url = f'https://{_api}/{path}'
    resp = _session.get(url) 
    return resp.text


#######################################################################
#
#  Master get/post/patch functions
#
#######################################################################    

# @log_execution_time(logger)
def _get(*args, **kwargs):
    kwargs["timeout"]=10
    logger.debug(f"GET: {args[0]}")
    try:
        # resp = p12get(*args, **kwargs, 
        #               pkcs12_data=_p12_data,
        #               pkcs12_password=_p12_password)
        resp = _session.get(*args, **kwargs)
    except Exception as exc:
        logger.error("An exception occurred while attempting to retrieve data from "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "data": "An exception occurred while retrieving data",
            "status": "ERROR",
            "addl_info": {
                "exception_details": f"{exc}",
            }
        }
        return resp_data
    try:
        resp_data = resp.json()
    
        if resp.status_code in (200, 201):
            resp_data["addl_info"] = "Processed by Sisyphus.RestApi."
            return resp_data
        else:
            resp_data['status'] = resp_data['status'].upper()
            resp_data["addl_info"] = {                
                    "http_response_code": resp.status_code,
                    "url": args[0],
                }
            return resp_data       
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page 
        # instead of JSON text. Package it up to have the same 
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        err = {
            "data": "The server returned an error.",
            "status": "ERROR",
            "addl_info":
            {
                "http_response_code": resp.status_code,
                "url" : args[0],
                "response": resp.text,
            },
        }
        return err

#######################################################################    

# @log_execution_time(logger)    
def _post(*args, **kwargs):
    
    logger.info(f"calling _post (V0) with args={args}, kwargs={kwargs}")
    kwargs["timeout"]=10
    try:
        # resp = p12post(*args, **kwargs, 
        #               pkcs12_data=_p12_data,
        #               pkcs12_password=_p12_password)       
        resp = _session.post(*args, **kwargs)
    except Exception as exc:
        logger.error("An exception occurred while attempting to post data to "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "data": "An exception occurred while posting data",
            "status": "ERROR",
            "addl_info": {
                "exception_details": f"{exc}",
            }
        }
        return resp_data
    
    try:
        resp_data = resp.json()
        if resp.status_code in (200, 201):
            resp_data["addl_info"] = "Processed by Sisyphus.RestApi."
            return resp_data
        else:
            resp_data["addl_info"] = {                
                    "http_response_code": resp.status_code,
                    "url": args[0],
                }
            return resp_data  
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page 
        # instead of JSON text. Package it up to have the same 
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        err = {
            "data": "The server returned an error.",
            "status": "ERROR",
            "addl_info":
            {
                "http_response_code": resp.status_code,
                "url" : args[0],
                "response": resp.text,
            },
        }
        return err

#######################################################################    
        
# @log_execution_time(logger)    
def _get_binary(*args, **kwargs):
    kwargs["timeout"]=10
    try:
        # resp = p12get(*args, **kwargs, 
        #               pkcs12_data=_p12_data,
        #               pkcs12_password=_p12_password)
        resp = _session.get(*args, **kwargs)
    except Exception as exc:
        logger.error("An exception occurred while attempting to get binary "
                     f"data from the REST API. Exception details: {exc}")
        raise RuntimeError(f"the request failed: {exc}")
      
    write_to_file = kwargs.pop("write_to_file")
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

# @log_execution_time(logger)    
def _patch(*args, **kwargs):
    kwargs["timeout"]=10
    try:
        # resp = p12patch(*args, **kwargs, 
        #               pkcs12_data=_p12_data,
        #               pkcs12_password=_p12_password)
        resp = _session.patch(*args, **kwargs)
    except Exception as exc:
        logger.error("An exception occurred while attempting to patch data to "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "data": "An exception occurred while patching data",
            "status": "ERROR",
            "addl_info": {
                "exception_details": f"{exc}",
            }
        }
        return resp_data
    
    try:
        resp_data = resp.json()
        if resp.status_code in (200, 201):
            resp_data["addl_info"] = "Processed by Sisyphus.RestApi."
            return resp_data
        else:
            resp_data["addl_info"] = {                
                    "http_response_code": resp.status_code,
                    "url": args[0],
                }
            return resp_data  
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page 
        # instead of JSON text. Package it up to have the same 
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        err = {
            "data": "The server returned an error.",
            "status": "ERROR",
            "addl_info":
            {
                "http_response_code": resp.status_code,
                "url" : args[0],
                "response": resp.text,
            },
        }
        return err

##########################################################################
# REST API reference
# ==================
#
# source: https://cdcvs.fnal.gov/redmine/projects/components-db/wiki/Rest_API
#
# COMPONENT TYPES
# ===============
# GET       /component-types[?[page=<int>][&term=<pattern>]]
# POST      /component-types
# GET       /component-types/<type_id>[?history=true]
# PATCH     /component-types/<type_id>
# GET/PATCH /component-types/<type_id>/connectors
# GET/POST  /component-types/<type_id>/images
# GET/PATCH /component-types/<type_id>/specifications
#
# COMPONENTS
# ==========
# GET       /component-types/<name>/components[?[page=<int>][&term=<pattern>]]
# POST      /component-types/<name>/components
# GET       /components/<external-id>[?history=true]
# GET       /components/<external-id>/container[?history=true]
# GET       /components/<external-id>/subcomponents[?history=true]
#
# TEST TYPES
# ==========
# GET       /component-types/<type_name>/test-types
# POST      /component-types/<type_name>/test-types
# GET       /component-types/<type-name>/test-types/<test-type-name>[?history=true]
#
# TESTS
# =====
# GET       /components/<external-id>/tests[?history=true]
# POST      /components/<external-id>/tests
# GET       /components/<external-id>/tests/<test-name>[?history=true]
#
# OPERATIONS
# ==========
# GET       /structures[?page=<int>]
# GET       /structures/<external-id>[?history=true]
# POST      /structures/<external-id>
#
# CABLES
# ======
# GET       /cables[?page=<int>]
# GET       /cables/<external-id>[?history=true]
# POST      /cables/<external-id>
#
# IMAGES
# ======
# GET/POST  /images/components/<eid>
# GET/POST  /images/component-types/<oid>
# GET/POST  /images/component-tests/<oid>
##########################################################################

def get_attributes(attribute_id, **kwargs):
    path = f"cdbdev/api/attributes/{attribute_id}"
    url = f"https://{_api}/{path}"

    resp = _get(url, **kwargs)

    if resp["status"].upper() != "ERROR":
        attribute_id = resp["link"]["href"].split("/")[-1]
        resp["data"]["attribute_id"] = attribute_id
        resp["data"]["component"] = resp["component"]
    
    return resp


#######################################################################
#
#  Component Type methods
#
####################################################################### 

def get_component_types(page=None, term=None, **kwargs):
    #
    #   CURRENTLY BROKEN IN REST API !!!!
    #

    path = "cdbdev/api/component-types"
    url = f"https://{_api}/{path}"
    
    params = []
    if page is not None:
        params.append(("page", page))
    if term is not None:
        params.append(("term", term))
    
    if len(params) > 0:
        resp = _get(url, params=params, **kwargs)
    else:
        resp = _get(url)
    
    return resp

#######################################################################

# @log_execution_time(logger)
def get_component_type(part_type_id, history=False, **kwargs):
    path = f"cdbdev/api/component-types/{part_type_id}"
    url = f"https://{_api}/{path}"
    
    params = []
    if history is True:
        params.append(("history", "true"))
    
    resp = _get(url, params=params, **kwargs)
    
    # do a little postprocessing to help DataModel out
    if resp["status"].upper() != "ERROR":
        resp["data"]["type_id"] = part_type_id

    return resp

#######################################################################

def patch_component_type():
    pass

#######################################################################

#def post_component(type_id, data, **kwargs):
#    path = f"cdbdev/api/component-types/{type_id}/components"
#    url = f"https://{_api}/{path}" 
#   
#    logger.info(f"calling post_component (V0) with url='{url}'")
# 
#    resp = _post(url, data=data, **kwargs)
#
#    return resp

#######################################################################

def get_component_type_connectors(type_id, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/connectors"
    url = f"https://{_api}/{path}" 
    return _get(url, **kwargs)
  
def patch_component_type_connectors(type_id, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}>/connectors"    
    url = f"https://{_api}/{path}"  

def get_component_type_images(type_id, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/images"
    url = f"https://{_api}/{path}"
    return _get(url, **kwargs)

def post_component_type_images(type_id, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/images"
    url = f"https://{_api}/{path}"
    
def get_component_type_specifications(type_id, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/specifications"
    url = f"https://{_api}/{path}"
    return _get(url)

def patch_component_type_specifications(type_id, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/specifications"  
    url = f"https://{_api}/{path}"

#######################################################################
# 
#  Component (or Item) methods
#
#######################################################################

# @log_execution_time(logger) 
def get_components(part_type_id, page=None, term=None, **kwargs):
    path = f"cdbdev/api/component-types/{part_type_id}/components"
    url = f"https://{_api}/{path}"
    
    params = []
    if page is not None:
        params.append(("page", page))
    if term is not None:
        params.append(("term", term))
    
    if len(params) > 0:
        resp = _get(url, params=params, **kwargs)
    else:
        resp = _get(url)
    
    return resp    

#######################################################################

# @log_execution_time(logger)
def post_component(type_id, data, **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/components"
    url = f"https://{_api}/{path}"

    logger.info(f"calling post_component (V0) with url='{url}'")

    resp = _post(url, json=data, **kwargs)
    
    # do a little postprocessing to help DataModel out
    if resp["status"].upper() != "ERROR":
        pass
        
    return resp

#######################################################################

# @log_execution_time(logger)
def get_component(part_id, history=False, **kwargs):
    path = f"cdbdev/api/components/{part_id}"
    url = f"https://{_api}/{path}"
    
    # A LITTLE WARNING...
    # 1) If you append the parameter "history" with ANY value (even
    #    False), it will bring back the history. So we have to make 
    #    sure to only append it to parameters if it's True.
    # 2) If you request the history, the structure of the result is not
    #    quite exactly the same as if you don't. If you do, it will 
    #    return metadata about each record under "specification," but 
    #    not the actual content.  If you don't as for history, you 
    #    get the content for the latest specification record, but no
    #    metadata. 
    
    params = []
    
    if history: # DO NOT append anything if False. See above note.
        params.append(("history", history))
    
    resp = _get(url, params=params, **kwargs)
    
    return resp  

#######################################################################

# @log_execution_time(logger)
def get_component_container(part_id, history=False, **kwargs):
    path = f"cdbdev/api/components/{part_id}/container"
    url = f"https://{_api}/{path}"
    
    params = []
    if history is True:
        params.append(("history", "true"))
    
    resp = _get(url, params=params, **kwargs)
    
    if resp["status"].upper() != "ERROR":
        data_node = resp["data"]
        
        if len(data_node) > 0:
            if data_node.get("operation", None) == "mount":
                parent_part_id = data_node["link"]["href"].split("/")[-1]
                data_node["parent_part_id"] = parent_part_id
                data_node["part_id"] = part_id
    
    return resp  

#######################################################################

# @log_execution_time(logger)
def get_component_subcomponents(part_id, history=False, **kwargs):
    path = f"cdbdev/api/components/{part_id}/subcomponents"
    url = f"https://{_api}/{path}"
    
    params = []
    if history is True:
        params.append(("history", "true"))
    
    resp = _get(url, **kwargs)
    
    return resp 

#######################################################################
#
#  Test Type methods
#
####################################################################### 

# @log_execution_time(logger)
def get_test_types(part_type_id, **kwargs):
    path = f"cdbdev/api/component-types/{part_type_id}/test-types"
    url = f"https://{_api}/{path}"
    resp = _get(url, **kwargs)

    # The "data" node will contain a list of "test type" objects, but these
    # objects are really just summaries and don't contain everything we 
    # need to know about the tests. To get that information, we need to call
    # another method with the test type id, but that id is buried inside the
    # "link" node as part of the url. So, we're going to have to do some
    # post-processing of the response to make it more useful to any consumer
    # of this (these?) data.
    if resp["status"].upper() != "ERROR":  
        component_type_node = resp["component_type"]
        
        for test_type_meta in resp["data"]:
            test_type_id = test_type_meta["link"]["href"].split("/")[-1]
            test_type_meta["component_type"] = component_type_node
            test_type_meta["test_type_id"] = test_type_id
            
    return resp

# @log_execution_time(logger)
def get_test_type(test_type_id, **kwargs):
    path = f"cdbdev/api/component-test-types/{test_type_id}"
    url = f"https://{_api}/{path}"
    return _get(url, **kwargs)

# @log_execution_time(logger)    
def post_test_type(part_type_id, data,  **kwargs):
    path = f"cdbdev/api/component-types/{part_type_id}/test-types"
    url = f"https://{_api}/{path}"

    resp = _post(url, json=data, **kwargs)
    return resp

# @log_execution_time(logger)
def get_test_type_by_name(type_id, test_type_name, history=False,  **kwargs):
    path = f"cdbdev/api/component-types/{type_id}/test-types/{test_type_name}"
    url = f"https://{_api}/{path}"

    resp = _get(url, **kwargs)

    # Add component_type to the data node for convenience down the road.
    if resp["status"].upper() != "ERROR":
        resp["data"]["specifications"][0]["component_type"] = resp["component_type"]    

    return resp

# GET       /components/<external-id>/tests[?history=true]
# POST      /components/<external-id>/tests
# GET       /components/<external-id>/tests/<test-name>[?history=true]

#######################################################################
#
#  Test methods
#
####################################################################### 

# @log_execution_time(logger)
def get_tests(eid, history=False, **kwargs):    
    path = f"cdbdev/api/components/{eid}/tests"
    url = f"https://{_api}/{path}"
    
    params = []
    if history is True:
        params.append(("history", "true"))
    
    resp = _get(url, params=params, **kwargs)
    
    return resp
  
# @log_execution_time(logger)
def get_test(eid, name, history=False, **kwargs):    
    path = f"cdbdev/api/components/{eid}/tests/{name}"
    url = f"https://{_api}/{path}"
    
    params = []
    if history is True:
        params.append(("history", "true"))
    
    resp = _get(url, params=params, **kwargs)
    
    return resp

def post_test(eid, test_data, **kwargs):
    path = f"cdbdev/api/components/{eid}/tests"
    url = f"https://{_api}/{path}"
    
    resp = _post(url, json=test_data, **kwargs)
    return resp

#######################################################################
#
#  Image methods
#
####################################################################### 

# GET/POST  /images/components/<eid>
# GET/POST  /images/component-types/<oid>
# GET/POST  /images/component-tests/<oid>

# @log_execution_time(logger)
def get_component_images(external_id, **kwargs):
    path = f"cdbdev/api/components/{external_id}/images"
    url = f"https://{_api}/{path}"
    return _get(url, **kwargs)

# @log_execution_time(logger)
def get_component_type_images(type_id, **kwargs):
    raise NotImplementedError()

# @log_execution_time(logger)
def get_component_test_images(*args, **kwargs):
    raise NotImplementedError()

# @log_execution_time(logger)    
def get_image(image_id, write_to_file=None, **kwargs):
    path = f"cdbdev/api/img/{image_id}"
    url = f"https://{_api}/{path}"
    return _get_binary(url, write_to_file=write_to_file, **kwargs)
 
# =====================================================================



# def test_gets():
#     print("See tests directory for individual tests for this module.")



# def test_get_component_csv():
#     comp_data = get_component("Z00100100049-00019")
#     spec = comp_data["data"]["specifications"][0]
#     print(json.dumps(spec, indent=4))
   
#     comp_type_data = get_component_type("Z00100100049")
#     spec_def = comp_type_data["data"]["properties"]["specifications"][0]["datasheet"]
#     print(json.dumps(spec_def, indent=4))
    
#     csv_src = spec["data"]
#     col_order = spec_def["data"]["_column_order"]
    
#     print("*** csv_src:")
#     print(json.dumps(csv_src, indent=4))
#     print(col_order)
    
#     csv_ordered = []
#     for colname in col_order:
#         csv_ordered.append([colname, *csv_src[colname]])
      
#     csv_flipped = list(zip(*csv_ordered))
#     print(json.dumps(csv_flipped, indent=4))
    
#     with open("sample_out.csv", "w") as f:
#         csv_writer = csv.writer(f, lineterminator='\n')
#         csv_writer.writerows(csv_flipped)

# def datasheet_to_csv(type_id, datasheet, csv_filename):
    
#     # get the specification definition from the component type
#     comp_type_data = get_component_type(type_id)
#     spec_def = comp_type_data["data"]["properties"]["specifications"][0]["datasheet"]
#     col_order = spec_def["data"]["_column_order"]

#     print("*** datasheet ***")
#     print(json.dumps(datasheet, indent=4))

#     print("*** master ***")
#     print(json.dumps(spec_def, indent=4))

#     # 
    

# def csv_to_datasheet(type_id, csv_filename):
#     pass
    
def run_tests():
    pass

if __name__ == "__main__":
    #test_post_component()
    #test_get_component_csv()
    run_tests()
   
    # with open("../../user/credentials/awagner.pem", "rb") as f:
    #     c = f.read()
        
    # print(b64encode(c))
    
    





