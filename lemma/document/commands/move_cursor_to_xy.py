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

    def __init__(self, x, y, do_selection=False):
        self.x = x
        self.y = y
        self.do_selection = do_selection
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.get_cursor_state()

        layout = document.get_cursor_holding_layout_close_to_xy(self.x, self.y)

        if self.do_selection:
            document.cursor.move_insert_to_node_with_selection(layout['node'])
        else:
            document.cursor.move_insert_to_node(layout['node'])

        document.update_last_cursor_movement()

    def undo(self, document):
        document.cursor.set_state(self.state['cursor_state_before'])

        document.update_last_cursor_movement()


