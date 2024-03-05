#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus.Utils.utils import preserve_order, restore_order, serialize_for_display
from Sisyphus.Utils.Terminal.Style import Style

from Sisyphus.DataModel import HWItem
from Sisyphus.DataModel import HWTest


import multiprocessing.dummy as mp # multiprocessing interface, but uses threads instead
import json
from uuid import uuid4 as uuid

green = Style.fg(0x00ff00)
jdump = lambda s: green.print(json.dumps(serialize_for_display(s), indent=4))


_lock = mp.threading.Lock()

_debug_no_async = False

class JobManager:

    def __init__(self, job_requests, num_threads=25):
        #{{{
        self.thread_pool = mp.Pool(processes=num_threads)

        if _debug_no_async:
            self._apply = self.thread_pool.apply
        else:
            self._apply = self.thread_pool.apply_async

        self.item_job_total = 0
        self.test_job_total = 0
        self.item_image_job_total = 0
        self.test_image_job_total = 0

        self.item_job_count = 0
        self.test_job_count = 0
        self.item_image_job_count = 0
        self.test_image_job_count = 0
        
        self.item_jobs = {}
        self.test_jobs = {}
        self.item_image_jobs = {}
        self.test_image_jobs = {}

        self.add_jobs(job_requests)
        #}}}

    def add_jobs(self, job_requests):
        #{{{
        # Let's count up each type of job first
        for job_request in job_requests:
            record_type = job_request["Record Type"]
            if record_type == "Item":
                self.item_job_total += 1
            if record_type == "Test":
                self.test_job_total += 1
            if record_type == "Item Image":
                self.item_image_job_total += 1
            if record_type == "Test Image":
                self.test_image_job_total += 1

        while job_requests and not hasattr(self, "_exception"):
            job_request = job_requests.pop(0)
            record_type = job_request["Record Type"]
            
            if record_type == "Item":
                self.add_item(job_request)
            if record_type == "Test":
                self.add_test(job_request)
            if record_type == "Item Image":
                self.add_item_image(job_request)
            if record_type == "Test Image":
                self.add_test_image(job_request)

        self.thread_pool.close()
        self.thread_pool.join()

        if hasattr(self, "_exception"):
            raise(self._exception)
        #}}}


    def execute(self, submit=False):

        sn_index = {}

        for job_num in sorted(self.item_jobs.keys()):
            job = self.item_jobs[job_num]
            print(job_num, (job.part_type_id, job.part_id, job.serial_number, job._sn_conflicts))



    def error_callback(self, *args, **kwargs):
        #print("error callback:", args, kwargs)
        self.thread_pool.terminate()
        self._exception = args[0]

    def regular_callback(self, *args, **kwargs):
        #print("callback:", args, kwargs)
        pass

    def add_item(self, job_request):
        def async_add_item(job_request):
            with _lock:
                self.item_job_count += 1
                item_job_number = self.item_job_count
                self.display_job_queue_status()

            hwitem = HWItem.fromUserData(job_request['Data'])

            with _lock:
                self.item_jobs[item_job_number] = hwitem
                self.display_job_queue_status()

        self._apply(async_add_item, (job_request,), {}, self.regular_callback, self.error_callback)
                 
    def add_test(self, job_request):
        def async_add_test(job_request):
            with _lock:
                self.test_job_count += 1
                test_job_number = self.test_job_count
                self.display_job_queue_status()

            hwtest = HWTest.fromUserData(job_request['Data'])

            with _lock:
                self.test_jobs[test_job_number] = hwtest
                self.display_job_queue_status()
        
        self._apply(async_add_test, (job_request,), {}, self.regular_callback, self.error_callback)


    def add_item_image(self, job_request):
        print('add item image')
    
    def add_test_image(self, job_request):
        print('add test image')

    def display_job_queue_status(self):
        #{{{
        if hasattr(self, "_exception"):
            print("[display_job_queue_status: ignoring because of exceptions]")
            return

        if not hasattr(self, "_job_types_found"):
            Style.notice.print("Queueing Job Requests:")
            self._job_types_found = 0

        if self._job_types_found:
            print(f"\x1b[{self._job_types_found}F", end='')

        job_types_found = 0

        if self.item_job_total:
            job_types_found += 1
            print(f"    \u2022 Item Jobs: {len(self.item_jobs)} / "
                    f"{self.item_job_total}\x1b[K")
        
        if self.test_job_total:
            job_types_found += 1
            print(f"    \u2022 Test Jobs: {len(self.test_jobs)} / "
                    f"{self.test_job_total}\x1b[K")
        
        if self.item_image_job_total:
            job_types_found += 1
            print(f"    \u2022 Item Image Jobs: {len(self.item_image_jobs)} / "
                    f"{self.item_image_job_total}\x1b[K")
        
        if self.test_image_job_total:
            job_types_found += 1
            print(f"    \u2022 Test Image Jobs: {len(self.test_image_jobs)} / "
                    f"{self.test_image_job_total}")

        self._job_types_found = job_types_found
        #}}}
























