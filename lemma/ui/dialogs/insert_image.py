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
from gi.repository import Gtk, Gdk

from PIL import Image as PIL_Image

from lemma.use_cases.use_cases import UseCases
from lemma.widgets.image import Image
from lemma.repos.workspace_repo import WorkspaceRepo


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.open(self.main_window, None, self.dialog_process_response)

    def setup(self):
        self.view = Gtk.FileDialog()
        self.view.set_modal(True)
        self.view.set_title(_('Insert Image'))

        file_filter = Gtk.FileFilter()
        for extension, name in [(extension, name) for (extension, name) in PIL_Image.registered_extensions().items() if name in PIL_Image.OPEN]:
            file_filter.add_pattern('*' + extension)
        file_filter.set_name(_('Image Files'))
        self.view.set_default_filter(file_filter)

    def dialog_process_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
        except Exception: pass
        else:
            if file != None:
                document = WorkspaceRepo.get_workspace().get_active_document()
                if document.insert_parent_is_root():
                    filename = file.get_path()
                    texture = Gdk.Texture.new_from_filename(filename)
                    data = texture.save_to_png_bytes().unref_to_data()
                    image = Image(data)
                    UseCases.add_image(image)


