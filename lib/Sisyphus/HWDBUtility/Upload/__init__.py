#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

import sys, os
import json
import argparse
from datetime import datetime, timezone

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus
from Sisyphus.HWDBUtility.Docket import Docket
from Sisyphus.HWDBUtility.HWItem import HWItem
from Sisyphus.HWDBUtility.HWItemTest import HWItemTest
from Sisyphus.Utils.Terminal.Style import Style

from Sisyphus.Utils.Terminal.BoxDraw import Table
from Sisyphus.Utils.Terminal import BoxDraw

class Uploader():
    def __init__(self, docket=None, args=None):
        #{{{ 
        Style.notice.print("(Uploader) Loading Docket...")
        if isinstance(docket, Docket):
            self.docket = docket
        elif isinstance(docket, str):
            self.docket = Docket(filename=docket)
        else:
            self.docket = Docket(definition=docket)

        self.docket.values["DUNE HWDB Utility Version"] = Sisyphus.version
        self.docket.values["Uploaded"] = datetime.now().astimezone().replace(microsecond=0).isoformat()

        if args:
            self._submit = args.submit


        Style.notice.print("(Uploader) Loading Sheets...")
        self.docket.load_sheets()

        Style.notice.print("(Uploader) Verifying Encoders...")
        self.docket.verify_encoders()

        Style.notice.print("(Uploader) Applying Encoders...")

        self.raw_jobs = self.docket.apply_encoders()

        self.analyze_jobs()

        #Style.info.print(json.dumps(jobs, indent=4))

        self.execute_jobs()
        #}}}

    def execute_jobs(self):
        #{{{
        for new_item in self.new_items:
            if self._submit:
                Style.notice.print("\nCreating new item:")
            else:
                Style.notice.print("\nCreating new item (SIMULATED):")

            print(new_item)

            if self._submit:
                new_item.update_core()
                new_item.update_enabled()

        for edited_item in self.edited_items:
            if self._submit:
                Style.notice.print("\nEditing an item:")
            else:
                Style.notice.print("\nEditing an item (SIMULATED):")
            print(edited_item)

            if self._submit:
                edited_item.update_core()
                edited_item.update_enabled()


        for merge_test in self.merge_tests:
            if self._submit:
                Style.notice.print("\nMerging tests:")
            else:
                Style.notice.print("\nMerging tests (SIMULATED):")
            print(merge_test)

            if self._submit:
                merge_test.update()

        #}}}


    def analyze_jobs(self):
        #{{{
        self.new_items = []
        self.edited_items = []
        self.merge_tests = []

        #......................................................................

        def queue_item_job(raw_job):
            #Style.notice.print(json.dumps(raw_job, indent=4))
            hwitem = HWItem.fromUserData(raw_job["Data"])
            #Style.error.print(json.dumps(hwitem._current, indent=4))
            if hwitem.is_new():
                print(f"Queuing CREATE job for Item {hwitem._current['serial_number']} "
                        f"(type: {hwitem._current['serial_number']})")
                self.new_items.append(hwitem)
            else:
                if hwitem.has_changed():
                    print(f"Queuing UPDATE job for Item {hwitem._current['part_id']} "
                            f"({hwitem._current['serial_number']})")
                    self.edited_items.append(hwitem)
                else:
                    print(f"Item {hwitem._current['part_id']} "
                        f"({hwitem._current['serial_number']}) has not changed")

        #......................................................................
        
        def queue_test_job(raw_job):
            
            #Style.info.print(json.dumps(raw_job, indent=4))
            hwitemtest = HWItemTest.fromUserData(raw_job["Data"])
            #Style.error.print(json.dumps(hwitemtest._current, indent=4))
            #print(hwitemtest)
            self.merge_tests.append(hwitemtest)
        #......................................................................
        
        raw_jobs = self.raw_jobs

        #Style.warning.print(json.dumps(raw_jobs, indent=4))
        #return

        while len(raw_jobs) > 0:
            current_job = raw_jobs.pop(0)
            record_type = current_job["Record Type"]
            if record_type == "Item":
                #print("FOUND ITEM")
                queue_item_job(current_job)
            elif record_type == "Test":
                queue_test_job(current_job)
            else:
                print("FOUND SOMETHING ELSE")


        print(f'New Items: {len(self.new_items)}')
        print(f'Edited Items: {len(self.edited_items)}')
        #}}}


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

        return Uploader(cmd_docket, args)
        #}}}






