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
from copy import deepcopy

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

import Sisyphus
from Sisyphus.HWDBUtility.Docket import Docket
from Sisyphus.HWDBUtility.HWItem import HWItem
from Sisyphus.HWDBUtility.HWTest import HWTest
from Sisyphus.HWDBUtility.SheetWriter import ExcelWriter

from Sisyphus.Utils.Terminal.Style import Style
from Sisyphus.Utils.Terminal.BoxDraw import Table
from Sisyphus.Utils.Terminal import BoxDraw

class Uploader():
    def __init__(self, docket=None, args=None):
        #{{{
        
        self.upload_time = datetime.now().astimezone().replace(microsecond=0)
        self.output_path = self.upload_time.replace(tzinfo=None).strftime('%Y%m%dT%H%M%S')
        
        if args:
            self._submit = args.submit
        else:
            self._submit = False

        #
        # Load the docket
        #
        if isinstance(docket, Docket):
            self.docket = docket
        elif isinstance(docket, str):
            self.docket = Docket(filename=docket)
        else:
            self.docket = Docket(definition=docket)
        self.docket.values["DUNE HWDB Utility Version"] = Sisyphus.version
        self.docket.values["Uploaded"] = self.upload_time.isoformat()

        # 
        # Use the docket to get raw job data
        #
        self.docket.load_sheets()
        self.docket.verify_encoders()
        self.raw_job_data = self.docket.apply_encoders()


        self.item_queue_new = []
        self.item_queue_edit = []
        self.test_queue_new = []
        self.item_summary = {} # we'll write these as sheets
        self.test_summary = {}

        #
        # Turn the raw job data into actionable jobs
        #
        self.process_raw_job_data()


        #self.execute_jobs()
        #}}}

    #--------------------------------------------------------------------------

    def output_receipts(self):
        if not (self.item_summary or self.test_summary):
            return

        ...
    
    #--------------------------------------------------------------------------

    def execute_jobs(self):
        #{{{
        for new_item in self.item_queue_new:
            if self._submit:
                Style.notice.print("\nCreating new item:")
            else:
                Style.notice.print("\nCreating new item (SIMULATED):")

            print(new_item)

            new_item.validate()
            if self._submit:
                new_item.update_core()
                new_item.update_enabled()

        for edited_item in self.item_queue_edit:
            if self._submit:
                Style.notice.print("\nEditing an item:")
            else:
                Style.notice.print("\nEditing an item (SIMULATED):")
            print(edited_item)

            edited_item.validate()
            if self._submit:
                edited_item.update_core()
                edited_item.update_enabled()


        for merge_test in self.test_queue_new:
            if self._submit:
                Style.notice.print("\nMerging tests:")
            else:
                Style.notice.print("\nMerging tests (SIMULATED):")
            print(merge_test)

            if self._submit:
                merge_test.update()

        #}}}

    #--------------------------------------------------------------------------

    def queue_item_job(self, raw_job):
        #{{{ 
        #print(json.dumps(raw_job["Data"], indent=4))
        print(raw_job)
        exit()
        hwitem = HWItem.fromUserData(raw_job["Data"])
        if hwitem.is_new():
            print(f"Queuing CREATE job for Item {hwitem._current['serial_number']} "
                    f"(type: {hwitem._current['serial_number']})")
            self.item_queue_new.append(hwitem)
        else:
            print(f"Queuing UPDATE job for Item {hwitem._current['part_id']} "
                    f"({hwitem._current['serial_number']})")
            self.item_queue_edit.append(hwitem)

        encoder = raw_job['Encoder']
        user_record = hwitem.toUserData()

        sheet_data = encoder.decode(user_record)
        
        #Style.info.print("USER RECORD", json.dumps(user_record, indent=4))
        #Style.info.print("ROW DATA", json.dumps(sheet_data, indent=4))
        
        part_type_id = user_record["Part Type ID"]
        part_type_name = user_record["Part Type Name"]
        part_id = user_record["External ID"]
        serial_number = user_record["Serial Number"]
        
        part_type_dict = self.item_summary.setdefault(part_type_id, {})
        part_type_dict["Part Type ID"] = part_type_id
        part_type_dict["Part Type Name"] = part_type_name

        if part_id:
            part_type_edit = (
                    part_type_dict
                        .setdefault("edit", {})
                        .setdefault(part_id, sheet_data)
                    )
        else:
            part_type_new = (
                    part_type_dict
                        .setdefault("new", {})
                        .setdefault(serial_number, sheet_data)
                    )
        #}}}
    
    #--------------------------------------------------------------------------

    def queue_test_job(self, raw_job):
        #{{{            
        #Style.info.print(json.dumps(raw_job, indent=4))
        hwtest = HWTest.fromUserData(raw_job["Data"])
        #Style.error.print(json.dumps(hwtest._current, indent=4))
        #print(hwtest)

        print(f"Queuing MERGE TEST job for Item {hwtest._current['serial_number']}")

        self.test_queue_new.append(hwtest)
        #}}}        

    #--------------------------------------------------------------------------
        
    def create_item_sheet(self, item_summary):
        #{{{
        
        header = {
            "Record Type": "Item",
            "Part Type ID": item_summary["Part Type ID"],
            "Part Type Name": item_summary["Part Type Name"],
        }            

        # I guess it's possible to have two items of the same type coming
        # from different encoders, so we should check every item to make
        # sure we get all fields
        all_fields = {}
        
        # When checking if some values are the same for every single item,
        # we only want to look at the first row for that item, because the
        # other rows won't change it, and if we implement sparse rows, we
        # don't want to get confused if those fields are empty for the 2nd
        # row and beyond
        first_rows = []

        for part_id, rows in item_summary.get("edit", {}).items():
            first_rows.append(deepcopy(rows[0]))
            all_fields.update({k: None for k in rows[0].keys()})
        for part_id, rows in item_summary.get("new", {}).items():
            first_rows.append(deepcopy(rows[0]))
            all_fields.update({k: None for k in rows[0].keys()})

        #print(list(all_fields))

        #print(first_rows)

        # Get rid of some fields that we definitely don't need because
        # they're redundant
        all_fields.pop("Part Type ID", None)
        all_fields.pop("Part Type Name", None)
        all_fields.pop("Manufacturer ID", None)
        all_fields.pop("Manufacturer Name", None)
        all_fields.pop("Institution ID", None)
        all_fields.pop("Institution Name", None)
        all_fields.pop("Country Code", None)
        all_fields.pop("Country Name", None)

        # Figure out which fields can be summarized in the header because
        # every item has the same value. Only allow certain fields to be
        # summarized.
        summarizable_fields = ["Manufacturer", "Institution", "Country", "Enabled"]
        for field in summarizable_fields:
            values = [d.get(field, None) for d in first_rows]
            if len(set(values)) == 1:
                header[field] = values[0]
                all_fields.pop(field, None)

        table = [
            #list(all_fields)
        ]
        
        
        # Let's add in the rows now, finally.
        for part_id in sorted(item_summary.get("edit", {}).keys()):
            rows = item_summary["edit"][part_id]
            for row in rows:
                sheet_row = {s: row.get(s, "") for s in all_fields }
                table.append(sheet_row)
        for part_id in sorted(item_summary.get("new", {}).keys()):
            rows = item_summary["new"][part_id]
            for rownum, row in enumerate(rows):
                sheet_row = {s: row.get(s, "") for s in all_fields }
                if rownum == 0:
                    sheet_row["External ID"] = "<unassigned>"
                table.append(sheet_row)

        # Since wildcards work for Institution and Manufacturer, let's trim the
        # really long ones if they occur in the table. If they're in the header,
        # they have enough room, so leave them alone.
        max_length = 50
        trimmable_fields = ["Institution", "Manufacturer"]
        for sheet_row in table:
            for field in trimmable_fields:
                if field in sheet_row and len(sheet_row[field]) > max_length:
                    sheet_row[field] = sheet_row[field][:max_length-1] + "%"

        EW = ExcelWriter("HWDB_Upload_Summary.xlsx")
        EW.add_sheet(header["Part Type ID"], header, table)
        EW.close()


        print(json.dumps(table, indent=4))
        #print(header)
        #print()
        #print('\n'.join(str(s) for s in table))

        #print(json.dumps(self.item_summary, indent=4))
        #}}}

    #--------------------------------------------------------------------------

    def process_raw_job_data(self):
        #{{{

        raw_jobs = self.raw_job_data

        #Style.warning.print(json.dumps(raw_jobs, indent=4))
        #return

        while len(raw_jobs) > 0:
            current_job = raw_jobs.pop(0)
            record_type = current_job["Record Type"]
            if record_type == "Item":
                #print("FOUND ITEM")
                self.queue_item_job(current_job)
            elif record_type == "Test":
                self.queue_test_job(current_job)
            else:
                print("FOUND SOMETHING ELSE")
        
        for part_type_id, item_summary in self.item_summary.items():
            self.create_item_sheet(item_summary)
        #create_item_sheet(self.item_summary)
        #print(json.dumps(self.item_summary, indent=4))
        



        print(f'New Items: {len(self.item_queue_new)}')
        print(f'Edited Items: {len(self.item_queue_edit)}')
        


        #}}}

    #--------------------------------------------------------------------------

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






