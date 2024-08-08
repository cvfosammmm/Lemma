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


class Cursor():

    def __init__(self, ast, node_insert=None, node_selection=None):
        self.ast = ast
        self.node_insert = node_insert
        self.node_selection = node_selection

    def set_insert_node(self, node):
        self.node_insert = node

    def set_selection_node(self, node):
        self.node_selection = node

    def set_insert_selection_nodes(self, node_insert, node_selection):
        self.node_insert = node_insert
        self.node_selection = node_selection

    def set_insert_position(self, position):
        self.set_insert_node(self.ast.root.get_node_at_position(position))

    def set_selection_position(self, position):
        self.set_selection_node(self.ast.root.get_node_at_position(position))

    ''' cursor movement '''

    def move_insert_left(self):
        self.move_insert_to_node(self.get_insert_node().prev())

    def move_insert_right(self):
        self.move_insert_to_node(self.get_insert_node().next())

    def move_insert_left_with_selection(self):
        self.move_insert_to_node_with_selection(self.get_insert_node().prev_no_descent())

    def move_insert_right_with_selection(self):
        self.move_insert_to_node_with_selection(self.get_insert_node().next_no_descent())

    def move_insert_to_node(self, node):
        if node != None:
            self.set_insert_selection_nodes(node, node)

    def move_selection_bound_to_node(self, node):
        if node != None:
            self.set_selection_node(node)

    def move_insert_to_node_with_selection(self, node):
        if node != None:
            self.set_insert_node(node)
            self.restore_selection_invariant()

    def set_state(self, position):
        self.set_insert_position(position[0])
        self.set_selection_position(position[1])

    def get_state(self):
        return [self.get_insert_position(), self.get_selection_position()]

    def get_insert_node(self):
        return self.node_insert

    def get_selection_node(self):
        return self.node_selection

    def get_insert_position(self):
        return self.node_insert.get_position()

    def get_selection_position(self):
        return self.node_selection.get_position()

    def get_first_cursor_pos(self):
        if self.get_insert_position() < self.get_selection_position():
            return self.get_insert_position()
        else:
            return self.get_selection_position()

    def get_last_cursor_pos(self):
        if self.get_insert_position() < self.get_selection_position():
            return self.get_selection_position()
        else:
            return self.get_insert_position()

    def has_selection(self):
        return self.get_insert_node() != self.get_selection_node()

    # restore the invariant that both the insert and the selection bound have the same parent.
    def restore_selection_invariant(self):

        # special cases where the invariant already holds
        if not self.has_selection(): return
        if self.node_insert.parent == self.node_selection.parent: return

        # compute the smallest common ancestor of both the insert and the selection node.
        ancestors = zip(self.node_insert.ancestors(), self.node_selection.ancestors())
        sca = list(filter(lambda x: x[0] == x[1], ancestors))[-1][0]

        # compute the new positions
        sca_pos = sca.get_position()
        pos1, pos2 = self.get_selection_position(), self.get_insert_position()
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        if len(pos1) > len(sca_pos) + 1:
            pos1 = pos1[:len(sca_pos) + 1]
        if len(pos2) > len(sca_pos) + 1:
            pos2 = pos2[:len(sca_pos) + 1]
            pos2[-1] += 1

        # move both insert and selection bound to the sca
        if self.get_insert_position() < self.get_selection_position():
            self.set_insert_position(pos1)
            self.set_selection_position(pos2)
        else:
            self.set_insert_position(pos2)
            self.set_selection_position(pos1)


