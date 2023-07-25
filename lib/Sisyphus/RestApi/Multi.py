#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/RestApi/Multi.py
Copyright (c) 2022 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Configuration import config
logger = config.getLogger("RestApi/Multi")

from Sisyphus import RestApi as ra
#from Sisyphus.Logging import logging
#logger = logging.getLogger(__name__)

import threading
import queue
import json
from copy import copy
from datetime import datetime

class PrioritizedTask:
    PRIORITY_HIGH = 1
    PRIORITY_LOW = 2
    def __init__(self, priority, task):
        self.priority = priority
        self.task = task
        
    def __lt__(self, other):
        return self.priority < other.priority


class ItemList:
    MAX_RETRIES = 3
    class Abandon(Exception):
        '''Exception raised when a task has reached its retry limit'''
        pass
    
    def __init__(self, 
                 type_id, 
                 num_threads=10, 
                 retries=MAX_RETRIES, 
                 raise_on_abandon=True,
                 block=True,
                 status_callback=None,
                 status_interval=0.2,
                 serial_numbers=None):
        thread_name = threading.current_thread().name
        self.type_id = type_id
        self.tasks = queue.PriorityQueue()
        self.results = []
        self.condition = threading.Condition()
        self.raise_on_abandon = raise_on_abandon
        self.fail_retry = 0
        self.fail_abandon = 0
        self.voluntary_abandon = False
        self.retries = retries
        self.status_callback = status_callback
        self.status_interval = status_interval
        self.block = block
        self.serial_numbers = set(serial_numbers)
        
        self.num_pages = 1
        self.page_size = 1
        self.num_items = 1
        
        task = PrioritizedTask(
            priority = PrioritizedTask.PRIORITY_HIGH,
            task =
                {
                    "task_name": f"TypeID {type_id}: get page 1 of ?",
                    "function": self._get_page,
                    "args": [],
                    "kwargs":
                    {
                        "page": 1,
                        "tries_remaining": self.retries,
                    }
                })
        self.tasks.put(task)
        
        self.threads = []
        
        for i in range(num_threads):
            th_name = f"Thread_{i}"
            logger.debug(f"Starting {th_name}")
            thread = threading.Thread(target=self._process_tasks, args=(), name=th_name)
            thread.start()
            self.threads.append(thread)
        
        logger.debug(f"{thread_name}: All threads started.")
        
        if self.block:
            self.wait()
        
    def wait(self):
        thread_name = threading.current_thread().name
        while len(self.threads) > 0:
            logger.debug(f"{thread_name}: Waiting for threads to finish. {len(self.threads)} threads remain.")
            logger.debug(f"{thread_name}: There are {self.tasks.unfinished_tasks} unfinished tasks "
                          f"and {self.tasks.qsize()} tasks waiting for threads.")
            for thread in self.threads:
                thread.join(0.2)
                if not thread.is_alive():
                    break
            if not thread.is_alive():
                self.threads.remove(thread)
        logger.debug(f"{thread_name}: All threads are finished.")

        if self.raise_on_abandon and self.fail_abandon > 0:
            logger.error("Raising Abandon exception because max retries was exceeded.")
            raise self.__class__.Abandon("A required REST API task could not be completed.")   
    
    @property
    def fail_abandon(self):
        return self._fail_abandon
    @fail_abandon.setter
    def fail_abandon(self, value):
        self._fail_abandon = value
        if self.raise_on_abandon and value > 0:
            with self.condition:
                self.condition.notify_all()
  
    @property
    def voluntary_abandon(self):
        return self._voluntary_abandon
    @voluntary_abandon.setter
    def voluntary_abandon(self, value):
        self._voluntary_abandon = value
        if self.raise_on_abandon and value:
            with self.condition:
                self.condition.notify_all()  
  
    @classmethod
    def get_items(cls, type_id, num_threads=10, retries=5, fail_on_abandon=True):
        item_list = cls(type_id, num_threads=num_threads,
                        retries=retries, fail_on_abandon=fail_on_abandon)
        return item_list.results
    
    def _add_result(self, result):
        self.results.append(result)
    
    def _process_tasks(self):
        thread_name = threading.current_thread().name
        logger.debug(f"{thread_name} started.")
        while True:
            
            try:
                #logger.debug(f"{thread_name}: requests task")
                ticket = self.tasks.get(block=False)
                task = ticket.task
                logger.debug(f"{thread_name}: gets task {task['task_name']}")
                task["function"](*task["args"], **task["kwargs"])    
                
            except queue.Empty:
                logger.debug(f"{thread_name}: queue is empty. Waiting.")
                with self.condition:
                    self.condition.wait()
                logger.debug(f"{thread_name}: received notify. Resuming.")
            
            if self.tasks.unfinished_tasks == 0:
                logger.debug(f"{thread_name}: there are no tasks left. waking other threads.")     
                with self.condition:
                    self.condition.notify_all()
                break
            
            if self.voluntary_abandon:
                logger.debug(f"{thread_name}: signaled to terminate with {self.tasks.unfinished_tasks} items "
                             "still in the queue")
                with self.condition:
                    self.condition.notify_all()
                break
            
            if self.raise_on_abandon and self.fail_abandon > 0:
                logger.error(f"{thread_name}: a task exceeded its retry limit. raising error.")
            
            
        logger.debug(f"{thread_name}: finished") 
               
    def _get_page(self, page, tries_remaining=1):
        thread_name = threading.current_thread().name
        while tries_remaining > 0:
            resp = ra.get_components(self.type_id, page=page)
            if resp["status"] == "OK":
                if page == 1:
                    self.num_pages = resp["pagination"]["pages"]
                    if self.num_pages > 1:
                        # assume the page size must be the same as the size of what
                        # we just got
                        self.page_size = len(resp["data"])
                        # we don't know how big the last page will be, so let's just
                        # say it's half the page size
                        self.num_items = self.page_size * (self.num_pages-1) + self.page_size//2
                    else:
                        self.num_items = len(resp["data"])
                        
                    for addl_page in range(2, self.num_pages+1):
                        task = PrioritizedTask(
                            priority = PrioritizedTask.PRIORITY_HIGH,
                            task =
                                {
                                    "task_name": f"TypeID {self.type_id}: get page {addl_page} of {self.num_pages}",
                                    "function": self._get_page,
                                    "args": [],
                                    "kwargs":
                                    {
                                        "page": addl_page,
                                        "tries_remaining": self.retries,
                                    }
                                })        
                        self.tasks.put(task) 
                elif page == self.num_pages:
                    self.num_items = self.page_size * (self.num_pages-1) + len(resp["data"])

                
                for item in resp["data"]:
                    ext_id = item["part_id"]
                    task = PrioritizedTask(
                        priority = PrioritizedTask.PRIORITY_LOW,
                        task =
                            {
                                "task_name": f"ExtID {ext_id}: get item",
                                "function": self._get_item,
                                "args": [],
                                "kwargs":
                                {
                                    "ext_id": ext_id, 
                                    "tries_remaining": self.retries,
                                }
                            })        
                    self.tasks.put(task)
                logger.debug(f"{thread_name}: {len(resp['data'])} tasks added to queue.")
                break
            else:
                tries_remaining -= 1
                self.fail_retry += 1
                logger.error(f"{thread_name}: Error getting page {page}. Will try {tries_remaining} more times.")
                logger.error(f"{thread_name}: \n{json.dumps(resp, indent=4)}")
        
        else: # triggers only if "while" exited without breaking
            self.fail_abandon += 1
        
        self.tasks.task_done()
        with self.condition:
            self.condition.notify_all()
  
    def _get_item(self, ext_id, tries_remaining=1):
        thread_name = threading.current_thread().name
        #print(thread_name)
        while tries_remaining > 0:
            resp = ra.get_component(ext_id)
            if resp["status"] == "OK":
                if self.serial_numbers is not None:
                    serial_number = resp['data']['serial_number']
                    if serial_number in self.serial_numbers:
                        self._add_result(resp['data'])
                        self.serial_numbers.remove(serial_number)
                        if len(self.serial_numbers) == 0:
                            self.voluntary_abandon = True
                else:    
                    self._add_result(resp['data']) 
                break
            else:
                tries_remaining -= 1
                self.fail_retry += 1
                #logger.error(f"{thread_name}: The response contained an error: {resp}")
                logger.error(f"{thread_name}: Error getting ext_id {ext_id}. Will try {tries_remaining} more times.")
        else: # weird python feature-- "else" triggers only if "while" exited without breaking
            self.fail_abandon += 1
        
        if self.status_callback is not None:
            self.status_callback(self)
        
        self.tasks.task_done()
        
        
