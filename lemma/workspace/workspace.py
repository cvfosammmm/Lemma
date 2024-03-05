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

import os.path
import time
import pickle

from lemma.helpers.observable import Observable
from lemma.document_list.document_list import DocumentList
from lemma.document_history.document_history import DocumentHistory
from lemma.app.service_locator import ServiceLocator


class Workspace(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.active_document = None
        self.mode = 'documents'

        self.documents = DocumentList(self)
        self.history = DocumentHistory(self)

        self.settings = ServiceLocator.get_settings()
        self.settings.connect('settings_changed', self.on_settings_changed)
        self.theme = self.settings.get_value('preferences', 'color_scheme')

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'color_scheme':
            self.theme = value
            self.add_change_code('theme_change')

    def get_active_document(self):
        return self.active_document

    def enter_draft_mode(self):
        self.mode = 'draft'
        self.add_change_code('mode_set')

        self.history.activate_document(None)
        self.documents.update()

    def leave_draft_mode(self):
        self.mode = 'documents'
        self.add_change_code('mode_set')

        self.history.activate_document(self.active_document)
        self.documents.update()

    def set_active_document(self, document, update_history=True):
        self.mode = 'documents'
        self.add_change_code('mode_set')

        self.active_document = document
        self.documents.update()

        if update_history and document != None:
            self.history.add(document)
        self.history.activate_document(document)
        self.add_change_code('new_active_document', document)

    def delete_document(self, document):
        if document == None: return
        if document == self.active_document:
            self.set_active_document(self.history.get_next_in_line(document))

        self.history.delete(document)
        self.documents.delete(document)


