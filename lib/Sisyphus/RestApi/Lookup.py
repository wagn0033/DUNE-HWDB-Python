#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/Docket/__init__.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

import os
import json
import re
from Sisyphus.Utils.utils import class_initializer

CACHE_DATA = os.path.normpath(os.path.join(os.path.dirname(__file__), '_cache'))

@class_initializer("_init_class")
class Country:
    def __new__(cls, string):
        #return cls
        return cls.find_code(string)

    @classmethod
    def find_code(cls, string):
        '''Returns country code from a string containing either the country code,
        the full name of the country (including diacritics), or a combination of 
        the two in the format "(CC) Country Name"'''
        return cls._lookup_country_code.get(string, None)
    
    @classmethod
    def find_name(cls, string):
        '''Returns country name from a string containing either the country code,
        the full name of the country (including diacritics), or a combination of 
        the two in the format "(CC) Country Name"'''
        return cls._lookup_country_name.get(string, None)

    @classmethod
    def find_code_and_name(cls, string):
        '''Returns code and country from a string containing either the country code,
        the full name of the country (including diacritics), or a combination of 
        the two in the format "(CC) Country Name"'''
        return cls._lookup_code_and_country.get(string, None)

    @classmethod
    def search(cls, string):
        '''Return list of code_and_country strings that regex match (case insensitive)
        the given string. May return multiple matches.'''
        
        c_n_c = list(cls._lookup_code_and_country.values())
        L = [s for s in c_n_c if re.search(string, s, flags=re.IGNORECASE)]
        matches = [item for index, item in enumerate(L) if index==L.index(item)]
        return matches

    # @classmethod 
    # def __call__(cls, string):
    #     return cls.find_code(string)

    @classmethod
    def _init_class(cls):
        with open(os.path.join(CACHE_DATA, "country.json"), "r") as fp:
            _json_cache = json.loads(fp.read())['data']
    
        cls._lookup_country_code = {}
        cls._lookup_country_name = {}
        cls._lookup_code_and_country = {}
        for item in _json_cache:
            code_only = item["country_code"]
            country_only = item["name"]
            code_and_country = f"({code_only}) {country_only}" 
            keys = (code_only, country_only, code_and_country)
            cls._lookup_country_code |= {key: code_only for key in keys}
            cls._lookup_country_name |= {key: country_only for key in keys}
            cls._lookup_code_and_country |= {key: code_and_country for key in keys}

@class_initializer("_init_class")
class Institution:
    def __new__(cls, string):
        #return cls
        return cls.find_id(string)

    @classmethod
    def find_id(cls, string):
        '''Returns Institution ID from a string containing either the Institution ID,
        the full name of the institution (including diacritics), or a combination of 
        the two in the format "(id) Institution Name"'''
        return cls._lookup_inst_id.get(str(string), None)
    
    @classmethod
    def find_name(cls, string):
        '''Returns an institution name from a string containing either the Institution ID,
        the full name of the institution (including diacritics), or a combination of 
        the two in the format "(id) Institution Name"'''
        return cls._lookup_inst_name.get(string, None)

    @classmethod
    def find_id_and_name(cls, string):
        '''Returns the ID and name from a string containing either the Institution ID,
        the full name of the institution (including diacritics), or a combination of 
        the two in the format "(id) Institution Name"'''
        return cls._lookup_id_and_name.get(string, None)

    @classmethod
    def search(cls, string):
        '''Return list of id_and_name strings that regex match (case insensitive)
        the given string. May return multiple matches.'''
        
        i_n_n = list(cls._lookup_id_and_name.values())
        
        L = [s for s in i_n_n if re.search(string, s, flags=re.IGNORECASE)]
        matches = [item for index, item in enumerate(L) if index==L.index(item)]
        
        return matches

    # @classmethod 
    # def __call__(cls, string):
    #     return cls.find_id(string)

    @classmethod
    def _init_class(cls):
        with open(os.path.join(CACHE_DATA, "institution.json"), "r") as fp:
            _json_cache = json.loads(fp.read())['data']
    
        cls._lookup_inst_id = {}
        cls._lookup_inst_name = {}
        cls._lookup_id_and_name = {}
        for item in _json_cache:
            id_only = item["id"]
            name_only = item["name"]
            id_and_name = f"({id_only}) {name_only}" 
            keys = (str(id_only), name_only, id_and_name)
            cls._lookup_inst_id |= {key: id_only for key in keys}
            cls._lookup_inst_name |= {key: name_only for key in keys}
            cls._lookup_id_and_name |= {key: id_and_name for key in keys}
        

@class_initializer("_init_class")
class Manufacturer:
    def __new__(cls, string):
        #return cls
        return cls.find_id(string)

    @classmethod
    def find_id(cls, string):
        '''Returns Manufacturer ID from a string containing either the Manufacturer ID,
        the full name of the manufacturer (including diacritics), or a combination of 
        the two in the format "(id) Manufacturer Name"'''
        #print(f"input: {string}")
        #print(cls._lookup_manu_id)
        #print(cls._lookup_manu_id[int(string)])
        return cls._lookup_manu_id.get(str(string), None)
    
    @classmethod
    def find_name(cls, string):
        '''Returns a manufacturer name from a string containing either the Manufacturer ID,
        the full name of the manufacturer (including diacritics), or a combination of 
        the two in the format "(id) Manufacturer Name"'''
        return cls._lookup_manu_name.get(string, None)

    @classmethod
    def find_id_and_name(cls, string):
        '''Returns the ID and name from a string containing either the Manufacturer ID,
        the full name of the manufacturer (including diacritics), or a combination of 
        the two in the format "(id) Manufacturer Name"'''
        return cls._lookup_id_and_name.get(string, None)

    @classmethod
    def search(cls, string):
        '''Return list of id_and_name strings that regex match (case insensitive)
        the given string. May return multiple matches.'''
        
        m_n_n = list(cls._lookup_id_and_name.values())
        
        L = [s for s in m_n_n if re.search(string, s, flags=re.IGNORECASE)]
        matches = [item for index, item in enumerate(L) if index==L.index(item)]
        
        return matches
    
    # @classmethod 
    # def __call__(cls, string):
    #     return cls.find_id(string)
    
    @classmethod
    def _init_class(cls):
        with open(os.path.join(CACHE_DATA, "manufacturer.json"), "r") as fp:
            _json_cache = json.loads(fp.read())['data']
    
        cls._lookup_manu_id = {}
        cls._lookup_manu_name = {}
        cls._lookup_id_and_name = {}
        for item in _json_cache:
            id_only = item["id"]
            name_only = item["name"]
            id_and_name = f"({id_only}) {name_only}" 
            keys = (str(id_only), name_only, id_and_name)
            cls._lookup_manu_id |= {key: id_only for key in keys}
            cls._lookup_manu_name |= {key: name_only for key in keys}
            cls._lookup_id_and_name |= {key: id_and_name for key in keys}
        
if __name__ == "__main__":
    #print("test country:", Country("IT"))
    #print("test country:", Country("Italy"))
    #print("test country:", Country("(IT) Italy"))
    #print("test country:", Country("invalid"))
    print("test institution:", Institution("186"))
    print("test institution:", Institution("University of Minnesota Duluth"))
    
    print("test manufacturer: ", Manufacturer("27"))
    print("test manufacturer: ", Manufacturer("Hajime Inc"))
    #print(json.dumps(Manufacturer._lookup_manu_id, indent=4))
    #print(json.dumps(Institution._lookup_inst_id, indent=4))
