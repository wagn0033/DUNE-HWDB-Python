#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
"""

import sys
from Sisyphus.Utils import UnitTest as unittest
from Sisyphus.Configuration import config


from get_tests.test__get_hwitem import *
from get_tests.test__get_misc import *
from get_tests.test__get_component_types import *
from get_tests.test__get_tests import *
from get_tests.test__get_images import *

from post_tests.test__post_hwitems_bulk import *
from post_tests.test__post_subcomponent import *
from post_tests.test__post_hwitem import *
from post_tests.test__post_tests import *
from post_tests.test__post_images import *

from patch_tests.test__patch_hwitems_bulk import *
from patch_tests.test__patch_enables import *
from patch_tests.test__patch_hwitem import *

class RealTimeTestResult(unittest.TextTestResult):
    """
    def startTest(self, test):
        super(RealTimeTestResult, self).startTest(test)
        self.stream.write(f"\n{test.__class__.__name__}.{test._testMethodName} ... ")
        self.stream.write(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.stream.flush()
        """

    def addSuccess(self, test):
        super(RealTimeTestResult, self).addSuccess(test)
        self.stream.write("ok\n")
        self.stream.flush()

    def addError(self, test, err):
        super(RealTimeTestResult, self).addError(test, err)
        self.stream.write("ERROR\n")
        self.stream.flush()

    def addFailure(self, test, err):
        super(RealTimeTestResult, self).addFailure(test, err)
        self.stream.write("FAIL\n")
        self.stream.flush()

class RealTimeTestRunner(unittest.TextTestRunner):
    resultclass = RealTimeTestResult

if __name__ == "__main__":
    #test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    #custom runner
    runner = RealTimeTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(suite)

    #exit with status code
    sys.exit(not result.wasSuccessful())