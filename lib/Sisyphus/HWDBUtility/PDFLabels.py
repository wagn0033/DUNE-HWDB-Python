#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/HWDBUtility/PDFLabels.py
Copyright (c) 2024 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

import Sisyphus
from Sisyphus import RestApiV1 as ra
import multiprocessing.dummy as mp # multiprocessing interface, but uses threads instead
import io
import PIL.Image
from copy import deepcopy
import tempfile

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib import units
    _reportlab_available = True

except ModuleNotFoundError:
    _reportlab_available = False

label_templates = {  #{{{
    "A4": {},
    "letter":
    {
        "2x2":
        {
            "name": "Letter-2x2",
            "description": '''8.5”×11” sheet, 5”×3.5” labels, 4 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (3.5, 5.0),
            "vertical_offsets": [0.5, 5.5],
            "horizontal_offsets": [0.5, 4.5],
        },
        "3x2":
        {
            "name": "Letter-3x2",
            "description": '''8.5”×11” sheet, 4”×3.333” labels, 6 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (4.0, 3.33333),
            "vertical_offsets": [0.5, 3.83333, 7.16667],
            "horizontal_offsets": [0.15625, 4.34375],
        },
        "4x2":
        {
            "name": "Letter-4x2",
            "description": '''8.5”×11” sheet, 4”×2.5” labels, 8 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (4.0, 2.5),
            "vertical_offsets": [0.5, 3.0, 5.5, 8.0],
            "horizontal_offsets": [0.15625, 4.34375],
        },
        "5x2":
        {
            "name": "Letter-5x2",
            "description": '''8.5”×11” sheet, 4”×2” labels, 10 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (4.0, 2.0),
            "vertical_offsets": [0.5, 2.5, 4.5, 6.5, 8.5],
            "horizontal_offsets": [0.15625, 4.34375],
        },
        "6x2":
        {
            "name": "Letter-6x2",
            "description": '''8.5”×11” sheet, 4”×1.5” labels, 12 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (4.0, 1.5),
            "vertical_offsets": [1.0, 2.5, 4.0, 5.5, 7.0, 8.5],
            "horizontal_offsets": [0.15625, 4.34375],
        },
        "7x2":
        {
            "name": "Letter-7x2",
            "description": '''8.5”×11” sheet, 4”×1.333” labels, 14 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (4.0, 1.33333),
            "vertical_offsets": [0.83333, 2.16667, 3.50000, 4.83333, 6.16667, 7.50000, 8.83333],
            "horizontal_offsets": [0.15625, 4.34375],
        },
        "5x3":
        {
            "name": "Letter-5x3",
            "description": '''8.5”×11” sheet, 2.625”×2” labels, 15 per sheet''',
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (2.625, 2.0),
            "vertical_offsets": [0.5, 2.5, 4.5, 6.5, 8.5],
            "horizontal_offsets": [0.15625, 2.90625, 5.65625],
        },
        "10x3":
        {
            "name": "Letter-10x3",
            "description": '''8.5”×11” sheet, 2.625”×1” labels, 30 per sheet''',
            "template numbers": [],
            "units": "inch",
            "pagesize": (8.5, 11.0),
            "labelsize": (2.625, 1.0),
            "vertical_offsets": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
            "horizontal_offsets": [0.15625, 2.90625, 5.65625],
        },
    }
} #}}}

