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

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

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

    def get_filenames(self):
        return set()

    def change_filename(self, name_from, name_to):
        pass

    def set_width(self, width):
        self.width = width
        self.height = int((self.width / self.original_width) * self.original_height)

    def allocate_size(self, fontname):
        self.allocation = (self.width, self.height - 2 * TextShaper.get_descend(fontname))

    def get_allocation(self):
        return self.allocation

    def draw(self, ctx, offset_x, offset_y, hidpi_factor, fontname):
        matrix = ctx.get_matrix()
        scaling_factor_x = self.width * hidpi_factor / self.original_width
        scaling_factor_y = self.height * hidpi_factor / self.original_height
        ctx.scale(scaling_factor_x, scaling_factor_y)

        ctx.set_source_surface(self.cairo_surface, offset_x * hidpi_factor / scaling_factor_x, offset_y * hidpi_factor / scaling_factor_y)
        ctx.paint()

        ctx.set_matrix(matrix)

    def get_cursor_name(self):
        return 'default'

    def on_primary_button_press(self, n_press, x, y):
        pass

    def is_resizable(self):
        return True

    def has_toolbar(self):
        return True

    def update_toolbar(self, toolbar):
        toolbar.status_label.set_text(self.get_status_text())
        layout = Pango.Layout(toolbar.status_label.get_pango_context())
        layout.set_text(self.get_longest_possible_status_text())
        toolbar.status_label.set_size_request(layout.get_extents()[0].width / Pango.SCALE + 30, -1)

        toolbar.scale.set_range(self.get_minimum_width(), LayoutInfo.get_max_layout_width())

        toolbar.scale.set_value(self.get_width())
        toolbar.scale.clear_marks()

        orig_width = self.get_original_width()
        if orig_width > self.get_minimum_width() and orig_width < LayoutInfo.get_max_layout_width():
            toolbar.scale.add_mark(orig_width, Gtk.PositionType.TOP)

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

    def get_status_text(self):
        size_string = str(self.width) + ' × ' + str(self.height)
        return self.format + _(' Image') + ' (' + size_string + ')'

    def get_longest_possible_status_text(self):
        max_width = LayoutInfo.get_max_layout_width()
        max_height = int((max_width / self.original_width) * self.original_height)
        max_digits = len(str(max_width)) + len(str(max_height))
        return self.format + _(' Image') + ' ( × ' + max_digits * '0' + ')'

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_data(self):
        return self.data

    def get_minimum_width(self):
        return LayoutInfo.get_min_image_size()

    def get_original_width(self):
        return self.original_width


