#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUploader/_Encoder.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus.RestApiV1 as ra
import Sisyphus.RestApiV1.Utilities as ut
from Sisyphus.HWDBUploader._Sheet import Sheet
from Sisyphus.Utils.Terminal import Style

import json
import sys
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import re

pp = lambda s: print(json.dumps(s, indent=4))

printcolor = lambda c, s: print(Style.fg(c)(s))

class Encoder:
    def __init__(self, encoder_def):
        self._encoder_def = deepcopy(encoder_def)
        enc = deepcopy(self._encoder_def)
        
        self.name = enc.pop("Encoder Name", None)
        self.record_type = enc.pop("Record Type", None)
        self.part_type_name = enc.pop("Part Type Name", None)
        self.part_type_id = enc.pop("Part Type ID", None)
        self.test_name = enc.pop("Test Name", None)

        self.options = enc.pop("Options", {})
        self.schema = enc.pop("Schema", {})

        # TODO: more fields

        printcolor("cornflowerblue", "Encoder Def Unused Keys")
        printcolor("cornflowerblue", json.dumps(enc, indent=4))

    def _preprocess_schema(self, schema):
        ...
    

    def get_field(self, sheet, column, row_index):
        ...


    def encode(self, sheet):
        result = {}
        printcolor("lime", f"Record Type: {self.record_type}")

        for row_index in range(sheet.rows):
            ...   


        return result

    def decode(self, obj):
        ...

