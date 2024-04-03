#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Regents of the University of Minnesota
Authors: 
    Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
    Urbas Ekka <ekka0002@umn.edu>, Dept. of Physics and Astronomy

Test RestApiV1 functions related to getting images
"""

from Sisyphus.Utils import UnitTest as unittest

import os, shutil
import json

from Sisyphus.RestApiV1 import get_hwitem
from Sisyphus.RestApiV1 import get_hwitem_image_list
from Sisyphus.RestApiV1 import get_component_type_image_list
from Sisyphus.RestApiV1 import get_image
from Sisyphus import RestApiV1 as ra

from Sisyphus.Utils.Terminal.Image import image2text

class Test__get_images(unittest.TestCase):
    """Test RestApiV1 functions related to getting images"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.download_path = os.path.join(
                os.path.dirname(__file__),
                "images", "download")
        shutil.rmtree(cls.download_path, ignore_errors=True)
        os.makedirs(cls.download_path)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()   
       
    #----------------------------------------------------------------------------- 
    
    def test__get_component_type_image_list(self):
        """Get a list of images stored for a component type

        Tests that a particular component type in the database has at least
        one image, and that the entries representing each image has the
         correct fields.
        """

        expected_fields = {
            "comments", "created", "creator", "image_id", "image_name",
            "library", "link"
        }

        resp = get_component_type_image_list("Z00100300006")

        # We'll only test that there's at least one image, and that
        # we don't raise an exception when we fetch it.             
        self.assertEqual(resp["status"], "OK")
        self.assertGreater(len(resp["data"]), 0)
        for image_node in resp["data"]:
            self.assertSetEqual(set(image_node.keys()), expected_fields)
            image_name = os.path.join(self.download_path, image_node["image_name"])
            resp = get_image(image_node["image_id"], write_to_file=image_name)
            textimage = image2text(resp.content, columns=40)
            self.logger.info("\n" + textimage)
            break

    #----------------------------------------------------------------------------- 
    
    def test__get_hwitem_image_list(self):
        """Get a list of images stored for an item

        Tests that a particular item in the database has at least one image,
        and that the entries representing each image has the correct fields.
        """

        expected_fields = {
            "comments", "created", "creator", "image_id", "image_name",
            "library", "link"
        }

        resp = get_hwitem_image_list("Z00100300006-00001")

        # We'll only test that there's at least one image, and that
        # we don't raise an exception when we fetch it.             
        self.assertEqual(resp["status"], "OK")
        self.assertGreater(len(resp["data"]), 0)
        for image_node in resp["data"]:
            self.assertSetEqual(set(image_node.keys()), expected_fields)
            image_name = os.path.join(self.download_path, image_node["image_name"])
            resp = get_image(image_node["image_id"], write_to_file=image_name)
            textimage = image2text(resp.content, columns=40)
            self.logger.info("\n" + textimage)
            break

    ##############################################################################                                
if __name__ == "__main__":
    unittest.main()
