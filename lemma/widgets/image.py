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

import io, cairo, urllib.parse, os, os.path, shutil
from PIL import Image as PIL_Image

import lemma.widgets.base as base
from lemma.services.files import Files


class Widget(base.Widget):

    def __init__(self, attributes):
        match attributes:
            case {'filename': filename, 'width': width}:
                base.Widget.__init__(self, 'image', True, {'filename': filename, 'width': int(float(width))})
            case {'filename': filename}:
                base.Widget.__init__(self, 'image', True, {'filename': filename})
            case _:
                raise Exception

        filename = Files.abspath_for_document_file(self.attributes['filename'])
        with PIL_Image.open(filename) as pil_image:
            self.cache['original_width'] = pil_image.width
            self.cache['original_height'] = pil_image.height
            self.cache['image_format'] = pil_image.format

            if 'A' not in pil_image.getbands():
                pil_image.putalpha(256)
            img_bytes = bytearray(pil_image.tobytes('raw', 'BGRa'))
            self.cache['cairo_surface'] = cairo.ImageSurface.create_for_data(img_bytes, cairo.FORMAT_ARGB32, self.cache['original_width'], self.cache['original_height'])

    def to_html(self, data_folder):
        path_origin = os.path.join(Files.get_documents_folder(), self.attributes['filename'])
        path_dest = os.path.join(data_folder, os.path.basename(self.attributes['filename']))

        if not os.path.exists(data_folder): os.makedirs(data_folder)
        shutil.copyfile(path_origin, path_dest)

        return '<img src="' + urllib.parse.quote(os.path.split(data_folder)[-1] + '/' + os.path.basename(self.attributes['filename'])) + '" width="' + str(self.get_size()[0]) + '" />'

    def get_clipboard_content_provider(self):
        filename = Files.abspath_for_document_file(self.attributes['filename'])
        texture = Gdk.Texture.new_from_filename(filename)
        data = texture.save_to_png_bytes().unref_to_data()

        return Gdk.ContentProvider.new_for_bytes('image/png', GLib.Bytes(data))

    def get_filenames(self):
        return {self.attributes['filename']}

    def change_filename(self, name_from, name_to):
        if self.attributes['filename'] == name_from:
            self.attributes['filename'] = name_to


