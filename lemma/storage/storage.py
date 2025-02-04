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
from lemma.document_repo.document_repo import DocumentRepo
import lemma.infrastructure.timer as timer


class Storage(object):

    def __init__(self, workspace):
        self.workspace = workspace

        self.pathname = ServiceLocator.get_notes_folder()
        if not os.path.exists(self.pathname):
            os.mkdir(self.pathname)

    def populate_workspace(self):
        pathname = os.path.join(self.pathname, 'workspace')
        if not os.path.isfile(pathname): return

        with open(pathname, 'rb') as file:
            data = pickle.loads(file.read())

            self.workspace.active_document = DocumentRepo.get_by_id(data['active_document_id'])
            for document_id in data['history']:
                document = DocumentRepo.get_by_id(document_id)
                if document != None:
                    self.workspace.history.add(document, remove_tail_after_last_active=False)
                    if document == self.workspace.active_document:
                        self.workspace.history.activate_document(document)

    def init_writer(self):
        self.workspace.connect('history_changed', self.on_history_change)

    def on_history_change(self, history):
        self.save_workspace()

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


