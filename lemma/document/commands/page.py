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
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()

        layout = document.cursor.get_insert_node().layout
        while layout.parent.parent != None:
            layout = layout.parent
        line_index = layout.parent.children.index(layout)

        if self.offset > 0 and line_index == len(layout.parent.children) - 1:
            new_node = layout.children[-1].node
        elif self.offset <= 0 and line_index == 0:
            new_node = layout.children[0].node
        else:
            x, y = document.cursor.get_insert_node().layout.get_absolute_xy()
            if document.implicit_x_position != None:
                x = document.implicit_x_position
            target_pos = y + self.offset

            if self.offset > 0:
                while line_index < len(layout.parent.children) - 1 and layout.parent.children[line_index].y < target_pos:
                    line_index += 1
            else:
                while line_index > 0 and layout.parent.children[line_index].y > target_pos:
                    line_index -= 1
            new_line = layout.parent.children[line_index]

            closest_child = None
            closest_child_dist = 10000
            for child in new_line.children:
                if abs(child.x - x) < closest_child_dist:
                    closest_child = child
                    closest_child_dist = abs(child.x - x)
            new_node = closest_child.node

        if self.do_selection:
            document.cursor.move_insert_to_node_with_selection(new_node)
        else:
            document.cursor.move_insert_to_node(new_node)

        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        document.cursor.set_state(self.state['cursor_state_before'])

  