class PDFLabels:

    def __init__(self, parts_list=None):
        self._hwitems = parts_list or []

        self._label_types = {
            "qr": [],
            "bar": [],
        }

        self._images = {
            "qr": {},
            "bar": {},
        }

    @property
    def hwitems(self):
        return self._hwitems

    @hwitems.setter
    def hwitems(self, value):
        assert(isinstance(value, (list, tuple)))
        self._hwitems = list(value)

    def _get_images(self):
        #{{{
        NUM_THREADS = 15
        save_session_kwargs = deepcopy(ra.session_kwargs)
        ra.session_kwargs["timeout"] = 16

        pool = mp.Pool(processes=NUM_THREADS) 


        for code_type in ('qr', 'bar'):
            
            if code_type == 'qr':
                fn = lambda args, kwargs: ra.get_hwitem_qrcode(*args, **kwargs)
            else:
                fn = lambda args, kwargs: ra.get_hwitem_barcode(*args, **kwargs)

            if self._label_types[code_type]:
                for part_id in self._hwitems:
                    res = pool.apply_async(fn, ((), {"part_id": part_id}))
                    self._images[code_type][part_id] = res
        pool.close()
        pool.join()

        for code_type in ('qr', 'bar'):
            for part_id in self._images[code_type]:
                self._images[code_type][part_id] = self._images[code_type][part_id].get().content
        
        ra.session_kwargs = save_session_kwargs
        #}}}    

    def use_default_label_types(self):
        default_label_types = [
            ('qr', '2x2', 'letter'),
            ('qr', '3x2', 'letter'),
            ('qr', '5x3', 'letter'),
            ('bar', '4x2', 'letter'),
            ('bar', '5x2', 'letter'),
            ('bar', '6x2', 'letter'),
            ('bar', '7x2', 'letter'),
            ('bar', '10x3', 'letter'),
        ]

        for args in default_label_types:
            self.add_label_type(*args)

    def add_label_type(self, code_type, template, page_size="letter"): 
        #{{{
        code_type = code_type.casefold()
        assert(code_type in ('qr', 'bar'))
        assert(page_size.casefold() in ('a4', 'letter'))
        page_size = {
            'a4': 'A4',
            'letter': 'letter',
        }[page_size.casefold()]

        if template in label_templates[page_size]:
            self._label_types[code_type].append(
                    label_templates[page_size][template])
        else:
            raise ValueError(f"Template ({page_size}, {template}) not defined")
        #}}}

    def generate_label_sheets(self, filename):
        #{{{
        if not _reportlab_available:
            print("Label generation unavailable. To enable label generation, install reportlab.\n"
                "Try: 'pip install reportlab'")
            return

        self._get_images()

        cvs = canvas.Canvas(filename)
        cvs.setTitle("HWDB Item Bar/QR Code Labels")
        cvs.setAuthor(f"HWDB Python Utility {Sisyphus.version}")

        def intro_page(cvs, code_type, template):
            #{{{
            unit = {
                'mm': units.mm,
                'cm': units.cm,
                'pica': units.pica,
                'inch': units.inch,
            }[template['units']]

            page_width, page_height = [unit * x for x in template["pagesize"]]
            cvs.setPageSize( (page_width, page_height) )
            
            num_rows = len(template["vertical_offsets"])
            num_cols = len(template["horizontal_offsets"])
            items_per_page = num_rows * num_cols
            full_pages, leftovers = divmod(len(self._hwitems), items_per_page)
            num_pages = full_pages + (1 if leftovers else 0)
            margin = 0.5 * units.inch 


            logo_path = Sisyphus.get_path("resources/images/DUNE-logo.png")

            logo_pil = PIL.Image.open(logo_path)
            aspect_ratio = logo_pil.size[0]/logo_pil.size[1]
            image_width = page_width - 2 * margin
            image_height = image_width / aspect_ratio

            cvs.drawImage(
                    Sisyphus.get_path("resources/images/DUNE-logo.png"),
                    margin,
                    page_height - margin - image_height,
                    image_width,
                    image_height,
                    mask=[0, 0, 0, 0, 0, 0])

            cvs.setFont("Helvetica-Bold", 26)
            cvs.setFillColorRGB(0.486, 0.682, 0.835)
            cvs.setStrokeColorRGB(0.0, 0.0, 0.0)
            
            code_type_name = {
                'qr': 'QR',
                'bar': 'Bar'
            }[code_type]

            cvs.drawString(
                    margin, 
                    page_height - margin - 1.75 * units.inch,
                    f"Hardware Item {code_type_name} Code Labels")

            cvs.setFont("Helvetica", 14)
            cvs.drawString(
                    margin,
                    page_height - margin - 2.25 * units.inch,
                    f"Label Template: {template['description']}")

            template_page = cvs.getPageNumber() + 1

            text_object = cvs.beginText()
            text_object.setTextOrigin(
                        margin, 
                        page_height - margin - 3.25 * units.inch)
            text_object.setFillColorRGB(0.949, 0.408, 0.169)
            text_object.textLine(f"Print template on page {template_page} on normal "
                    "paper and check alignment with your label")
            text_object.textLine("sheet. You may need to disable "
                    "\"fit to page\" or adjust other settings to achieve")
            text_object.textLine("proper alignment.")

            
            first_page = template_page + 1
            last_page = first_page + num_pages - 1
            if first_page == last_page:
                text = f"Insert label sheet and print page {first_page} from this document."
            else:
                text = (f"Insert label sheet and print pages {first_page}-{last_page} "
                            "from this document.")

            text_object.textLine("")
            text_object.setFillColorRGB(0.486, 0.682, 0.835)
            text_object.textLine(text)
    
            cvs.drawText(text_object)

            cvs.showPage()

            add_labels(cvs, code_type, template, outlines_only=True)

            #}}}


        def add_labels(cvs, code_type, template, outlines_only=False):
            #{{{

            template = deepcopy(template)
            
            unit = {
                'mm': units.mm,
                'cm': units.cm,
                'pica': units.pica,
                'inch': units.inch,
            }[template['units']]

            # Set the page size BEFORE deciding whether to rotate, because
            # if we rotate, we'll rotate into the correct footprint
            cvs.setPageSize( tuple(unit * d for d in template["pagesize"]) )                    

            #cvs.setStrokeColorRGB(0.80, 0.40, 0.40)
            #cvs.roundRect(
            #        0.0,
            #        0.0,
            #        unit * template["pagesize"][0], 
            #        unit * template["pagesize"][1], 
            #        unit * 5/32, 
            #        fill=0)
            
            labels_are_sideways = (template["labelsize"][1] > template["labelsize"][0])

            rotate = ( (code_type == "qr" and not labels_are_sideways)
                    or (code_type == "bar" and labels_are_sideways))
            #rotate = False

            if rotate:
                # swap the label dimensions
                labelwidth, labelheight = template["labelsize"]
                template["labelsize"] = labelheight, labelwidth
                
                # swap the offsets
                v_off, h_off = template["vertical_offsets"], template["horizontal_offsets"]
                template["horizontal_offsets"], template["vertical_offsets"] = v_off, h_off
                
                # swap the page dimensions
                # (even though the page dimensions have already been set,
                # these are still used for offset calculations)
                pw, ph = template["pagesize"]
                template["pagesize"] = ph, pw

            
            width, height = template["labelsize"]

            page_width, page_height = template["pagesize"]
            
            if code_type == 'qr':
                image_vert_alloc = 0.90
                caption_vert_alloc = 0.20 # there is some overlap
                font_scale = 0.08 # relative to the image height
            else:
                image_vert_alloc = 1.0
                caption_vert_alloc = 0.0
                font_scale = 0.0
            
            num_rows = len(template["vertical_offsets"])
            num_cols = len(template["horizontal_offsets"])
            items_per_page = num_rows * num_cols
            full_pages, leftovers = divmod(len(self._hwitems), items_per_page)
            num_pages = full_pages + (1 if leftovers else 0)


            for page in range(num_pages):
                if outlines_only and page > 0:
                    break
                if rotate:
                    cvs.translate(unit * pw, 0.0)
                    cvs.rotate(90)

                for row, row_offset in enumerate(template["vertical_offsets"]):
                    for col, col_offset in enumerate(template["horizontal_offsets"]):
                        label_num = page * num_rows * num_cols + row * num_cols + col
                        y_offset = page_height - row_offset - height
                        x_offset = col_offset
                  
                        ### Uncomment this if you want a background color
                        ### drawn so you can see the image boundaries 
                        #cvs.setStrokeColorRGB(0.80, 0.80, 0.80)
                        #cvs.setFillColorRGB(0.90, 0.90, 0.90)
                        #cvs.roundRect(
                        #        unit * x_offset, 
                        #        unit * y_offset, 
                        #        unit * width, 
                        #        unit * height, 
                        #        unit * 5/32, 
                        #        fill=1)
                        
                        if label_num < len(self._hwitems) and not outlines_only: 

                            part_id = self._hwitems[label_num]

                            image_bytes = self._images[code_type][part_id]
                            image_pil = PIL.Image.open(io.BytesIO(image_bytes))
                            aspect_ratio = image_pil.size[0]/image_pil.size[1]

                            alloc_height = height
                            alloc_width = height * aspect_ratio * image_vert_alloc

                            if alloc_width > width:
                                alloc_width = width
                                alloc_height = width / (aspect_ratio * image_vert_alloc)

                            image_height = alloc_height * image_vert_alloc
                            image_width = alloc_width

                            image_h_offset = 0.5 * (width - image_width)
                            image_v_offset = 0.5 * (height - alloc_height)
                            caption_height = alloc_height * caption_vert_alloc
                            font_size = image_height * font_scale

                            ### Canvas.DrawImage() appears to be broken and 
                            ### does not accept a PIL image or a bytes object
                            ### as advertised, so to get around it, we will
                            ### write it to a temporary file and use the file
                            ### name instead.
                            with tempfile.NamedTemporaryFile() as tf:
                                tf.write(image_bytes)
                                tf.seek(0)                        
                                #cvs.drawImage(tf.name,
                                #        unit * (x_offset+image_h_offset),
                                #        unit * (y_offset+image_v_offset),
                                #        unit * image_width,
                                #        unit * image_height)
                                cvs.drawImage(tf.name,
                                        unit * (x_offset + image_h_offset),
                                        unit * (y_offset + image_v_offset 
                                                + (alloc_height - image_height)),
                                        unit * image_width,
                                        unit * image_height)

                            if code_type == 'qr':
                                # Add a caption
                                cvs.setFont("Helvetica-Bold", unit * font_size)
                                cvs.setFillColorRGB(0.0, 0.0, 0.0)
                                cvs.setStrokeColorRGB(0.0, 0.0, 0.0)
                                #cvs.drawCentredString(
                                #    unit * (x_offset + 0.5 * width),
                                #    unit * (y_offset + image_v_offset 
                                #            - caption_vert_alloc * alloc_height),
                                #    part_id)
                                cvs.drawCentredString(
                                    unit * (x_offset + 0.5 * width),
                                    unit * (y_offset + image_v_offset 
                                            + 0.5 * (caption_height - font_size)),
                                    part_id)

                            elif code_type == 'bar':
                                ...



                        # Draw the outline
                        if outlines_only:
                            cvs.setStrokeColorRGB(0.80, 0.80, 0.80)
                            cvs.roundRect(
                                    unit * x_offset, 
                                    unit * y_offset, 
                                    unit * width, 
                                    unit * height, 
                                    unit * 5/32, 
                                    fill=0)

                cvs.showPage()
            #}}}


        for code_type in ('bar', 'qr'):
            for template in self._label_types[code_type]:
                intro_page(cvs, code_type, template)
                add_labels(cvs, code_type, template)

        cvs.save()
        #}}}
    
