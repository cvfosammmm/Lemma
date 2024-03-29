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
from lemma.document.ast.node import UnicodeCharacter, MathSymbol


class Command():

    def __init__(self, text):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.text = text
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before_1'] = document.ast.get_cursor_state()
        self.state['cursor_state_before_2'] = document.ast.get_cursor_state()
        self.state['deleted_nodes'] = []
        self.state['nodes_added'] = []

        node = document.ast.get_insert_node()
        if node.parent.is_root():
            self.state['deleted_nodes'] = document.ast.delete_selection()
            self.state['cursor_state_before_2'] = document.ast.get_cursor_state()
            for char in self.text:
                character = UnicodeCharacter(char)
                self.state['nodes_added'] += document.ast.insert_node(character)

        elif node.parent.is_math_area():
            if not document.ast.has_selection() and self.text == ' ' and node == node.parent.get_child(-1):
                document.ast.move_insert_right()
            else:
                self.state['deleted_nodes'] = document.ast.delete_selection()
                self.state['cursor_state_before_2'] = document.ast.get_cursor_state()
                for char in self.text:
                    if char == 'h': char = '\u210E'
                    elif char.isalpha() and char.islower(): char = chr(ord(char) + 119789)
                    elif char.isalpha() and char.isupper(): char = chr(ord(char) + 119795)
                    elif char == '-': char = '−'
                    elif char == '*': char = '∗'
                    elif char == '\'': char = '′'

                    if LaTeXDB.is_mathsymbol(char):
                        character = MathSymbol(char)
                        self.state['nodes_added'] += document.ast.insert_node(character)
                if len(self.state['nodes_added']) == 0:
                    for node in self.state['deleted_nodes']:
                        document.ast.insert_node(node)
                    self.state['deleted_nodes'] = []
                    document.ast.set_cursor_state(self.state['cursor_state_before_1'])

        self.is_undo_checkpoint = (len(self.state['nodes_added']) > 0 or len(self.state['deleted_nodes']) > 0 )
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for node in self.state['nodes_added']:
            document.ast.delete_node(node)
        document.ast.set_cursor_state(self.state['cursor_state_before_2'])
        document.set_scroll_insert_on_screen_after_layout_update()

        for node in self.state['deleted_nodes']:
            document.ast.insert_node(node)
        document.ast.set_cursor_state(self.state['cursor_state_before_1'])


