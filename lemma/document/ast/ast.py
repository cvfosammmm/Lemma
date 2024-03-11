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

import time

import lemma.document.ast.node as ast
from lemma.document.cursor.cursor import Cursor


class AST(object):

    def __init__(self):
        self.root = ast.Root()
        self.root.insert(0, ast.Line())
        self.insert = Cursor(self, self.root.get_child(0).get_child(0))

    def move_cursor_by_offset(self, offset):
        offset_moved = 0
        iterator = self.insert.get_node().get_iterator()

        if offset < 0:
            while offset < offset_moved:
                if iterator.prev() == False:
                    break
                offset_moved -= 1
        else:
            while offset > offset_moved:
                if iterator.next() == False:
                    break
                offset_moved += 1
        self.insert.set_node(iterator.get_node())

        return offset_moved

    def insert_node_at_cursor(self, node):
        if isinstance(node, ast.EndOfLine):
	        self.insert_linebreak()
        elif isinstance(node, ast.UnicodeCharacter):
	        self.insert_character(node.content)
        elif isinstance(node, ast.MathSymbol):
	        self.insert_math_symbol(node.name)

    def insert_text_at_cursor(self, text):
        for char in text:
            if char == '\n':
    	        self.insert_linebreak()
            else:
    	        self.insert_character(char)

    def insert_character(self, char):
        character = ast.UnicodeCharacter(char)
        line = self.insert.get_node().get_iterator().get_line()
        index = line.get_index(self.insert.get_node())
        line.insert(index, character)

    def insert_linebreak(self):
        orig_line = self.insert.get_node().get_iterator().get_line()
        line_1, line_2 = orig_line.split(self.insert.get_node())
        index = self.root.get_index(orig_line)
        self.root.remove(orig_line)
        self.root.insert(index, line_2)
        self.root.insert(index, line_1)
        self.insert.set_node(line_2.get_child(0))

    def insert_math_symbol(self, name):
        symbol = ast.MathSymbol(name)
        line = self.insert.get_node().get_iterator().get_line()
        index = line.get_index(self.insert.get_node())
        line.insert(index, symbol)

    def delete_char_at_cursor(self):
        deleted_node = None

        line = self.insert.get_node().get_iterator().get_line()
        if self.insert.get_node() == line.get_child(-1):
            if self.root.get_child(-1) != line:
                deleted_node = self.insert.get_node()

                line_1 = self.insert.get_node().get_iterator().get_line()
                line_2 = self.root.get_child(self.root.get_index(line_1) + 1)
                new_line = ast.Line()
                new_line.add(line_1)
                new_line.add(line_2)
                index = self.root.get_index(line_1)
                self.root.insert(index, new_line)
                self.root.remove(line_1)
                self.root.remove(line_2)
                self.insert.set_node(new_line.get_child(line_1.length() - 1))
        else:
            deleted_node = self.insert.get_node()

            line = self.insert.get_node().get_iterator().get_line()
            index = line.get_index(self.insert.get_node())
            line.remove(self.insert.get_node())
            self.insert.set_node(line.get_child(index))

        return deleted_node


