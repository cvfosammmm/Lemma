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
import math

from lemma.services.layout_info import LayoutInfo
from lemma.services.file_format_db import FileFormatDB
import lemma.services.timer as timer


class Image(object):

    @timer.timer
    def __init__(self, data, attributes=dict()):
        self.data = data.read()
        self.width = None
        self.height = None

        with PIL_Image.open(data) as pil_image:
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
            self.set_width(min(self.original_width, LayoutInfo.get_layout_width()))

    def set_width(self, width):
        self.width = width
        self.height = int((width / self.original_width) * self.original_height)

    def get_width(self):
        return self.width

    def get_minimum_width(self):
        return LayoutInfo.get_min_image_size()

    def get_height(self):
        return self.height

    def get_original_width(self):
        return self.original_width

    def get_original_height(self):
        return self.original_height

    def get_format(self):
        return self.format

    def get_cairo_surface(self):
        return self.cairo_surface

    def get_cursor_name(self):
        return 'default'

    def get_status_text(self):
        size_string = str(self.get_width()) + ' × ' + str(self.get_height())
        return self.get_format() + _(' Image') + ' (' + size_string + ')'

    def get_longest_possible_status_text(self):
        max_width = LayoutInfo.get_layout_width()
        max_height = int((max_width / self.get_original_width()) * self.get_original_height())
        max_digits = len(str(max_width)) + len(str(max_height))
        return self.get_format() + _(' Image') + ' ( × ' + max_digits * '0' + ')'

    def is_resizable(self):
        return True

    def get_data(self):
        return self.data

    def get_attributes(self):
        return {'type': 'image', 'width': str(self.get_width())}

    def to_html(self, data_location_prefix):
        with PIL_Image.open(io.BytesIO(self.data)) as pil_image:
            file_ending = FileFormatDB.get_ending_from_format_name(pil_image.format)
            filename = data_location_prefix + file_ending
            pil_image.save(filename)
        return '<img src="' + urllib.parse.quote(os.path.split(os.path.dirname(filename))[1] + '/' + os.path.basename(filename)) + '" width="' + str(self.get_width()) + '" />'


