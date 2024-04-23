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

from lemma.document.ast.iterator import Iterator


class Node():

    def __init__(self, head):
        self.parent = None
        self.children = []
        self.head = head
        self.box = None

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
        node.set_parent(self)

    def get_child(self, index):
        return self.children[index]

    def get_index(self, node):
        return self.children.index(node)

    def length(self):
        return len(self.children)

    def get_iterator(self):
        return Iterator(self)

    def is_leaf(self): return len(self.children) == 0
    def is_root(self): return self.head == 'root'
    def is_matharea(self): return self.head == 'matharea'


