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
from gi.repository import Gtk, Pango

from lemma.services.message_bus import MessageBus
from lemma.repos.workspace_repo import WorkspaceRepo


class CursorState():

    def __init__(self, main_window, application):
        self.application = application

        self.tags_at_cursor = set()
        self.implicit_x_position = 0

        MessageBus.subscribe(self, 'new_active_document')
        MessageBus.subscribe(self, 'document_ast_or_cursor_changed')
        MessageBus.subscribe(self, 'implicit_x_position_changed')

        self.update_tags_at_cursor()
        self.update_implicit_x_position()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'new_active_document' in messages or 'document_ast_or_cursor_changed' in messages:
            self.update_tags_at_cursor()

        if 'new_active_document' in messages or 'implicit_x_position_changed' in messages:
            self.update_implicit_x_position()

    def update_implicit_x_position(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        layout = document.get_layout()
        insert = document.cursor.get_insert_node()

        x, y = layout.get_absolute_xy(layout.get_node_layout(insert))
        self.implicit_x_position = x

    def update_tags_at_cursor(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            self.tags_at_cursor = set()
        else:
            node = document.get_insert_node()

            if node.parent.type == 'paragraph':
                prev_node = node.prev_no_descent()
            else:
                prev_node = node.prev_in_parent()

            if node == None or prev_node == None:
                self.tags_at_cursor = set()
            else:
                self.tags_at_cursor = prev_node.tags.copy()


