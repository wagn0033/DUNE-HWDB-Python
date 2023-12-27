#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bin/advanced-upload-docket.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

import sys
import argparse
import json, json5
from Sisyphus.HWDBUploader import Docket

def parse_args(argv):

    description = "TBD"

    arg_table = [
        (('docket',), {"metavar": "filename", "nargs": 1}),
        #(('--docket',), {"dest": "docket", "required": True, "metavar": "filename"}),
        (('--submit',), {"dest": "submit", "action": "store_true"}),
        #(('--ignore-warnings',), {"dest": "ignore", "action": "store_true"}),
    ]

    parser = argparse.ArgumentParser(description=description, add_help=True)

    for args, kwargs in arg_table:
        parser.add_argument(*args, **kwargs)
    
    # THIS IS BROKEN... I want to pass argv to it, but it just doesn't behave the same.
    # but I don't need to fix this right now.
    args = parser.parse_args()
    return args


def main(argv):
    args = parse_args(argv)

    docket_file = args.docket[0]
    ext = docket_file.split('.')[-1]
        
    try:
        with open(docket_file, "r") as f:
            contents = f.read()
    except Exception as ex:
        print(f"Exception: {type(ex)} {ex}")
        raise ex
    
    if ext.lower() in ["json", "json5"]:
        docket_def = json5.loads(contents)
    elif ext.lower() in ["py",]:
        _locals = {}
        exec(contents, globals(), _locals)
        docket_def = _locals["contents"]
    
    docket = Docket(docket_def)

    docket.process_sources()
    if args.submit:
        docket.update_hwdb()
    else:
        docket.display_plan()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
