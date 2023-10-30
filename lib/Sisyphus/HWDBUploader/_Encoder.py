#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Encoder.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re


pp = lambda s: print(json.dumps(s, indent=4))

class Encoder:
    def __init__(self):
        pass


