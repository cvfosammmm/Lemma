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
from gi.repository import Gtk, GLib, Gio

import os.path, pickle, re

import lemma.dialogs.import_documents.import_documents_viewgtk as view
from lemma.ast.node import *
from lemma.document.document import Document
from lemma.app.service_locator import ServiceLocator
import lemma.commands.commands as commands


class ImportDocuments(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.workspace = None
        self.current_values = dict()

    def run(self, workspace):
        self.workspace = workspace

        self.init_current_values()
        self.view = view.ImportDocumentsView(self.main_window)
        self.setup()
        self.view.present()

    def init_current_values(self):
        self.current_values['files'] = set()

    def setup(self):
        self.view.import_button.set_sensitive(False)
        self.view.drop_stack.set_visible_child_name('message')

        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.import_button.connect('clicked', self.on_import_button_clicked)
        self.view.add_file_button.connect('clicked', self.on_add_file_button_clicked)
        self.view.drop_controller.connect('drop', self.on_drop)

    def on_cancel_button_clicked(self, button):
        self.view.close()

    def on_import_button_clicked(self, button):
        self.import_files()
        self.view.close()

    def on_add_file_button_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_modal(True)
        dialog.set_title(_('Add Files'))

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern('*.md')
        file_filter.set_name(_('Markdown Files'))
        dialog.set_default_filter(file_filter)

        import_folder = ServiceLocator.get_settings().get_value('app_state', 'last_import_folder')
        if import_folder == None or not os.path.exists(import_folder) or not os.path.isdir(import_folder):
            import_folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if import_folder != None:
            dialog.set_initial_folder(Gio.File.new_for_path(import_folder))

        dialog.open_multiple(self.main_window, None, self.add_file_dialog_process_response)

    def add_file_dialog_process_response(self, dialog, result):
        try:
            files = dialog.open_multiple_finish(result)
        except Exception: pass
        else:
            if files != None and len(files) > 0:
                import_folder = os.path.dirname(files[0].get_path())
                ServiceLocator.get_settings().set_value('app_state', 'last_import_folder', import_folder)
                for file in files:
                    self.add_file_to_list(file.get_path())
                self.view.list.invalidate_sort()

    def on_drop(self, controller, files, x, y):
        for file in files:
            self.add_file_to_list(file.get_path())
        self.view.list.invalidate_sort()

    def add_file_to_list(self, path):
        if not os.path.isdir(path) and path.endswith('.md') and path not in self.current_values['files']:
            self.current_values['files'].add(path)
            row = view.Row(path)
            row.button.connect('clicked', self.remove_file_from_list)
            self.view.list.append(row)

        self.view.import_button.set_sensitive(True)
        self.view.drop_stack.set_visible_child_name('files')

    def remove_file_from_list(self, button):
        row = button.get_parent().get_parent()
        self.view.list.remove(row)
        self.current_values['files'].remove(row.path)

        self.view.import_button.set_sensitive(len(self.current_values['files']) > 0)
        self.view.drop_stack.set_visible_child_name(('files' if len(self.current_values['files']) > 0 else 'message'))

    def import_files(self):
        for path in self.current_values['files']:
            document = Document(self.workspace, self.workspace.documents.get_new_document_id())
            document.command_processor.add_command(commands.PopulateFromPath(path))
            document.command_processor.reset_undo_stack()
            self.workspace.documents.add(document)


