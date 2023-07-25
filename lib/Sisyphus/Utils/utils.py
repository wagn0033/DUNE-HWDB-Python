#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/Utils/utils.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

# TBD: could probably remove logging in this module, to reduce
# unnecessary dependencies
#from Sisyphus.Logging import logging
#logger = logging.getLogger(__name__)
#logger.info(f"{__name__} imported logging")
from Sisyphus.Configuration import config
logger = config.getLogger("utils")

import os, sys
from functools import wraps

#from functools import wraps, partial
#from Sisyphus.Utils.utils import traverse

#from collections.abc import Mapping, Sequence

class classmethod_strict(object):
    def __init__(self, method):
        self.method = method
    def __get__(self, instance, cls):
        if instance is not None:
            raise TypeError("classmethod intended to be called "
                            "from class only, not from instances")
        #return lambda *args, **kw: self.method(cls, *args, **kw)
        @wraps(self.method)
        def fn(*args, **kwargs):
            try:
                return self.method(cls, *args, **kwargs)
            except Exception as e:
                print(e)
                raise
        return fn

def process_list(fn):
    def wrap(seq):
        print(seq)
        return list(map(fn, seq))
    setattr(wrap, "__name__", f"list<{fn.__name__}>")
    return wrap 


def traverse_dict(path):
    def wrap(fn):
        def wrap(mp):
            print(mp, path)
            return fn(traverse(mp, path))
        
        #wrap.__name__ = f"Traverse<{fn.__name__}>"
        setattr(wrap, "__name__", f"traverse<{len(path)},{fn.__name__}>")
        return wrap 
    
    return wrap 


def normalize_path(path):
    """
    Resolve the path to a uniform standard. 
    Essentially the same as os.path.normpath, except, it also makes
    sure the drive letter is capitalized if we're in a windows system.
    
    Usage: see os.path.normpath()
    """

    newpath = os.path.normpath(path)

    # Check if the first two chars indicate the drive.
    # If so, make sure it's uppercase.
    if len(newpath)>2 and newpath[1] == ":":
        newpath = "".join([newpath[0].upper(), newpath[1:]])
    
    return newpath
    


def safe_add_to_path(*paths):
    """
    Checks sys.path for paths, and only inserts those that are not
    already there. Both paths and sys.path are normalized first, so
    equivalent paths will take the same form.
    """
    
    # map paths to their normalized version, so after we find out if
    # the path doesn't exist, we can add the *original* path, not 
    # the normalized one. If two paths are given that resolve to the
    # same normalized path, only the last one will be added.
    normalized_paths = {normalize_path(path): path for path in paths} 
    normalized_sys_paths = {normalize_path(path): path for path in sys.path}
    
    for norm, orig in normalized_paths.items():
        if norm not in normalized_sys_paths.keys():
            sys.path.append(orig)


# TBD: should BaseObject use this one? I found it useful elsewhere, so I don't want it
# only in BaseObject anymore
def class_initializer(class_init=None):
    #@wraps(cls)
    def decorator_wrapper(cls):
        #setattr(cls, "_priv", [a, b, c])
        init_fn = getattr(cls, class_init, None) 
        if init_fn is None:
            msg = f"class {cls.__name__} does not have a class initializer {class_init}"
            logger.error(msg)
            raise TypeError(msg)
        elif not callable(init_fn):
            msg = f"class {cls.__name__}'s initializer {class_init} is not callable."
            logger.error(msg)
            raise TypeError(msg)
        else:
            #print(f"calling {cls.__name__}'s initializer!")
            init_fn()
        return cls
    return decorator_wrapper

def traverse(container, path):
    """
    Traverses through a nested container of dicts and lists. (Or compatible
    mapping and sequence types.)

    Parameters
    ----------
    container : nested mapping (dict-like) and sequence (list-like) types
    
    path : a sequence of str and/or int that describes the route through the
           nested dict/list

    Returns
    -------
    node : Any
        the data found by traversing the given path

    """
    try:
        node = container
        for id_ in path:
            node = node[id_]
        return node
    except LookupError:
        raise LookupError(path)
    except TypeError:
        return 'bad'
        #print(path, container)
        raise TypeError(f"path '{path}' was not valid")
