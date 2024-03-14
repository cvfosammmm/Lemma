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

    def __init__(self, text):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.text = text
        self.state = dict()

    def run(self, document):
        self.state['insert_position_before'] = document.ast.insert.get_position()
        self.state['chars_added'] = []

        for char in self.text:
            if document.ast.insert.get_node().parent.is_line():
                self.state['chars_added'] += document.ast.insert_character(char)
                document.set_scroll_insert_on_screen_after_layout_update()

            elif document.ast.insert.get_node().parent.is_math_area():
                node = document.ast.insert.get_node()

                if char.isalnum():
                    self.state['chars_added'] += document.ast.insert_character(char)
                elif char == '-':
                    self.state['chars_added'] += document.ast.insert_character('−')
                elif char == '|':
                    self.state['chars_added'] += document.ast.insert_character('|')
                elif char in ['+', '=', '<', '>']:
                    self.state['chars_added'] += document.ast.insert_character(char)
                elif char == ' ' and node == node.parent.get_child(-1):
                    document.ast.move_cursor_by_offset(1)

        self.is_undo_checkpoint = (len(self.state['chars_added']) > 0)
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for node in self.state['chars_added']:
            document.ast.delete_node(node)
        document.ast.insert.set_position(self.state['insert_position_before'])
        document.set_scroll_insert_on_screen_after_layout_update()


