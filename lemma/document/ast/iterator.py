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


class Iterator():

    def __init__(self, node):
        self.current_node = node

    def prev(self):
        node = self.current_node
        while not node.is_root() and node.parent.get_index(node) == 0:
            node = node.parent

        if node.is_root(): return False

        node = node.parent.get_child(node.parent.get_index(node) - 1)

        while not node.is_leaf():
            node = node.get_child(-1)

        self.current_node = node

    def next(self):
        node = self.current_node
        while not node.is_root() and node.parent.get_index(node) == node.parent.length() - 1:
            node = node.parent

        if node.is_root(): return False

        node = node.parent.get_child(node.parent.get_index(node) + 1)

        while not node.is_leaf():
            node = node.get_child(0)

        self.current_node = node

    def prev_in_current_parent(self):
        node = self.current_node
        index = node.parent.get_index(node) - 1
        while not node.parent.get_child(index).is_leaf():
            index -= 1

        self.current_node = node.parent.get_child(index)

    def next_in_current_parent(self):
        node = self.current_node
        index = node.parent.get_index(node) + 1
        while not node.parent.get_child(index).is_leaf():
            index += 1

        self.current_node = node.parent.get_child(index)

    def get_node(self):
        return self.current_node

    def get_position(self):
        position = list()
        node = self.current_node
        while not node.is_root():
            position.insert(0, node.parent.get_index(node))
            node = node.parent

        return position

    def is_first_in_parent(self):
        return self.current_node == self.current_node.parent.get_child(0)

    def is_last_in_parent(self):
        return self.current_node == self.current_node.parent.get_child(-1)


