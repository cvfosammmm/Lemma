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


class Cursor():

    def __init__(self, document, node=None):
        self.document = document
        self.node = node

    def set_node(self, node):
        self.node = node

    def get_node(self):
        return self.node

    def set_position(self, position):
        node = self.document.lines

        for index in position:
            node = node.get_child(index)
        self.node = node

    def get_position(self):
        position = list()
        node = self.node
        while not node.parent.is_root():
            position.insert(0, node.parent.get_index(node))
            node = node.parent

        return position


