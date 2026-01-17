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
from gi.repository import GLib, Gio

import tempfile
import shutil
import html2text
import os.path, os

import lemma.ui.dialogs.export_bulk_view as view
from lemma.services.html_exporter import HTMLExporter
from lemma.services.settings import Settings
from lemma.services.paths import Paths
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_values = dict()

    def run(self):
        self.init_current_values()
        self.view = view.ExportBulkView(self.main_window)
        self.populate_view()
        self.observe_view()
        self.validate()
        self.view.present()

    def init_current_values(self):
        self.current_values['filename'] = None
        self.current_values['document_ids'] = set([doc_stub['id'] for doc_stub in DocumentRepo.list()])

    def populate_view(self):
        last_export_folder = Settings.get_value('last_bulk_export_folder')
        if last_export_folder == None or not os.path.exists(last_export_folder) or not os.path.isdir(last_export_folder):
            last_export_folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)
        if last_export_folder != None:
            self.view.file_chooser_button.dialog.set_initial_folder(Gio.File.new_for_path(last_export_folder))

        for doc_stub in DocumentRepo.list():
            row = view.Row(doc_stub['id'], doc_stub['title'])
            row.button.set_active(doc_stub['id'] in self.current_values['document_ids'])
            self.view.list.append(row)
        self.view.select_all_button.set_active(True)

    def observe_view(self):
        self.view.file_chooser_button.observe('file-set', self.on_file_chosen)

        for row in self.view.list:
            row.button.connect('toggled', self.on_document_button_toggled, row.document_id)
        self.view.select_all_button.connect('toggled', self.on_select_all_button_toggled)

        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.submit_button.connect('clicked', self.on_submit_button_clicked)

    def validate(self):
        is_valid = self.current_values['filename'] != None and len(self.current_values['document_ids']) > 0
        self.view.submit_button.set_sensitive(is_valid)

        if len(self.current_values['document_ids']) == len(DocumentRepo.list()):
            self.view.select_all_button.set_active(True)
        elif len(self.current_values['document_ids']) == 0:
            self.view.select_all_button.set_active(False)

    def on_document_button_toggled(self, button, document_id):
        if button.get_active():
            self.current_values['document_ids'].add(document_id)
        else:
            self.current_values['document_ids'].discard(document_id)
        self.validate()

    def on_select_all_button_toggled(self, button):
        is_active = button.get_active()
        for row in self.view.list:
            row.button.set_active(is_active)

    def on_checkbutton_toggled(self, button, name, value):
        if button.get_active():
            self.current_values[name] = value
        self.validate()

    def on_file_chosen(self, chooser_button):
        self.current_values['filename'] = chooser_button.get_filename()
        self.validate()

    def on_cancel_button_clicked(self, button):
        self.view.close()

    def on_submit_button_clicked(self, button):
        arch_filename = self.current_values['filename']
        UseCases.settings_set_value('last_bulk_export_folder', os.path.dirname(arch_filename))

        with tempfile.TemporaryDirectory() as temp_dir:
            for document_id in self.current_values['document_ids']:
                document = DocumentRepo.get_by_id(document_id)
                filename = os.path.join(temp_dir, str(document.id) + '.md')

                exporter = HTMLExporter()
                html = exporter.export_document(document, filename)

                html = html.replace('.html">', '.md">')
                markdown = html2text.html2text(html)

                with open(filename, 'w') as f:
                    f.write(markdown)

            shutil.make_archive(arch_filename[:-4], 'zip', temp_dir)

        self.view.close()


