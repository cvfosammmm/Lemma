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


class Command():

    def __init__(self):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.ast.get_cursor_state()
        self.state['deleted_nodes'] = []

        node = document.ast.get_insert_node()
        if document.ast.has_selection():
            self.state['deleted_nodes'] = document.ast.delete_selection()
        elif not node.is_first_in_parent() or node.parent.length() == 1:
            document.ast.move_insert_left_with_selection()
            self.state['deleted_nodes'] = document.ast.delete_selection()

        self.is_undo_checkpoint = (len(self.state['deleted_nodes']) > 0)
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for node in self.state['deleted_nodes']:
            document.ast.insert_node(node)
        document.ast.set_cursor_state(self.state['cursor_state_before'])
        document.set_scroll_insert_on_screen_after_layout_update()


