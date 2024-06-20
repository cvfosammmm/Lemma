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

    def __init__(self, height):
        self.is_undo_checkpoint = False
        self.height = height
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.ast.get_cursor_state()

        x, y = document.ast.get_insert_node().get_xy()
        if document.implicit_x_position != None:
            x = document.implicit_x_position
        if y == 0:
            document.ast.move_insert_to_node(document.layout.get_node_at_xy(0, 0))
        else:
            document.ast.move_insert_to_node(document.layout.get_node_at_xy(x, max(0, y - self.height)))
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        document.ast.set_cursor_state(self.state['cursor_state_before'])


