#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 09:28:15 2023

@author: alexwagner
"""

import json
from Sisyphus import RestApiV1 as ra
from Sisyphus.RestApiV1 import Utilities as ut

kwargs = {
            #"part_type_id": "Z00100300022",
            "part_type_id": None,
            "part_type_name": None,
            "part_id": "Z00100300022-00064",
            "serial_number": None,
            "count": 2
        }

items = ut.fetch_hwitems(**kwargs)

print(json.dumps(items, indent=4))

items_again = ut.fetch_hwitems(**kwargs)



