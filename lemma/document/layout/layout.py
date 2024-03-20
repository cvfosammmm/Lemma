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

from lemma.app.font_manager import FontManager


class BoxVContainer(object):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.classes = set()

        self.parent = None
        self.children = list()

    def add(self, child):
        self.children.append(child)
        self.height += child.height
        self.width = max(child.width, self.width)
        child.set_parent(self)

    def insert(self, position, child):
        self.children.insert(position, child)
        self.height = max(child.height, self.height)
        self.width += child.width
        child.set_parent(self)

    def get_xy_at_child(self, box):
        x = 0
        y = 0
        for child in self.children:
            if child == box:
                break
            y += child.height
        return (x, y)

    def get_child_at_xy(self, x, y):
        current_child, current_height = (None, 0)

        for child in self.children:
            current_child = child
            current_height += child.height
            if current_height >= y:
                current_height -= child.height
                break

        return (current_child, 0, current_height)

    def set_parent(self, parent): self.parent = parent
    def is_leaf(self): return False
    def get_node(self): return None


class BoxHContainer(object):

    def __init__(self):
        self.width = 0
        self.height = FontManager.get_line_height()
        self.classes = set()

        self.parent = None
        self.children = list()

    def add(self, child):
        self.children.append(child)
        self.height = max(child.height, self.height)
        self.width += child.width
        child.set_parent(self)

    def insert(self, position, child):
        self.children.insert(position, child)
        self.height = max(child.height, self.height)
        self.width += child.width
        child.set_parent(self)

    def get_xy_at_child(self, box):
        x = 0
        y = 0
        for child in self.children:
            if child == box:
                break
            x += child.width
        return (x, y)

    def get_child_at_xy(self, x, y):
        current_child, current_width = (None, 0)

        for child in self.children:
            current_child = child
            current_width += child.width
            if current_width >= x:
                current_width -= child.width
                break

        return (current_child, current_width, 0)

    def set_parent(self, parent): self.parent = parent
    def is_leaf(self): return False
    def get_node(self): return None


class BoxGlyph(object):

    def __init__(self, width, height, left, top, char, node=None):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.classes = set()

        self.parent = None
        self.char = char
        self.node = node

    def set_parent(self, parent): self.parent = parent
    def is_leaf(self): return True
    def get_node(self): return self.node


class BoxEmpty(object):

    def __init__(self, node=None):
        self.width = 0
        self.height = 0
        self.left = 0
        self.top = 0
        self.classes = set()

        self.parent = None
        self.node = node

    def set_parent(self, parent): self.parent = parent
    def is_leaf(self): return True
    def get_node(self): return self.node


class BoxPlaceholder(object):

    def __init__(self, width, height, left, top, node=None):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.classes = set()

        self.parent = None
        self.char = '•'
        self.node = node

    def set_parent(self, parent): self.parent = parent
    def is_leaf(self): return True
    def get_node(self): return self.node


