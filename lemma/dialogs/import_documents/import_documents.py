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
from gi.repository import Gtk

import os.path, pickle, re

import lemma.dialogs.import_documents.import_documents_viewgtk as view
from lemma.ast.node import *
from lemma.document.document import Document
from lemma.app.service_locator import ServiceLocator


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

        dialog.open_multiple(self.main_window, None, self.add_file_dialog_process_response)

    def add_file_dialog_process_response(self, dialog, result):
        try:
            files = dialog.open_multiple_finish(result)
        except Exception: pass
        else:
            if files != None:
                for file in files:
                    self.add_file_to_list(file.get_path())
                self.view.list.invalidate_sort()

    def on_drop(self, controller, files, x, y):
        for file in files:
            path = file.get_path()
            if not os.path.isdir(path) and path.endswith('.md'):
                self.add_file_to_list(path)
        self.view.list.invalidate_sort()

    def add_file_to_list(self, path):
        if path not in self.current_values['files']:
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
            document.last_modified = os.path.getmtime(path)

            document.title = os.path.basename(path[:-3])
            if self.workspace.documents.get_by_title(document.title):
                match = re.match(r'.*\(([1-9]+)\)', document.title)
                if match != None:
                    document.title = document.title[:-(len(match.group(1)) + 2)]

                number = 1
                new_title = document.title + '(' + str(number) + ')'
                while self.workspace.documents.get_by_title(new_title):
                    number += 1
                    new_title = document.title + '(' + str(number) + ')'
                document.title = new_title

            with open(path, 'r') as file:
                lines = file.readlines()
                if len(lines) == 0: return
                if lines[0].startswith('# '):
                    del(lines[0])
                if len(lines) == 0: return

                document_lines = Lines()
                for line in lines:
                    document_line = Line()
                    for char in line[:-1]:
                        document_line.append(UnicodeCharacter(char))
                    document_lines.append(document_line)

            document.lines = document_lines
            document.insert.set_position([0, 0])
            document.update_visitors()

            self.workspace.documents.add(document)


