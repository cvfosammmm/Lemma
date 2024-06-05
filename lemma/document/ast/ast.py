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

from lemma.document.ast.node import Node
from lemma.document.ast.cursor import Cursor
from lemma.document.ast.iterator import ASTIterator


class AST(object):

    def __init__(self):
        self.root = Node('root')
        self.root.insert(0, Node('EOL', '\n'))
        self.cursor = Cursor(self, self.root[0], self.root[0])

    ''' cursor movement '''

    def move_insert_left(self):
        prev_node = ASTIterator.prev(self.get_insert_node())
        if prev_node != None:
            self.move_insert_to_node(prev_node)

    def move_insert_right(self):
        next_node = ASTIterator.next(self.get_insert_node())
        if next_node != None:
            self.move_insert_to_node(next_node)

    def move_insert_to_node(self, node):
        self.cursor.set_insert_selection_nodes(node, node)

    def move_selection_bound_to_node(self, node):
        self.cursor.set_selection_node(node)

    def move_insert_left_with_selection(self):
        self.move_insert_to_node_with_selection(ASTIterator.prev_no_descent(self.get_insert_node()))

    def move_insert_right_with_selection(self):
        self.move_insert_to_node_with_selection(ASTIterator.next_no_descent(self.get_insert_node()))

    def move_insert_to_node_with_selection(self, node):
        self.cursor.set_insert_node(node)
        self.cursor.restore_selection_invariant()

    def set_cursor_state(self, position):
        self.cursor.set_insert_position(position[0])
        self.cursor.set_selection_position(position[1])

    ''' cursor state '''

    def get_cursor_state(self):
        return [self.cursor.get_insert_position(), self.cursor.get_selection_position()]

    def get_insert_node(self):
        return self.cursor.get_insert_node()

    def get_node_at_position(self, pos):
        node = self.root
        for index in pos:
            node = node[index]
        return node

    def get_first_cursor_pos(self):
        if self.cursor.get_insert_position() < self.cursor.get_selection_position():
            return self.cursor.get_insert_position()
        else:
            return self.cursor.get_selection_position()

    def get_last_cursor_pos(self):
        if self.cursor.get_insert_position() < self.cursor.get_selection_position():
            return self.cursor.get_selection_position()
        else:
            return self.cursor.get_insert_position()

    def has_selection(self):
        return self.cursor.has_selection()

    ''' editing '''

    def insert_node(self, node):
        parent = self.get_insert_node().parent
        index = parent.index(self.get_insert_node())
        parent.insert(index, node)
        return [node]

    def delete_selection(self):
        if self.cursor.get_insert_position() < self.cursor.get_selection_position():
            first_node = self.cursor.get_insert_node()
            last_node = self.cursor.get_selection_node()
        else:
            first_node = self.cursor.get_selection_node()
            last_node = self.cursor.get_insert_node()

        deleted_nodes = []
        while first_node != last_node:
            deleted_nodes += [first_node]
            parent = first_node.parent
            index = parent.index(first_node)
            parent.remove(first_node)
            first_node = parent[index]

        self.move_insert_to_node(first_node)
        return deleted_nodes

    def delete_node(self, node):
        node.parent.remove(node.parent[node.parent.index(node)])

    def get_subtree(self, pos1, pos2):
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        parent = self.get_node_at_position(pos1[:-1])

        return parent[pos1[-1]:pos2[-1]]


