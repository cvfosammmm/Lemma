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

from lemma.services.message_bus import MessageBus
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases


class Backlinks(object):

    def __init__(self, main_window, model_state):
        self.main_window = main_window
        self.view = self.main_window.backlinks
        self.model_state = model_state

        self.view.listbox.connect('row-activated', self.on_row_activated)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'document_removed')
        MessageBus.subscribe(self, 'document_ast_changed')
        MessageBus.subscribe(self, 'mode_set')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'document_removed' in messages or 'document_ast_changed' in messages or 'mode_set' in messages:
            self.update()

    def update(self):
        if self.model_state.has_active_doc:
            backlinks = DocumentRepo.list_by_link_target(self.model_state.document.title)
            if len(backlinks) > 0:
                self.view.show_backlinks(backlinks)
            else:
                self.view.show_no_backlinks_page(self.model_state.document.title)
        else:
            self.view.show_no_open_documents_page()

    def on_row_activated(self, listbox, row):
        document_id = row.get_child().document_id

        UseCases.set_active_document(document_id)
        UseCases.scroll_to_xy(0, 0, animation_type=None)


