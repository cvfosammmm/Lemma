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

from lemma.helpers.observable import Observable
import lemma.infrastructure.timer as timer


class DocumentHistory(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace

        self.documents = list()
        self.active_document = None
        self.active_document_index = None

    def add(self, document, remove_tail_after_last_active=True):
        if remove_tail_after_last_active and self.active_document_index != None:
            self.documents = self.documents[:self.active_document_index + 1]
        if document in self.documents:
            self.documents.remove(document)
        if len(self.documents) >= 100:
            self.documents = self.documents[-100:]
        self.documents.append(document)
        self.add_change_code('changed')

    def activate_document(self, document):
        if document != None and document in self.documents:
            self.active_document_index = self.documents.index(document)
            if self.active_document != None:
                self.active_document.disconnect('changed', self.on_document_change)
            self.active_document = document
            self.active_document.connect('changed', self.on_document_change)

        self.add_change_code('changed')
        self.add_change_code('active_document_changed')

    def delete(self, document):
        if document not in self.documents: return

        if self.documents.index(document) < self.active_document_index:
            self.active_document_index -= 1
        self.documents.remove(document)

        self.add_change_code('changed')
        self.add_change_code('active_document_changed')

    def get_next_in_line(self, document):
        if document not in self.documents: return None

        prev_doc = self.get_previous_if_any(document)
        if prev_doc != None: return prev_doc

        next_doc = self.get_next_if_any(document)
        if next_doc != None: return next_doc

        return None

    def get_previous_if_any(self, document):
        if document not in self.documents: return None

        index = self.documents.index(document)
        if index == 0: return None
        else: return self.documents[index - 1]

    def get_next_if_any(self, document):
        if document not in self.documents: return None

        index = self.documents.index(document)
        if index == (len(self.documents) - 1): return None
        else: return self.documents[index + 1]

    @timer.timer
    def on_document_change(self, document):
        self.add_change_code('changed')


