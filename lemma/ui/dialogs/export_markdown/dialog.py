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
from gi.repository import Gtk, Gio, GLib

import os.path, shutil, os
import urllib.parse
import html2text

from lemma.infrastructure.service_locator import ServiceLocator


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.document = None
        self.current_tags = set()
        self.current_link = None

    def run(self, document):
        self.document = document
        self.setup()
        self.view.save(self.main_window, None, self.dialog_process_response)

    def setup(self):
        self.view = Gtk.FileDialog()
        self.view.set_modal(True)
        self.view.set_title(_('Export Document'))

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern('*.md')
        file_filter.set_name(_('Markdown Files'))
        self.view.set_default_filter(file_filter)

        export_folder = ServiceLocator.get_settings().get_value('app_state', 'last_export_folder')
        if export_folder == None or not os.path.exists(export_folder) or not os.path.isdir(export_folder):
            export_folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if export_folder != None:
            self.view.set_initial_folder(Gio.File.new_for_path(export_folder))

        self.view.set_initial_name(self.document.title + '.md')

    def dialog_process_response(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except Exception: pass
        else:
            if file != None:
                filename = file.get_path()
                ServiceLocator.get_settings().set_value('app_state', 'last_export_folder', os.path.dirname(filename))

                if not filename.endswith('.md'):
                    filename += '.md'

                markdown = '# ' + self.document.title + '\n'
                markdown += html2text.html2text(self.document.html)

                with open(filename, 'w') as f:
                    f.write(markdown)

                data_dir = ServiceLocator.get_notes_folder()
                for file in [file for file in os.listdir(data_dir) if file.startswith(str(self.document.id) + '-')]:
                    shutil.copy(os.path.join(data_dir, file), os.path.dirname(filename))


