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

from lemma.services.message_bus import MessageBus
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class PinnedDocuments():

    def __init__(self, main_window):
        self.pin_buttons = main_window.headerbar.hb_right.pin_buttons
        self.pin_buttons_box = main_window.headerbar.hb_right.pin_buttons_box

        for i, button in self.pin_buttons.items():
            button.connect('clicked', self.on_pin_button_clicked, i)

        MessageBus.subscribe(self, 'pinned_documents_changed')

        self.update()

    @timer.timer
    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'pinned_documents_changed' in messages:
            self.update()

    @timer.timer
    def update(self):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()

        for i in range(len(pinned_documents)):
            document_title = DocumentRepo.get_stub_by_id(pinned_documents[i])['title']
            if document_title != None:
                document_title = '"' + document_title + '"'
            else:
                document_title = 'Pinned Document ' + str(i + 1)

            button = self.pin_buttons[i + 1]
            button.set_tooltip_text('Activate ' + document_title + ' (Alt+' + str(i + 1) + ')')

        for i, button in self.pin_buttons.items():
            button.set_sensitive(len(pinned_documents) >= i)
            button.set_visible(len(pinned_documents) >= i)

        self.pin_buttons_box.set_visible(len(pinned_documents) > 0)

    def on_pin_button_clicked(self, button, button_pos):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()

        if len(pinned_documents) >= button_pos:
            document_id = pinned_documents[button_pos - 1]
            UseCases.set_active_document(document_id, update_history=True)


