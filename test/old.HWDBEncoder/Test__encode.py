#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test/Encoder/Test__encoder.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger()

import os
import json
import unittest
#import random



class Test__encoder(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_encoder_01(self):
        logger.info("Performing test: test_encoder_01")
        

   
if __name__ == "__main__":
    unittest.main()
