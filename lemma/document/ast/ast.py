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
from lemma.document.ast.cursor import Cursor


class AST(object):

    def __init__(self):
        self.root = ast.Root()
        self.root.insert(0, ast.Line())
        self.insert = Cursor(self, self.root.get_child(0).get_child(0))
        self.selection_bound = Cursor(self, self.root.get_child(0).get_child(0))

    def move_insert_to_position(self, position):
        self.insert.set_position(position)
        self.selection_bound.set_position(position)

    def move_insert_by_offset(self, offset):
        offset_moved = 0
        iterator = self.get_insert_node().get_iterator()

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
        self.move_insert_to_node(iterator.get_node())

        return offset_moved

    def move_insert_to_node(self, node):
        self.insert.set_node(node)
        self.selection_bound.set_node(node)

    def get_insert_node(self):
        return self.insert.get_node()

    def get_insert_position(self):
        return self.insert.get_position()

    def insert_node(self, node):
        if isinstance(node, ast.EndOfLine):
            self.insert_linebreak()
        else:
            parent = self.get_insert_node().parent
            index = parent.get_index(self.get_insert_node())
            parent.insert(index, node)

    def insert_character(self, char):
        composite_node = self.get_insert_node().parent
        index = composite_node.get_index(self.get_insert_node())
        character = ast.UnicodeCharacter(char)
        composite_node.insert(index, character)

        return [character]

    def insert_mathsymbol(self, char):
        composite_node = self.get_insert_node().parent
        index = composite_node.get_index(self.get_insert_node())
        character = ast.MathSymbol(char)
        composite_node.insert(index, character)

        return [character]

    def insert_linebreak(self):
        orig_line = self.get_insert_node().get_iterator().get_line()
        line_1, line_2 = orig_line.split(self.get_insert_node())
        index = self.root.get_index(orig_line)
        self.root.remove(orig_line)
        self.root.insert(index, line_2)
        self.root.insert(index, line_1)
        self.move_insert_to_node(line_2.get_child(0))

    def insert_math_area(self):
        line = self.get_insert_node().get_iterator().get_line()
        index = line.get_index(self.get_insert_node())
        line.insert(index, ast.MathArea())
        line.insert(index, ast.BeforeMathArea())
        self.move_insert_by_offset(-1)

    def delete_node(self, node):
        node.parent.remove(node.parent.get_child(node.parent.get_index(node)))

    def delete_char_at_insert(self):
        if self.get_insert_node().parent.is_line():
            line = self.get_insert_node().parent
            if self.get_insert_node() == line.get_child(-1) and line.parent.get_child(-1) == line:
                return []
            elif isinstance(self.get_insert_node(), ast.BeforeMathArea):
                return self.delete_math()
            elif self.get_insert_node() == line.get_child(-1):
                return self.delete_linebreak()
            else:
                return self.delete_char()
        elif self.get_insert_node().parent.is_math_area():
            math_area = self.get_insert_node().parent
            if self.get_insert_node() != math_area.get_child(-1):
                return self.delete_char()
            elif math_area.length() == 1:
                self.move_insert_by_offset(-1)
                return self.delete_math()
        return []

    def delete_math(self):
        line = self.get_insert_node().get_iterator().get_line()
        index = line.get_index(self.get_insert_node())
        deleted_nodes = [line.get_child(index), line.get_child(index + 1)]

        line.remove(line.get_child(index))
        line.remove(line.get_child(index))
        self.move_insert_to_node(line.get_child(index))

        return deleted_nodes

    def delete_char(self):
        parent = self.get_insert_node().parent
        index = parent.get_index(self.get_insert_node())
        deleted_nodes = [parent.get_child(index)]

        parent.remove(parent.get_child(index))
        self.move_insert_to_node(parent.get_child(index))

        return deleted_nodes

    def delete_linebreak(self):
        deleted_nodes = [self.get_insert_node()]

        line_1 = self.get_insert_node().get_iterator().get_line()
        line_2 = self.root.get_child(self.root.get_index(line_1) + 1)
        new_line = ast.Line()
        new_line.add(line_1)
        new_line.add(line_2)
        index = self.root.get_index(line_1)
        self.root.insert(index, new_line)
        self.root.remove(line_1)
        self.root.remove(line_2)
        self.move_insert_to_node(new_line.get_child(line_1.length() - 1))

        return deleted_nodes


