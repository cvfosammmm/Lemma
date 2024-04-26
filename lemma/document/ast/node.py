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


class Node():

    def __init__(self, head):
        self.parent = None
        self.children = []
        self.head = head
        self.box = None
        self.tags = set()

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

    def length(self):
        return len(self.children)

    def __iter__(self): return self.children.__iter__()
    def __getitem__(self, key): return self.children.__getitem__(key)

    def ancestors(self):
        node = self
        ancestors = [node]
        while not node.is_root():
            ancestors.insert(0, node.parent)
            node = node.parent

        return ancestors

    def is_leaf(self): return len(self.children) == 0
    def is_first_in_parent(self): return self == self.parent[0]
    def is_last_in_parent(self): return self == self.parent[-1]
    def is_root(self): return self.head == 'root'
    def is_math(self): return ('matharea' in [node.head for node in self.ancestors()])
    def is_matharea(self): return self.head == 'matharea'
    def is_char(self): return self.is_leaf() and not self.is_math()


