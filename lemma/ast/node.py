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

import re
whitespace_regex = re.compile('\s')

from lemma.iterator.iterator import Iterator


class Node(object):

    def __init__(self):
        self.parent = None

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def set_parent(self, parent):
        self.parent = parent

    def accept(self, visitor):
        visitor.visit_node(self)

    def get_iterator(self):
        return Iterator(self)

    def is_line(self):
        return False


class Lines(Node):

    def __init__(self):
        Node.__init__(self)

        self.children = []

        self.iter_index = None

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        if self.iter_index < self.length():
            self.iter_index += 1
            return self.get_child(self.iter_index - 1)
        else:
            raise StopIteration

    def insert(self, index, node):
        self.children.insert(index, node)
        node.set_parent(self)

    def append(self, node):
        self.children.append(node)
        node.set_parent(self)

    def remove(self, node):
        self.children.remove(node)
        node.set_parent(self)

    def get_child(self, index):
        return self.children[index]

    def get_index(self, node):
        return self.children.index(node)

    def length(self):
        return len(self.children)

    def accept(self, visitor):
        visitor.visit_lines(self)


class Line(Node):

    def __init__(self):
        Node.__init__(self)

        self.children = []
        self.insert(0, EndOfLine())

        self.iter_index = None

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        if self.iter_index < self.length():
            self.iter_index += 1
            return self.get_child(self.iter_index - 1)
        else:
            raise StopIteration

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

    def accept(self, visitor):
        visitor.visit_line(self)

    def is_line(self):
        return True


class UnicodeCharacter(Node):

    def __init__(self, string):
        Node.__init__(self)

        self.content = string
        self.is_whitespace = (whitespace_regex.match(string) != None)

    def accept(self, visitor):
        visitor.visit_char(self)


class EndOfLine(Node):

    def __init__(self):
        Node.__init__(self)

    def accept(self, visitor):
        visitor.visit_eol(self)


