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

from operator import attrgetter

from lemma.helpers.observable import Observable
from lemma.document_list.document_list_view import DocumentListView
from lemma.document_list.document_list_presenter import DocumentListPresenter
from lemma.document_list.document_list_controller import DocumentListController
from lemma.document_list.context_menu.context_menu import ContextMenu


class DocumentList(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace

        self.max_document_id = 0
        self.documents = list()
        self.documents_by_id = dict()
        self.active_document = None

        self.width = 0
        self.height = 0
        self.selected_index = None

        self.view = DocumentListView()
        self.presenter = DocumentListPresenter(self, self.view)
        self.controller = DocumentListController(self, self.view)
        self.context_menu = ContextMenu(self)

    def add(self, document):
        self.max_document_id = max(self.max_document_id, document.id)
        self.documents.append(document)
        self.documents.sort(key=attrgetter('last_modified'), reverse=True)
        self.documents_by_id[document.id] = document
        self.add_change_code('new_document', document)
        self.add_change_code('changed')

    def delete(self, document):
        self.documents.remove(document)
        self.add_change_code('document_removed', document)
        self.add_change_code('changed')

    def update(self):
        if self.workspace.active_document != None:
            if self.active_document != None:
                self.active_document.disconnect('changed', self.on_document_change)
            self.active_document = self.workspace.active_document
            self.active_document.connect('changed', self.on_document_change)
        self.add_change_code('changed')

    def on_document_change(self, document):
        self.documents.sort(key=attrgetter('last_modified'), reverse=True)
        self.add_change_code('changed')

    def get_by_title(self, title):
        for document in self.documents:
            if title == document.title:
                return document

    def get_by_id(self, id):
        if id not in self.documents_by_id: return None
        return self.documents_by_id[id]

    def count(self):
        return len(self.documents)

    def get_new_document_id(self):
        return self.max_document_id + 1

    def set_selected_index(self, index):
        if index != self.selected_index:
            self.selected_index = index
            self.add_change_code('selected_item_changed')

    def activate_item(self, index):
        self.workspace.set_active_document(self.documents[index])


