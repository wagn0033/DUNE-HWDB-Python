#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/RestApiV1/Test__patch_hwitem.py
Copyright (c) 2023 Regents of the University of Minnesota
Authors: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy
"""

import unittest
from get_tests.test__get_hwitem import *
from get_tests.test__get_misc import *
from get_tests.test__get_component_types import *
from get_tests.test__get_tests import *

from post_tests.test__post_bulk_add import *
from post_tests.test__post_subcomponent import *
from post_tests.test__post_hwitem import *
from post_tests.test__post_tests import *

from patch_tests.test__patch_bulk_update import *
from patch_tests.test__patch_enables import *
from patch_tests.test__patch_hwitem import *

if __name__ == "__main__":
    unittest.main(argv=config.remaining_args)
