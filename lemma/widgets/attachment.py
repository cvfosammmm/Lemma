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
import os.path, shutil

from lemma.services.files import Files
from lemma.services.text_shaper import TextShaper
from lemma.services.text_renderer import TextRenderer
from lemma.services.color_manager import ColorManager


class Attachment(object):

    def __init__(self, filename):
        self.allocation = (0, 0)

        self.filename = filename
        self.dimensions = []

    def get_type(self):
        return 'attachment'

    def get_filenames(self):
        return {self.filename}

    def change_filename(self, name_from, name_to):
        if self.filename == name_from:
            self.filename = name_to

    def allocate_size(self, fontname):
        self.dimensions = TextShaper.measure(os.path.basename(self.filename), fontname)
        self.allocation = (sum(metric[0] for metric in self.dimensions), max(metric[1] for metric in self.dimensions))

    def get_allocation(self):
        return self.allocation

    def draw(self, ctx, offset_x, offset_y, hidpi_factor, fontname):
        baseline = TextShaper.get_ascend(fontname) + TextShaper.get_descend(fontname)
        fg_color = ColorManager.get_ui_color_string('links')

        for char, dims in zip(os.path.basename(self.filename), self.dimensions):
            surface, left, top = TextRenderer.get_glyph(char, fontname, fg_color, hidpi_factor)
            if surface != None:
                ctx.set_source_surface(surface, int((offset_x) * hidpi_factor + left), int((offset_y + baseline) * hidpi_factor + top))
                ctx.paint()
            offset_x += dims[0]

    def get_cursor_name(self):
        return 'pointer'

    def on_primary_button_press(self, n_press, x, y):
        if n_press == 2:
            Files.open(self.filename)

    def is_resizable(self):
        return False

    def to_xml(self):
        return '<widget type="attachment" filename="' + self.filename + '" />'

    def to_html(self, data_folder_dest):
        path_origin = os.path.join(Files.get_notes_folder(), self.filename)
        path_dest = os.path.join(data_folder_dest, os.path.basename(self.filename))

        if not os.path.exists(data_folder_dest): os.makedirs(data_folder_dest)
        shutil.copyfile(path_origin, path_dest)

        return '<a href="' + urllib.parse.quote(os.path.split(data_folder_dest)[-1] + '/' + os.path.basename(self.filename)) + '">' + os.path.basename(self.filename) + '</a>'


