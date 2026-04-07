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
from gi.repository import Gtk, Gdk, GLib, Gio

import os.path

from lemma.use_cases.use_cases import UseCases
from lemma.widgets.factory import WidgetFactory
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.files import Files
from lemma.services.settings import Settings


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.open_multiple(self.main_window, None, self.dialog_process_response)

    def setup(self):
        self.view = Gtk.FileDialog()
        self.view.set_modal(True)
        self.view.set_title(_('Attach File(s)'))

        folder_preset = Settings.get_value('last_file_import_folder')
        if folder_preset == None or not os.path.exists(folder_preset) or not os.path.isdir(folder_preset):
            folder_preset = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if folder_preset != None:
            self.view.set_initial_folder(Gio.File.new_for_path(folder_preset))

    def dialog_process_response(self, dialog, result):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if not document.insert_parent_is_root(): return

        try:
            files = dialog.open_multiple_finish(result)
        except Exception: pass
        else:
            for file in files:
                origin = file.get_path()
                filename = Files.add_file_to_doc_folder_with_distinct_name(document, origin)

                UseCases.settings_set_value('last_file_import_folder', os.path.dirname(origin))

                widget = WidgetFactory.make_widget('attachment', {'filename': filename})
                UseCases.add_widget(widget)


