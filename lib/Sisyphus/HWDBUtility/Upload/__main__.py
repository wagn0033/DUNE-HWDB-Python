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
from Sisyphus.Utils.Terminal.Style import Style
from Sisyphus import RestApiV1 as ra
ra.session_kwargs["timeout"] = 10



def main(argv=None):
    logger.info(f"Starting {__name__}")
    uploader = Uploader.fromCommandLine(argv or sys.argv)

    docket = uploader.docket
   
    #Style.notice.print("Combined Docket:") 
    #Style.info.print(docket)

    logger.info(f"Finished {__name__} and exiting.")

if __name__ == "__main__":
    main(argv=config.remaining_args)
