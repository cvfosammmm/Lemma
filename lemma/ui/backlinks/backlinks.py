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
from gi.repository import Gtk, Gdk

from lemma.document_repo.document_repo import DocumentRepo


class Backlinks(object):

    def __init__(self, workspace, main_window, application):
        self.main_window = main_window
        self.view = self.main_window.backlinks
        self.application = application
        self.workspace = workspace

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('document_changed', self.on_document_changed)
        self.workspace.connect('mode_set', self.on_mode_set)

        self.view.listbox.connect('row-activated', self.on_row_activated)

        self.update()

    def on_new_active_document(self, workspace, document=None): self.update()
    def on_document_removed(self, workspace, document): self.update()
    def on_document_changed(self, workspace, document): self.update()
    def on_mode_set(self, workspace): self.update()

    def update(self):
        active_document = self.workspace.active_document
        has_active_doc = (self.workspace.mode == 'documents' and active_document != None)

        self.view.reset()
        if not has_active_doc:
            pass
        else:
            backlinks = DocumentRepo.list_by_link_target(active_document.title)
            for document_id in backlinks:
                linking_doc = DocumentRepo.get_by_id(document_id)
                self.view.add_item(linking_doc)

    def on_row_activated(self, listbox, row):
        self.application.use_cases.set_active_document(row.get_child().document)


