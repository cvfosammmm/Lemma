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

from lemma.helpers.helpers import position_less_than


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
        node = self.ast.root

        for index in position:
            node = node[index]
        self.set_node_insert(node)

    def set_position_selection(self, position):
        node = self.ast.root

        for index in position:
            node = node[index]
        self.set_node_selection(node)

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
        ancestors = zip(self.node_insert.ancestors()[:-1], self.node_selection.ancestors()[:-1])
        sca = list(filter(lambda x: x[0] == x[1], ancestors))[-1][0]

        # move both insert and selection bound to the sca.
        node_1 = [node for node in self.node_insert.ancestors() if node.parent == sca][0]
        node_2 = [node for node in self.node_selection.ancestors() if node.parent == sca][0]
        if position_less_than(self.get_position_selection(), self.get_position_insert()):
            insert_node = sca[sca.index(node_1) + 1]
            selection_node = sca[sca.index(node_2)]
        else:
            insert_node = sca[sca.index(node_1)]
            selection_node = sca[sca.index(node_2) + 1]
        if self.node_selection.parent != sca:
            self.set_node_selection(selection_node)
        if self.node_insert.parent != sca:
            self.set_node_insert(insert_node)


