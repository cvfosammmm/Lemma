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

from lemma.document.ast.node import Root
from lemma.document.ast.cursor import Cursor


class AST(object):

    def __init__(self):
        self.root = Root()
        self.insert = Cursor(self, self.root.get_child(0))
        self.selection_bound = Cursor(self, self.root.get_child(0))

    ''' cursor movement '''

    def move_insert_left(self):
        iterator = self.get_insert_node().get_iterator()
        iterator.prev()
        self.move_insert_to_node(iterator.get_node())

    def move_insert_right(self):
        iterator = self.get_insert_node().get_iterator()
        iterator.next()
        self.move_insert_to_node(iterator.get_node())

    def move_insert_to_node(self, node):
        self.insert.set_node(node)
        self.selection_bound.set_node(node)

    def move_selection_bound_to_node(self, node):
        self.selection_bound.set_node(node)

    def move_insert_left_with_selection(self):
        node = self.insert.get_node()

        if node != node.parent.get_child(0):
            iterator = self.get_insert_node().get_iterator()
            iterator.prev_in_current_parent()
            self.insert.set_node(iterator.get_node())
        elif not node.parent.is_root():
            self.move_insert_left()
            iterator = self.get_insert_node().get_iterator()
            iterator.next_in_current_parent()
            self.selection_bound.set_node(iterator.get_node())

    def move_insert_right_with_selection(self):
        node = self.insert.get_node()

        if node != node.parent.get_child(-1):
            iterator = self.get_insert_node().get_iterator()
            iterator.next_in_current_parent()
            self.insert.set_node(iterator.get_node())
        elif not node.parent.is_root():
            self.move_insert_right()
            iterator = self.get_insert_node().get_iterator()
            iterator.prev_in_current_parent()
            self.selection_bound.set_node(iterator.get_node())

    def set_cursor_state(self, position):
        self.insert.set_position(position[0])
        self.selection_bound.set_position(position[1])

    ''' cursor state '''

    def get_cursor_state(self):
        return [self.insert.get_position(), self.selection_bound.get_position()]

    def get_insert_node(self):
        return self.insert.get_node()

    def has_selection(self):
        return self.insert.get_node() != self.selection_bound.get_node()

    ''' editing '''

    def insert_node(self, node):
        parent = self.get_insert_node().parent
        index = parent.get_index(self.get_insert_node())
        parent.insert(index, node)
        return [node]

    def delete_selection(self):
        if self.insert.get_position() > self.selection_bound.get_position():
            first_node = self.selection_bound.get_node()
            last_node = self.insert.get_node()
        else:
            first_node = self.insert.get_node()
            last_node = self.selection_bound.get_node()

        deleted_nodes = []
        while first_node != last_node:
            deleted_nodes += [first_node]
            parent = first_node.parent
            index = parent.get_index(first_node)
            parent.remove(first_node)
            first_node = parent.get_child(index)

        self.move_insert_to_node(first_node)
        return deleted_nodes

    def delete_node(self, node):
        node.parent.remove(node.parent.get_child(node.parent.get_index(node)))


