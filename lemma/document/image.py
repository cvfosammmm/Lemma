#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import urllib.parse
import os.path, io
from PIL import Image as PIL_Image
import cairo

from lemma.services.layout_info import LayoutInfo
from lemma.services.files import Files
from lemma.services.text_shaper import TextShaper
import lemma.services.timer as timer


class Image(object):

    @timer.timer
    def __init__(self, data, attributes=dict()):
        self.attributes = attributes
        self.allocation = (0, 0)

        self.data = data
        self.width = None
        self.height = None

        with PIL_Image.open(io.BytesIO(data)) as pil_image:
            self.format = pil_image.format
            self.original_width = pil_image.width
            self.original_height = pil_image.height

            if 'A' not in pil_image.getbands():
                pil_image.putalpha(256)
            img_bytes = bytearray(pil_image.tobytes('raw', 'BGRa'))
            self.cairo_surface = cairo.ImageSurface.create_for_data(img_bytes, cairo.FORMAT_ARGB32, self.original_width, self.original_height)

        if 'width' in attributes:
            self.set_width(int(attributes['width']))
        else:
            self.set_width(min(self.original_width, LayoutInfo.get_max_layout_width()))

    def get_type(self):
        return 'image'

    def get_attribute(self, key):
        return self.attributes[key]

    def get_filenames(self):
        return set()

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def change_filename(self, name_from, name_to):
        pass

    def set_width(self, width):
        self.width = width
        self.height = int((self.width / self.original_width) * self.original_height)

    def allocate_size(self, fontname):
        self.allocation = (self.width, self.height - 2 * TextShaper.get_descend(fontname))

    def get_allocation(self):
        return self.allocation

    def to_xml(self):
        return '<widget type="image" width="' + str(self.width) + '"><![CDATA[' + str(self.data) + ']]></widget>'

    def to_html(self, data_folder_dest):
        with PIL_Image.open(io.BytesIO(self.data)) as pil_image:
            file_no = len(os.listdir(data_folder_dest))
            file_ending = Files.get_extension_from_image_format(pil_image.format)
            filename = os.path.join(data_folder_dest, str(file_no) + file_ending)
            pil_image.save(filename)
        return '<img src="' + urllib.parse.quote(os.path.split(os.path.dirname(filename))[-1] + '/' + os.path.basename(filename)) + '" width="' + str(self.width) + '" />'

    # image specific functions below

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_data(self):
        return self.data

    def get_original_width(self):
        return self.original_width


