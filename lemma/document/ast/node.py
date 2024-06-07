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

from lemma.document.ast.position import Position


class Node():

    def __init__(self, node_type, value=None):
        self.parent = None
        self.children = []
        self.type = node_type
        self.value = value
        self.box = None
        self.tags = set()
        self.link = None

    def set_parent(self, parent):
        self.parent = parent

    def set_box(self, box):
        self.box = box

    def insert(self, index, node):
        self.children.insert(index, node)
        node.set_parent(self)

    def append(self, node):
        self.insert(-1, node)

    def remove(self, node):
        self.children.remove(node)
        node.set_parent(None)

    def index(self, node):
        return self.children.index(node)

    def get_position(self):
        node = self
        position = list()
        while not node.is_root():
            position.insert(0, node.parent.index(node))
            node = node.parent

        return Position(*position)

    def __len__(self): return len(self.children)
    def __iter__(self): return self.children.__iter__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            node = Node(self.type, self.value)
            node.tags = self.tags
            node.link = self.link
            node.children = self.children.__getitem__(key)
            return node
        else:
            return self.children.__getitem__(key)

    def ancestors(self):
        node = self
        ancestors = []
        while not node.is_root():
            ancestors.insert(0, node.parent)
            node = node.parent

        return ancestors

    def is_leaf(self): return len(self.children) == 0
    def is_first_in_parent(self): return self == self.parent[0]
    def is_last_in_parent(self): return self == self.parent[-1]
    def is_root(self): return self.parent == None
    def is_mathsymbol(self): return self.type == 'mathsymbol'
    def is_matharea(self): return self.type == 'matharea'
    def is_char(self): return self.type == 'char'

    def is_inside_link(self):
        if self.link == None: return False
        if self.is_first_in_parent(): return False
        return self.link == self.prev_in_parent().link

    def get_bounds_for_link(self):
        if self.link == None: return (None, None)
        if self.is_first_in_parent(): return (None, None)

        node1 = self
        node2 = self

        while node2.link == self.link:
            next_node = node2.next_in_parent()
            if next_node != None:
                node2 = next_node
            else:
                break
        while node1.link == self.link:
            prev_node = node1.prev_in_parent()
            if prev_node != None:
                node1 = prev_node
            else:
                break

        return (node1.get_position(), node2.get_position())

    def prev(self):
        node = self
        if node != node.parent[0]:
            node = node.parent[node.parent.index(node) - 1]
            while not node.is_leaf():
                node = node[-1]
            return node

        elif not node.parent.is_root():
            return node.parent

        return None

    def next(self):
        node = self
        if not node.is_leaf():
            node = node[0]
        else:
            while not node.is_root() and node.parent.index(node) == len(node.parent) - 1:
                node = node.parent
            if node.is_root():
                return None
            else:
                node = node.parent[node.parent.index(node) + 1]

        return node

    def prev_no_descent(self):
        node = self
        if node != node.parent[0]:
            index = node.parent.index(node) - 1
            node = node.parent[index]

        elif not node.parent.is_root():
            node = node.parent

        return node

    def next_no_descent(self):
        node = self
        if node != node.parent[-1]:
            index = node.parent.index(node) + 1
            node = node.parent[index]

        else:
            while not node.is_root() and node.parent.index(node) == len(node.parent) - 1:
                node = node.parent
            if node.is_root():
                return
            else:
                node = node.parent[node.parent.index(node) + 1]

        return node

    def prev_in_parent(self):
        if self != self.parent[0]:
            index = self.parent.index(self) - 1
            return self.parent[index]
        return None

    def next_in_parent(self):
        if self != self.parent[-1]:
            index = self.parent.index(self) + 1
            return self.parent[index]
        return None


