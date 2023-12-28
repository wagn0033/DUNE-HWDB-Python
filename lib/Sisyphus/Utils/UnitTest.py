#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/Utils/UnitTest.py
Copyright (c) 2023 Regents of the University of Minnesota
Author:
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import unittest

class LoggedTestCase(unittest.TestCase):
    """Extends unittest.TestCase to automatically log test cases"""
    logger = logger

    def setUp(self):
        self.maxDiff = 0x10000
        self.logger.info(f"[TEST {self._testMethodName}]")
        if self._testMethodDoc is not None:
            doc_first_line = self._testMethodDoc.split('\n', 1)[0]
            self.logger.info(f"__doc__: {doc_first_line}")

    def tearDown(self):
        has_error = self._outcome.errors[-1][1] is not None

        if not has_error:
            self.logger.info(f"[PASS {self._testMethodName}]")
        else:
            self.logger.error(f"[FAIL {self._testMethodName}]")
