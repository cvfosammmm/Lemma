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
from gi.repository import GLib, Gdk

import urllib.parse, os, os.path, shutil

import lemma.widgets.base as base
from lemma.services.text_shaper import TextShaper
from lemma.services.files import Files


class Widget(base.Widget):

    def __init__(self, attributes):
        match attributes:
            case {'filename': filename}:
                base.Widget.__init__(self, 'attachment', False, {'filename': filename})
            case _:
                raise Exception

    def to_html(self, data_folder):
        path_origin = os.path.join(Files.get_documents_folder(), self.attributes['filename'])
        path_dest = os.path.join(data_folder, os.path.basename(self.attributes['filename']))

        if not os.path.exists(data_folder): os.makedirs(data_folder)
        shutil.copyfile(path_origin, path_dest)

        return '<a href="' + urllib.parse.quote(os.path.split(data_folder)[-1] + '/' + os.path.basename(self.attributes['filename'])) + '">' + os.path.basename(self.attributes['filename']) + '</a>'

    def get_clipboard_content_provider(self):
        filename = Files.abspath_for_document_file(self.attributes['filename'])

        return Gdk.ContentProvider.new_for_bytes('text/uri-list', GLib.Bytes(('file://' + filename).encode()))

    def get_filenames(self):
        return {self.attributes['filename']}

    def change_filename(self, name_from, name_to):
        if self.attributes['filename'] == name_from:
            self.attributes['filename'] = name_to

    def get_allocation(self, fontname):
        dimensions = TextShaper.measure(os.path.basename(self.attributes['filename']), fontname)

        return (sum(metric[0] for metric in dimensions), max(metric[1] for metric in dimensions))


