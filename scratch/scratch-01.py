#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 09:28:15 2023

@author: alexwagner
"""

import json
from Sisyphus.RestApiV1 import get_component_images, get_image

images = get_component_images("Z00100300001")

print(json.dumps(images, indent=4))

for image_meta in images['data']:
    image_id = image_meta['image_id']
    image_name = image_meta['image_name']

    image_data = get_image(image_id, image_name)
