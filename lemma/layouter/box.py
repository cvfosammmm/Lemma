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

        self.children = list()

    def add(self, child):
        self.children.append(child)
        self.height += child.height
        self.width = max(child.width, self.width)

    def insert(self, position, child):
        self.children.insert(position, child)
        self.height = max(child.height, self.height)
        self.width += child.width

    def get_node(self): return None


class BoxHContainer(object):

    def __init__(self):
        self.width = 0
        self.height = FontManager.line_height

        self.children = list()

    def add(self, child):
        self.children.append(child)
        self.height = max(child.height, self.height)
        self.width += child.width

    def insert(self, position, child):
        self.children.insert(position, child)
        self.height = max(child.height, self.height)
        self.width += child.width

    def get_node(self): return None


class BoxGlyph(object):

    def __init__(self, width, height, left, top, char, node=None):
        self.width = width
        self.height = height
        self.left = left
        self.top = top

        self.char = char
        self.node = node
        self.is_selected = False

    def get_node(self): return self.node


class BoxInsert(object):

    def __init__(self, height, top):
        self.width = 0
        self.height = height
        self.left = 0
        self.top = top

    def get_node(self): return None


class BoxOther(object):

    def __init__(self, width, height, left, top, node=None):
        self.width = width
        self.height = height
        self.left = left
        self.top = top

        self.node = node

    def get_node(self): return self.node


