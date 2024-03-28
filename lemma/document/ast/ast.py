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
from lemma.helpers.helpers import position_less_than


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
        iterator = self.get_insert_node().get_iterator()
        iterator.prev_no_descent()
        self.insert.set_node(iterator.get_node())
        self.restore_selection_invariant()

    def move_insert_right_with_selection(self):
        iterator = self.get_insert_node().get_iterator()
        iterator.next_no_descent()
        self.insert.set_node(iterator.get_node())
        self.restore_selection_invariant()

    def move_insert_to_node_with_selection(self, node):
        self.insert.set_node(node)
        self.restore_selection_invariant()

    def restore_selection_invariant(self):
        sca = self.smallest_common_real_ancestor(self.insert.get_node(), self.selection_bound.get_node())

        if self.insert.get_node() == self.selection_bound.get_node(): return
        if self.insert.get_node().parent == sca and self.selection_bound.get_node().parent == sca: return

        node_1 = [node for node in self.get_insert_iter().get_ancestors() if node.parent == sca][0]
        node_2 = [node for node in self.get_selection_iter().get_ancestors() if node.parent == sca][0]

        if position_less_than(self.selection_bound.get_position(), self.insert.get_position()):
            selection_node = sca.get_child(sca.get_index(node_2))
            insert_node = sca.get_child(sca.get_index(node_1) + 1)
        else:
            insert_node = sca.get_child(sca.get_index(node_1))
            selection_node = sca.get_child(sca.get_index(node_2) + 1)

        if self.selection_bound.get_node().parent != sca:
            self.selection_bound.set_node(selection_node)
        if self.insert.get_node().parent != sca:
            self.insert.set_node(insert_node)

    def smallest_common_real_ancestor(self, node_1, node_2):
        ancestors_1 = node_1.get_iterator().get_ancestors()[:-1]
        ancestors_2 = node_2.get_iterator().get_ancestors()[:-1]
        i = 0
        for i in range(0, min(len(ancestors_1), len(ancestors_2))):
            if ancestors_1[i] == ancestors_2[i]:
                sca = ancestors_1[i]
            else:
                break
        return sca

    def set_cursor_state(self, position):
        self.insert.set_position(position[0])
        self.selection_bound.set_position(position[1])

    ''' cursor state '''

    def get_cursor_state(self):
        return [self.insert.get_position(), self.selection_bound.get_position()]

    def get_insert_node(self):
        return self.insert.get_node()

    def get_insert_iter(self):
        return self.insert.get_node().get_iterator()

    def get_selection_iter(self):
        return self.selection_bound.get_node().get_iterator()

    def get_first_cursor_pos(self):
        if position_less_than(self.insert.get_position(), self.selection_bound.get_position()):
            return self.insert.get_position()
        else:
            return self.selection_bound.get_position()

    def get_last_cursor_pos(self):
        if position_less_than(self.insert.get_position(), self.selection_bound.get_position()):
            return self.selection_bound.get_position()
        else:
            return self.insert.get_position()

    def has_selection(self):
        return self.insert.get_node() != self.selection_bound.get_node()

    ''' editing '''

    def insert_node(self, node):
        parent = self.get_insert_node().parent
        index = parent.get_index(self.get_insert_node())
        parent.insert(index, node)
        return [node]

    def delete_selection(self):
        if position_less_than(self.insert.get_position(), self.selection_bound.get_position()):
            first_node = self.insert.get_node()
            last_node = self.selection_bound.get_node()
        else:
            first_node = self.selection_bound.get_node()
            last_node = self.insert.get_node()

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


