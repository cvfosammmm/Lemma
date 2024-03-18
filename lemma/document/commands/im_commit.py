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

from lemma.app.latex_db import LaTeXDB


class Command():

    def __init__(self, text):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.text = text
        self.state = dict()

    def run(self, document):
        self.state['insert_position_before'] = document.ast.insert.get_position()
        self.state['chars_added'] = []

        node = document.ast.insert.get_node()
        if node.parent.is_line():
            for char in self.text:
                self.state['chars_added'] += document.ast.insert_character(char)

        elif node.parent.is_math_area():
            if self.text == ' ' and node == node.parent.get_child(-1):
                document.ast.move_cursor_by_offset(1)
            else:
                for char in self.text:
                    if char.isalpha() and char.islower(): char = chr(ord(char) + 119789)
                    elif char.isalpha() and char.isupper(): char = chr(ord(char) + 119795)
                    elif char == '-': char = '−'
                    elif char == '*': char = '∗'

                    if LaTeXDB.is_mathsymbol(char):
                        self.state['chars_added'] += document.ast.insert_mathsymbol(char)

        self.is_undo_checkpoint = (len(self.state['chars_added']) > 0)
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for node in self.state['chars_added']:
            document.ast.delete_node(node)
        document.ast.insert.set_position(self.state['insert_position_before'])
        document.set_scroll_insert_on_screen_after_layout_update()


