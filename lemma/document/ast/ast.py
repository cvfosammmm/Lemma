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


class AST(object):

    def __init__(self):
        self.root = Node('list')
        self.root.insert(0, Node('EOL', '\n'))

    def delete_range(self, first_node, last_node):
        deleted_nodes = []
        while first_node != last_node:
            deleted_nodes += [first_node]
            parent = first_node.parent
            index = parent.index(first_node)
            parent.remove(first_node)
            first_node = parent[index]

        return deleted_nodes

    def delete_node(self, node):
        node.parent.remove(node.parent[node.parent.index(node)])

    def get_subtree(self, pos1, pos2):
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        parent = self.root.get_node_at_position(pos1[:-1])

        return parent[pos1[-1]:pos2[-1]]