def run_test():
    
    import argparse
    from Sisyphus.Utils.Terminal import ProgressBar
    
    parser = argparse.ArgumentParser(description='TBD')
    parser.add_argument('--threads',
                        dest='threads',
                        required=False,
                        default=10,
                        help='tbd')
    parser.add_argument('--typeid',
                        dest='typeid',
                        required=False,
                        default="Z00100100007",
                        help='tbd')
    args = parser.parse_args()
    
    num_threads = int(args.threads)
    typeid = args.typeid
    
    print(f"begin test for typeid='{typeid}' with {num_threads} threads")
    start_time = datetime.now()
    
    global prog 
    prog = ProgressBar(1, prefix='Fetching items:', suffix='', decimals=1, length=50, fill='█', printEnd='\r')
    
    def update_status(item_list):
        global prog
        prog.total = item_list.num_items
        prog.update(len(item_list.results))
        #print(f"{len(item_list.results)} of {item_list.num_items} items found.")
    
    
    L = ItemList(typeid, num_threads=num_threads, status_callback=update_status, block=False)
    print("and now we wait.")
    L.wait()

    end_time = datetime.now()
    interval = end_time - start_time
    num_results = len(L.results)
    
    #print(json.dumps(L.results, indent=4))
    print(f"{num_results} results found.")
    print(f"The test executed in {interval}")
    print(f"Throughput: {num_results/interval.total_seconds():0.2f} items/second")
    
    if L.fail_retry > 0:
        print(f"fail/retry: {L.fail_retry}")
    if L.fail_abandon > 0:
        print(f"fail/abandon: {L.fail_abandon}")
    
    
    print("end test")

if __name__ == '__main__':
    run_test()
    
