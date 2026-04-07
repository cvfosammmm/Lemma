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

from lemma.services.text_shaper import TextShaper
from lemma.services.layout_info import LayoutInfo


class Widget(object):

    def __init__(self, type_str, is_resizable, attributes):
        self.type = type_str
        self.is_resizable = is_resizable
        self.attributes = attributes

        self.cache = dict()

    def get_type(self):
        return self.type

    def get_attribute(self, key):
        if key not in self.attributes:
            return None

        return self.attributes[key]

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def to_xml(self):
        attributes = ' type="' + self.type + '"'
        for key, value in self.attributes.items():
            attributes += ' ' + key + '="' + str(value) + '"'
        return '<widget' + attributes + '></widget>'

    def to_html(self, data_folder):
        return ''

    def get_size(self):
        if self.is_resizable:
            if self.get_attribute('width') != None:
                width = self.get_attribute('width')
            else:
                width = min(self.cache['original_width'], LayoutInfo.get_max_layout_width())
            if self.get_attribute('height') != None:
                height = self.get_attribute('height')
            else:
                height = int((width / self.cache['original_width']) * self.cache['original_height'])
            return (width, height)

        return (None, None)

    def get_allocation(self, fontname):
        if self.is_resizable:
            width, height = self.get_size()
            return (width, height - 2 * TextShaper.get_descend(fontname))

        return (0, 0)

    def get_clipboard_content_provider(self):
        return None

    def get_filenames(self):
        return set()

    def change_filename(self, name_from, name_to):
        pass


