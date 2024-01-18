#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""
import os
import sys
import json

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.HWDBUtility.Upload import Uploader



def main(argv=None):
    uploader = Uploader.fromCommandLine(argv or sys.argv)

    docket = uploader.docket
    
    combined = \
    {
        "Docket Name": docket.docket_name,
        "Values": docket.values,
        "Sources": docket.sources,
        "Encoders": docket.encoders,
    }

    print(json.dumps(combined, indent=4))

if __name__ == "__main__":
    main(argv=config.remaining_args)
