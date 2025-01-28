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

import os, os.path, pickle

from lemma.document.document import Document
from lemma.infrastructure.html_exporter import HTMLExporter
from lemma.infrastructure.html_parser import HTMLParser
from lemma.infrastructure.service_locator import ServiceLocator


class Storage(object):

    def __init__(self, workspace):
        self.workspace = workspace

        self.pathname = ServiceLocator.get_notes_folder()
        if not os.path.exists(self.pathname):
            os.mkdir(self.pathname)

    def populate_documents(self):
        for direntry in os.scandir(self.pathname):
            if direntry.is_file() and direntry.name.isdigit():
                document = Document(int(direntry.name))
                document.last_modified = os.path.getmtime(direntry.path)

                with open(direntry.path, 'r') as file:
                    html = file.read()

                parser = HTMLParser(html, self.pathname)
                parser.run()
                document.title = parser.title
                document.ast = parser.composite
                document.cursor.set_state([document.ast[0].get_position(), document.ast[0].get_position()])
                document.set_scroll_insert_on_screen_after_layout_update()
                document.update()
                document.signal_changes()

                self.workspace.add(document)

    def populate_workspace(self):
        pathname = os.path.join(self.pathname, 'workspace')
        if not os.path.isfile(pathname): return

        with open(pathname, 'rb') as file:
            data = pickle.loads(file.read())

            self.workspace.active_document = self.workspace.get_by_id(data['active_document_id'])
            if self.workspace.active_document != None: self.workspace.active_document.connect('changed', self.workspace.on_document_change)

            for document_id in data['history']:
                document = self.workspace.get_by_id(document_id)
                if document != None:
                    self.workspace.history.add(document, remove_tail_after_last_active=False)
                    if document == self.workspace.active_document:
                        self.workspace.history.activate_document(document)
            self.workspace.history.add_change_code('active_document_changed')

    def init_writer(self):
        for document in self.workspace.documents:
            document.connect('changed', self.on_document_change)
        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('changed', self.on_workspace_changed)
        self.workspace.history.connect('changed', self.on_history_change)

    def on_workspace_changed(self, workspace):
        self.save_workspace()

    def on_history_change(self, history):
        self.save_workspace()

    def on_new_document(self, workspace, document):
        self.save_document(document)
        document.connect('changed', self.on_document_change)

    def on_document_removed(self, workspace, document):
        document.disconnect('changed', self.on_document_change)
        self.delete_document(document)

    def on_document_change(self, document):
        self.save_document(document)

    def save_document(self, document):
        pathname = os.path.join(self.pathname, str(document.id))
        exporter = HTMLExporter()
        html = exporter.export_html(document)

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(html)

    def delete_document(self, document):
        pathname = os.path.join(self.pathname, str(document.id))
        os.remove(pathname)

    def save_workspace(self):
        pathname = os.path.join(self.pathname, 'workspace')

        try: filehandle = open(pathname, 'wb')
        except IOError: pass
        else:
            if self.workspace.active_document != None:
                active_document_id = self.workspace.active_document.id
            else:
                active_document_id = None

            data = {'active_document_id': active_document_id,
                    'history': self.get_history_list()}
            filehandle.write(pickle.dumps(data))

    def get_history_list(self):
        history_list = []
        for i, document in enumerate(self.workspace.history.documents):
            if document != None:
                history_list.append(document.id)
        return history_list


