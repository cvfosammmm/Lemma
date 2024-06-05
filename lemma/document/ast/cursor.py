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

    def set_node_insert(self, node):
        self.node_insert = node

    def set_node_selection(self, node):
        self.node_selection = node

    def set_nodes_insert_selection(self, node_insert, node_selection):
        self.node_insert = node_insert
        self.node_selection = node_selection

    def set_position_insert(self, position):
        self.set_node_insert(self.ast.get_node_at_position(position))

    def set_position_selection(self, position):
        self.set_node_selection(self.ast.get_node_at_position(position))

    def get_node_insert(self):
        return self.node_insert

    def get_node_selection(self):
        return self.node_selection

    def get_position_insert(self):
        return self.node_insert.get_position()

    def get_position_selection(self):
        return self.node_selection.get_position()

    def has_selection(self):
        return self.get_node_insert() != self.get_node_selection()

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
        pos1, pos2 = self.get_position_selection(), self.get_position_insert()
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        if len(pos1) > len(sca_pos) + 1:
            pos1 = pos1[:len(sca_pos) + 1]
        if len(pos2) > len(sca_pos) + 1:
            pos2 = pos2[:len(sca_pos) + 1]
            pos2[-1] += 1

        # move both insert and selection bound to the sca
        if self.get_position_insert() < self.get_position_selection():
            self.set_position_insert(pos1)
            self.set_position_selection(pos2)
        else:
            self.set_position_insert(pos2)
            self.set_position_selection(pos1)


