#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 11:18:30 2023

@author: alexwagner
"""

from Sisyphus.Configuration import config
logger = config.getLogger(__name__)

from Sisyphus import RestApiV1 as ra

import threading
import queue
import json
import datetime
import time
import random
from copy import copy, deepcopy


class Task:

    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3

    def __init__(self, *,
                task_name = None,
                priority = None, 
                function = None,
                args = [],
                kwargs = {}):

        if priority is None:
            priority = self.__class__.PRIORITY_MEDIUM

        self.priority = priority
        self.task_name = task_name

    def __lt__(self, other):
        return self.priority < other.priority

class ThreadPool:
    def __init__(self, parent, num_threads=5):
        self.parent = parent
        self.num_threads = num_threads

class WorkerThread:
    def __init__(self, parent):
        pass

    def start(self):
        thread_name = threading.current_thread().name


class Multitasker:

    def __init__(self, num_threads=5):
        self.num_threads = num_threads
        self.thread_pool = ThreadPool(parent=self, num_threads=num_threads)
        self.task_queue = queue.PriorityQueue()

    def add_tasks(self, tasks):
        for task in tasks:
            self.task_queue.put(task)

    def add_task(self, task):
        self.task_queue.put(task)


    def wait(self, timeout=None):
        thread_name = threading.current_thread().name
        while len(self.threads) > 0:
            logger.debug(f"{thread_name}: Waiting for threads to finish. {len(self.threads)} threads remain.")
            logger.debug(f"{thread_name}: There are {self.tasks.unfinished_tasks} unfinished tasks "
                          f"and {self.tasks.qsize()} tasks waiting for threads.")
            for thread in self.thread_pool:
                thread.join(0.2)
                if not thread.is_alive():
                    break
            if not thread.is_alive():
                self.threads.remove(thread)
        logger.debug(f"{thread_name}: All threads are finished.")

###############################################################################
#
#  Example Usage
#
###############################################################################

# Example "task" function
def procrastinate(sleep_time, return_value):
    thread_name = threading.current_thread().name
    logger.debug(f"starting <procrastinate> in thread <{thread_name}>")
    logger.debug(f"<procrastinate> sleeping for <{sleep}> seconds")
    time.sleep(sleep_time)
    logger.debug(f"finished <procrastinate> in thread <{thread_name}>")
    return return_value

def main():
    
    tasks = \
    [
        Task(
            task_name="Task 1",
            function=procrastinate,
            priority=Task.PRIORITY_MEDIUM,
            kwargs=
            {
                "sleep_time": 5, 
                "return_value": "ABC",
            }
        ),
        Task(
            task_name="Task 2",
            function=procrastinate,
            priority=Task.PRIORITY_MEDIUM,
            kwargs=
            {
                "sleep_time": 3, 
                "return_value": "DEF",
            }
        ),
    ]

    mt = Multitasker()
    mt.add_tasks(tasks)

    mt.wait()



if __name__ == "__main__":
    main()
    







