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


class AST(object):

    def __init__(self):
        self.root = Node('list')
        self.root.insert(0, Node('EOL', '\n'))
        self.cursor = Cursor(self, self.root[0], self.root[0])

    def insert_node(self, node):
        parent = self.cursor.get_insert_node().parent
        index = parent.index(self.cursor.get_insert_node())
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

        self.cursor.move_insert_to_node(first_node)
        return deleted_nodes

    def delete_node(self, node):
        node.parent.remove(node.parent[node.parent.index(node)])

    def get_subtree(self, pos1, pos2):
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        parent = self.root.get_node_at_position(pos1[:-1])

        return parent[pos1[-1]:pos2[-1]]


