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

from lemma.infrastructure.layout_info import LayoutInfo
from lemma.db.file_format_db import FileFormatDB


class Image(object):

    def __init__(self, filename, width=None):
        self.pil_image = PIL_Image.open(filename)
        self.pil_image_display = self.pil_image

        if width != None:
            self.set_width(min(self.pil_image.width, width))
        else:
            self.set_width(min(self.pil_image.width, LayoutInfo.get_layout_width()))

    def set_width(self, width):
        height = int((width / self.pil_image.width) * self.pil_image.height)
        self.pil_image_display = self.pil_image.resize((width, height))

    def get_width(self):
        return self.pil_image_display.width

    def get_height(self):
        return self.pil_image_display.height

    def get_original_width(self):
        return self.pil_image.width

    def get_original_height(self):
        return self.pil_image.height

    def get_format(self):
        return self.pil_image.format

    def get_file_ending(self):
        return FileFormatDB.get_ending_from_format_name(self.pil_image.format)

    def get_cairo_surface(self):
        pil_img = self.pil_image_display
        pil_img.putalpha(256)
        im_bytes = bytearray(pil_img.tobytes('raw', 'BGRa'))
        return cairo.ImageSurface.create_for_data(im_bytes, cairo.FORMAT_ARGB32, pil_img.width, pil_img.height)

    def save_as(self, filename):
        self.pil_image.save(filename)


