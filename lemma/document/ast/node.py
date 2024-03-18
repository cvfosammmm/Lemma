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

from lemma.document.ast.iterator import Iterator


class Root():

    def __init__(self):
        self.children = []

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

    def accept(self, visitor): visitor.visit_root(self)
    def is_leaf(self): return False
    def is_root(self): return True
    def is_line(self): return False
    def is_math_area(self): return False


class Line():

    def __init__(self):
        self.parent = None
        self.children = []
        self.insert(0, EndOfLine())

    def set_parent(self, parent):
        self.parent = parent

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

    def split(self, separating_child):
        part_1 = Line()
        part_2 = Line()

        current_part = part_1
        for child in self.children:
            if child == separating_child:
                current_part = part_2
            if child != self.get_child(-1):
                current_part.append(child)

        return (part_1, part_2)

    def add(self, line):
        for child in line.children:
            if child != line.get_child(-1):
                self.append(child)

    def accept(self, visitor): visitor.visit_line(self)
    def is_leaf(self): return False
    def is_root(self): return False
    def is_line(self): return True
    def is_math_area(self): return False


class BeforeMathArea():

    def __init__(self):
        self.parent = None
        self.box = None

    def set_parent(self, parent):
        self.parent = parent

    def set_box(self, box):
        self.box = box

    def get_iterator(self):
        return Iterator(self)

    def accept(self, visitor): visitor.visit_beforemath(self)
    def is_leaf(self): return True
    def is_root(self): return False
    def is_line(self): return False
    def is_math_area(self): return False


class MathArea():

    def __init__(self):
        self.parent = None
        self.children = []
        self.insert(0, EndOfMathArea())

    def set_parent(self, parent):
        self.parent = parent

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

    def split(self, separating_child):
        part_1 = Line()
        part_2 = Line()

        current_part = part_1
        for child in self.children:
            if child == separating_child:
                current_part = part_2
            if child != self.get_child(-1):
                current_part.append(child)

        return (part_1, part_2)

    def add(self, line):
        for child in line.children:
            if child != line.get_child(-1):
                self.append(child)

    def accept(self, visitor): visitor.visit_matharea(self)
    def is_leaf(self): return False
    def is_root(self): return False
    def is_line(self): return False
    def is_math_area(self): return True


class EndOfMathArea():

    def __init__(self):
        self.parent = None
        self.box = None

    def set_parent(self, parent):
        self.parent = parent

    def set_box(self, box):
        self.box = box

    def get_iterator(self):
        return Iterator(self)

    def accept(self, visitor): visitor.visit_aftermath(self)
    def is_leaf(self): return True
    def is_root(self): return False
    def is_line(self): return False
    def is_math_area(self): return False


class MathSymbol():

    def __init__(self, string):
        self.parent = None
        self.content = string
        self.box = None

    def set_parent(self, parent):
        self.parent = parent

    def set_box(self, box):
        self.box = box

    def get_iterator(self):
        return Iterator(self)

    def accept(self, visitor): visitor.visit_mathsymbol(self)
    def is_leaf(self): return True
    def is_root(self): return False
    def is_line(self): return False
    def is_math_area(self): return False


class UnicodeCharacter():

    def __init__(self, string):
        self.parent = None
        self.content = string
        self.is_whitespace = (whitespace_regex.match(string) != None)
        self.box = None

    def set_parent(self, parent):
        self.parent = parent

    def set_box(self, box):
        self.box = box

    def get_iterator(self):
        return Iterator(self)

    def accept(self, visitor): visitor.visit_char(self)
    def is_leaf(self): return True
    def is_root(self): return False
    def is_line(self): return False
    def is_math_area(self): return False


class EndOfLine():

    def __init__(self):
        self.parent = None
        self.box = None

    def set_parent(self, parent):
        self.parent = parent

    def set_box(self, box):
        self.box = box

    def get_iterator(self):
        return Iterator(self)

    def accept(self, visitor): visitor.visit_eol(self)
    def is_leaf(self): return True
    def is_root(self): return False
    def is_line(self): return False
    def is_math_area(self): return False


