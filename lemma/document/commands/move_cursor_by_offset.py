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

    def __init__(self, offset, do_selection=False):
        self.offset = offset
        self.do_selection = do_selection
        self.is_undo_checkpoint = False
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()

        cursor = document.cursor
        if self.do_selection:
            if self.offset < 0:
                for i in range(-self.offset):
                    cursor.move_insert_to_node_with_selection(cursor.prev_no_descent(cursor.get_insert_node()))
            else:
                for i in range(self.offset):
                    cursor.move_insert_to_node_with_selection(cursor.next_no_descent(cursor.get_insert_node()))
        else:
            if self.offset < 0:
                for i in range(-self.offset):
                    cursor.move_insert_to_node(cursor.prev(cursor.get_insert_node()))
            else:
                for i in range(self.offset):
                    cursor.move_insert_to_node(cursor.next(cursor.get_insert_node()))

        document.set_scroll_insert_on_screen_after_layout_update()
        document.cursor.update_implicit_x_position()

    def undo(self, document):
        document.cursor.set_state(self.state['cursor_state_before'])


