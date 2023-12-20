#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/Utils/utils.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy

Miscellaneous utility functions
"""

import os, sys
from functools import wraps


class objectmethod(classmethod):
    '''Permits a method to be used in both the class and instances of the class

    It behaves essentially like classmethod, except the first argument
    to the function (typically named 'cls') is only the class if called
    from the class. If called from an instance, it is the instance
    instead (typically named 'self').

    >>> class Example:
    ...     @objectmethod
    ...     def func(obj):
    ...         if type(obj) is type:
    ...             print("called from class")
    ...         else:
    ...             print("called from instance")
    ...
    >>> Example.func()
    called from class
    >>> Example().func()
    called from instance

    '''

    def __get__(self, instance, owner):
        if instance is None:
            return super().__get__(instance, owner)
        else:
            return self.__func__.__get__(instance, owner)


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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
