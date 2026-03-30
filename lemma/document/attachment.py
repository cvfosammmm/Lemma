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
from lemma.services.helpers import Helpers
from lemma.services.text_shaper import TextShaper
from lemma.services.text_renderer import TextRenderer
from lemma.services.color_manager import ColorManager


class Attachment(object):

    def __init__(self, filename):
        self.attributes = {'filename': filename}
        self.allocation = (0, 0)

    def get_type(self):
        return 'attachment'

    def get_attribute(self, key):
        return self.attributes[key]

    def get_filenames(self):
        return {self.attributes['filename']}

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def change_filename(self, name_from, name_to):
        if self.attributes['filename'] == name_from:
            self.attributes['filename'] = name_to

    def allocate_size(self, fontname):
        dimensions = TextShaper.measure(os.path.basename(self.attributes['filename']), fontname)
        self.allocation = (sum(metric[0] for metric in dimensions), max(metric[1] for metric in dimensions))

    def get_allocation(self):
        return self.allocation

    def to_xml(self):
        return '<widget type="attachment" filename="' + self.attributes['filename'] + '" />'

    def to_html(self, data_folder_dest):
        path_origin = os.path.join(Files.get_documents_folder(), self.attributes['filename'])
        path_dest = os.path.join(data_folder_dest, os.path.basename(self.attributes['filename']))

        if not os.path.exists(data_folder_dest): os.makedirs(data_folder_dest)
        shutil.copyfile(path_origin, path_dest)

        return '<a href="' + urllib.parse.quote(os.path.split(data_folder_dest)[-1] + '/' + os.path.basename(self.attributes['filename'])) + '">' + os.path.basename(self.attributes['filename']) + '</a>'


