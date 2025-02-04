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

import lemma.infrastructure.timer as timer


class DocumentHistory():

    def __init__(self, workspace):
        self.workspace = workspace

        self.documents = list()
        self.active_document_index = None

    def add(self, document, remove_tail_after_last_active=True):
        if remove_tail_after_last_active and self.active_document_index != None:
            self.documents = self.documents[:self.active_document_index + 1]
        if document in self.documents:
            self.documents.remove(document)
        if len(self.documents) >= 100:
            self.documents = self.documents[-100:]
        self.documents.append(document)

    def activate_document(self, document):
        if document != None and document in self.documents:
            self.active_document_index = self.documents.index(document)

    def delete(self, document):
        if document not in self.documents: return

        if self.documents.index(document) < self.active_document_index:
            self.active_document_index -= 1
        self.documents.remove(document)

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


