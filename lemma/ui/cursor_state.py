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
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class CursorState():

    def __init__(self, main_window):
        self.toolbar = main_window.toolbar

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'app_state_changed')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'document_changed' in messages:
            self.update()

        if 'app_state_changed' in messages:
            self.update_tag_toggle(self.toolbar.toolbar_main.bold_button, 'bold')
            self.update_tag_toggle(self.toolbar.toolbar_main.italic_button, 'italic')

    @timer.timer
    def update(self):
        self.update_tags_and_link_at_cursor()
        self.update_tag_toggle(self.toolbar.toolbar_main.bold_button, 'bold')
        self.update_tag_toggle(self.toolbar.toolbar_main.italic_button, 'italic')

    @timer.timer
    def update_tags_and_link_at_cursor(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            UseCases.app_state_set_values({'tags_at_cursor': set(), 'link_at_cursor': None})
        else:
            node = document.cursor.get_insert_node()
            prev_node = node.prev_in_parent()

            if node == None or prev_node == None:
                UseCases.app_state_set_values({'tags_at_cursor': set(), 'link_at_cursor': None})
            else:
                if node.link == prev_node.link:
                    UseCases.app_state_set_values({'tags_at_cursor': prev_node.tags.copy(), 'link_at_cursor': node.link})
                else:
                    UseCases.app_state_set_values({'tags_at_cursor': prev_node.tags.copy(), 'link_at_cursor': None})

    def update_tag_toggle(self, button, tagname):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        chars_selected = False
        all_tagged = True
        if document.cursor.has_selection():
            for node in [node for node in document.ast.get_subtree(*document.cursor.get_state()) if node.type == 'char']:
                chars_selected = True
                if tagname not in node.tags:
                    all_tagged = False
                    break

        if chars_selected:
            if all_tagged:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')
        else:
            if tagname in ApplicationState.get_value('tags_at_cursor'):
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')


