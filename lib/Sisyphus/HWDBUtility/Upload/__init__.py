#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

import sys, os
import json
import argparse

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.HWDBUtility.Docket import Docket
from Sisyphus.Utils.Terminal.Style import Style

class Uploader():
    def __init__(self, docket=None):
        
        if isinstance(docket, Docket):
            self.docket = docket
        elif isinstance(docket, str):
            self.docket = Docket(filename=docket)
        else:
            self.docket = Docket(definition=docket)

        Style.notice.print("Loading Sheets...")
        self.docket.load_sheets()

    @classmethod
    def fromCommandLine(self, argv=None):
        #{{{
        # Since we're probably not being invoked directly, we let the
        # calling script tell us what its name is, so we can adjust
        # our "help" screen accordingly.

        argv = argv or sys.argv
        prog_parser = argparse.ArgumentParser(add_help=False)
        prog_parser.add_argument('--progname')
        prog_args, argv = prog_parser.parse_known_args(argv)
        progname = prog_args.progname
        if progname is not None:
            progname = os.path.basename(progname)
            _ = argv.pop(0)
        else:
            progname = os.path.basename(argv.pop(0))

        description = "HWDB Upload Utility"

        arg_table = [
            (
                ('files',),
                {"metavar": "file", 'nargs': '*', "default": None}
            ),
            (
                ('--record-type',),
                {}
            ),
            (
                ('--test-name',),
                {}
            ),
            (
                ('--part-type-id',),
                {}
            ),
            (
                ('--part-type-name',),
                {}
            ),
            (
                ('--value',),
                {'metavar': ('key', 'value'), 'nargs': 2, 'action': 'append'}
            ),
            (
                ('--submit',),
                {'dest': 'submit', 'action': 'store_true'}
            ),
        ]

        parser = argparse.ArgumentParser(
                    prog=progname,
                    description=description,
                    add_help=True)

        for args, kwargs in arg_table:
            parser.add_argument(*args, **kwargs)

        args = parser.parse_args(argv)

        data_files = []
        docket_files = []
        values = {}

        for filename in args.files:
            suffix = filename.split('.')[-1].lower()
            if suffix in ['csv', 'txt', 'xlsx']:
                data_files.append(filename)
            elif suffix in ['py', 'json', 'json5']:
                docket_files.append(filename)
            else:
                print(f"'{filename}' does not appear to be a valid file type")

        if args.record_type is not None:
            values["Record Type"] = args.record_type
        if args.test_name is not None:
            values["Test Name"] = args.test_name
        if args.part_type_id is not None:
            values["Part Type ID"] = args.part_type_id
        if args.part_type_name is not None:
            values["Part Type Name"] = args.part_type_name

        for key, value in (args.value or []):
            values[key] = value

        # Construct a "starter" docket
        cmd_docket = \
        {
            'Docket Name': 'Command Line Args',
            'Sources': data_files,
            'Values': values,
            'Includes': docket_files,
        }

        
        #print(json.dumps(cmd_docket, indent=4))

        return Uploader(cmd_docket)
        #}}}






