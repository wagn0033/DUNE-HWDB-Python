#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApiV1/Utilities.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra


class HWItem:

    def __init__(self):

        self.data = None
        self.subcomponents = None
        self.container = None
