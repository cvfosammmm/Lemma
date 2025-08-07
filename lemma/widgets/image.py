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

import os.path
from PIL import Image as PIL_Image
import cairo

from lemma.services.layout_info import LayoutInfo
from lemma.services.file_format_db import FileFormatDB


class Image(object):

    def __init__(self, filename, width=None):
        self.pil_image = PIL_Image.open(filename)
        self.cairo_surface = None

        if width != None:
            self.set_width(width)
        else:
            self.set_width(min(self.pil_image.width, LayoutInfo.get_layout_width()))

    def set_width(self, width):
        height = int((width / self.pil_image.width) * self.pil_image.height)
        img = self.pil_image.resize((width, height))
        if 'A' not in img.getbands():
            img.putalpha(256)
        img_bytes = bytearray(img.tobytes('raw', 'BGRa'))
        self.cairo_surface = cairo.ImageSurface.create_for_data(img_bytes, cairo.FORMAT_ARGB32, img.width, img.height)

    def get_width(self):
        return self.cairo_surface.get_width()

    def get_minimum_width(self):
        return LayoutInfo.get_min_image_size()

    def get_height(self):
        return self.cairo_surface.get_height()

    def get_original_width(self):
        return self.pil_image.width

    def get_original_height(self):
        return self.pil_image.height

    def get_format(self):
        return self.pil_image.format

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

    def to_html(self, data_location_prefix):
        file_ending = FileFormatDB.get_ending_from_format_name(self.pil_image.format)
        filename = data_location_prefix + file_ending
        self.pil_image.save(filename)
        return '<img src="' + filename + '" width="' + str(self.get_width()) + '" />'

    # make this pickle
    def __getstate__(self):
        return {'pil_image': self.pil_image, 'width': self.get_width()}

    def __setstate__(self, state):
        self.pil_image = state['pil_image']
        self.set_width(state['width'])


