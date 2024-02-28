#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/__init__.py
Copyright (c) 2024 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""
import os

version = 'v1.2.0.pre-release.2024.02.28a'

project_root = os.path.realpath(os.path.join(os.path.dirname(__file__), "../.."))

def get_path(path):
    """Get a path relative to the project root"""
    return os.path.realpath(os.path.join(project_root, path))
