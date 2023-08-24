#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApiV1/__init__.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()


#import Sisyphus.Config as Config
#from Sisyphus.Config import config as cfg
#logger = cfg.getLogger("RestApiV1")

import json
from requests import Session
import requests.adapters

import urllib.parse

def sanitize(s):
    return urllib.parse.quote(s, safe="")


def create_session():
    session = Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount(f'https://{config.rest_api}', adapter)
    session.cert = config.certificate
    return session

session = create_session()

#######################################################################    

def _get(url, *args, **kwargs):
    
    logger.debug(f"Calling API with url='{url}'")
    
    # kwargs["timeout"]=10
    
    #
    #  Send the "get" request.
    #  If an error occurs, create a JSON response explaining the problem
    #  and return it.
    #
    try:
        resp = session.get(url, *args, **kwargs)
    except Exception as exc:
        logger.error("An exception occurred while attempting to retrieve data from "
                     f"the REST API. Exception details: {exc}")
        resp_data = {
            "data": "An exception occurred while retrieving data",
            "status": "URL Error",
            "addl_info": {
                "exception_details": f"{exc}",
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
        return resp_data
    except json.JSONDecodeError:
        # This is probably a 500 error that returned an HTML page 
        # instead of JSON text. Package it up to have the same 
        # structure as how the API would've handled a 4xx error so
        # the consumer can look in the same place for info.
        logger.error("The server returned content that was not valid JSON")
        err = {
            "data": "The server returned content that was not valid JSON",
            "status": "Server Error",
            "addl_info":
            {
                "http_response_code": resp.status_code,
                "url" : url,
                "response": resp.text,
            },
        }
        return err

#######################################################################

def _post(url, data, *args, **kwargs):
    
    logger.debug(f"Calling REST API (post) with url='{url}'")
    #kwargs["timeout"]=10
    
    #
    #  Send the "post" request.
    #  If an error occurs, create a JSON response explaining the problem
    #  and return it.
    #
    try:
        resp = session.post(url, data, *args, **kwargs)
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
    
    if resp.status_code not in (200, 201):
        logger.warning(f"RestApiV1._post method returned status code {resp.status_code}")
    
    
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
            "data": "The server returned content that was not valid JSON",
            "status": "Server Error",
            "addl_info":
            {
                "http_response_code": resp.status_code,
                "url" : url,
                "response": resp.text,
            },
        }
        return err
    
def get_hwitem_by_part_id(part_id, **kwargs):
    path = f"cdbdev/api/v1/components/{sanitize(part_id)}"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    
    return resp

def get_image_by_part_id(part_id, **kwargs):
    path = f"cdbdev/api/v1/components/{sanitize(part_id)}/images"
    url = f"https://{config.rest_api}/{path}"

    resp = _get(url, **kwargs)
    return resp


def get_countries(**kwargs):
    path = "cdbdev/api/v1/countries"
    url = f"https://{config.rest_api}/{path}"
    
    resp = _get(url, **kwargs)
    return resp 



def post_component(type_id, data, **kwargs):
    path = f"cdbdev/api/v1/component-types/{type_id}/components"
    url = f"https://{config.rest_api}/{path}" 
    
    resp = _post(url, data=data, **kwargs)

    print(resp)
    if resp["status"] != "OK":
        logger.error("Error while posting a component")
        logger.info(f"url: {url}")
        logger.info(f"data: {data}")
        logger.info(f"response: {resp}")


    return resp





#######################################################################
#######################################################################

    
if __name__ == "__main__":
    pass