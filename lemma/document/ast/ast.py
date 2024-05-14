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
from lemma.document.ast.services import ASTIterator, sort_positions, node_to_position, position_to_node, position_less_than


class AST(object):

    def __init__(self):
        self.root = Node('root')
        self.root.insert(0, Node('EOL'))
        self.cursor = Cursor(self, self.root[0], self.root[0])

    ''' cursor movement '''

    def move_insert_left(self):
        self.move_insert_to_node(ASTIterator.prev(self.get_insert_node()))

    def move_insert_right(self):
        self.move_insert_to_node(ASTIterator.next(self.get_insert_node()))

    def move_insert_to_node(self, node):
        self.cursor.set_nodes_insert_selection(node, node)

    def move_selection_bound_to_node(self, node):
        self.cursor.set_node_selection(node)

    def move_insert_left_with_selection(self):
        self.move_insert_to_node_with_selection(ASTIterator.prev_no_descent(self.get_insert_node()))

    def move_insert_right_with_selection(self):
        self.move_insert_to_node_with_selection(ASTIterator.next_no_descent(self.get_insert_node()))

    def move_insert_to_node_with_selection(self, node):
        self.cursor.set_node_insert(node)
        self.cursor.restore_selection_invariant()

    def set_cursor_state(self, position):
        self.cursor.set_position_insert(position[0])
        self.cursor.set_position_selection(position[1])

    ''' cursor state '''

    def get_cursor_state(self):
        return [self.cursor.get_position_insert(), self.cursor.get_position_selection()]

    def get_insert_node(self):
        return self.cursor.get_node_insert()

    def get_first_cursor_pos(self):
        if position_less_than(self.cursor.get_position_insert(), self.cursor.get_position_selection()):
            return self.cursor.get_position_insert()
        else:
            return self.cursor.get_position_selection()

    def get_last_cursor_pos(self):
        if position_less_than(self.cursor.get_position_insert(), self.cursor.get_position_selection()):
            return self.cursor.get_position_selection()
        else:
            return self.cursor.get_position_insert()

    def has_selection(self):
        return self.cursor.has_selection()

    ''' editing '''

    def insert_node(self, node):
        parent = self.get_insert_node().parent
        index = parent.index(self.get_insert_node())
        parent.insert(index, node)
        return [node]

    def delete_selection(self):
        if position_less_than(self.cursor.get_position_insert(), self.cursor.get_position_selection()):
            first_node = self.cursor.get_node_insert()
            last_node = self.cursor.get_node_selection()
        else:
            first_node = self.cursor.get_node_selection()
            last_node = self.cursor.get_node_insert()

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
        pos1, pos2 = sort_positions(pos1, pos2)
        parent = position_to_node(pos1[:-1], self.root)

        return parent[pos1[-1]:pos2[-1]]

    def matching_subtree_around_node(self, node, match_function):
        parent = node.parent
        node1 = node
        node2 = node

        while match_function(node2):
            node2 = ASTIterator.next_in_parent(node2)
        while match_function(ASTIterator.prev_in_parent(node1)):
            node1 = ASTIterator.prev_in_parent(node1)

        return self.get_subtree(node_to_position(node1), node_to_position(node2))


