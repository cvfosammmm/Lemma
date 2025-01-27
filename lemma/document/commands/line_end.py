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

    def __init__(self, do_selection=False):
        self.do_selection = do_selection
        self.is_undo_checkpoint = False
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()

        insert = document.cursor.get_insert_node()
        layout = insert.layout
        while layout.parent.parent != None:
            layout = layout.parent
        while layout.children[-1].node == None:
            layout = layout.children[-1]
        node = layout.children[-1].node

        if self.do_selection:
            document.cursor.move_insert_to_node_with_selection(node)
        else:
            document.cursor.move_insert_to_node(node)

        document.set_scroll_insert_on_screen_after_layout_update()
        document.cursor.update_implicit_x_position()

    def undo(self, document):
        document.cursor.set_state(self.state['cursor_state_before'])


