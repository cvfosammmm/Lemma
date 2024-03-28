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

        if node != node.parent.get_child(0):
            node = node.parent.get_child(node.parent.get_index(node) - 1)
            while not node.is_leaf():
                node = node.get_child(-1)

        elif not node.parent.is_root():
            node = node.parent

        self.current_node = node

    def next(self):
        node = self.current_node

        if not node.is_leaf():
            node = node.get_child(0)
        else:
            while not node.is_root() and node.parent.get_index(node) == node.parent.length() - 1:
                node = node.parent
            if node.is_root():
                return
            else:
                node = node.parent.get_child(node.parent.get_index(node) + 1)

        self.current_node = node

    def prev_no_descent(self):
        node = self.current_node

        if node != node.parent.get_child(0):
            index = node.parent.get_index(node) - 1
            node = node.parent.get_child(index)

        elif not node.parent.is_root():
            node = node.parent

        self.current_node = node

    def next_no_descent(self):
        node = self.current_node

        if node != node.parent.get_child(-1):
            index = node.parent.get_index(node) + 1
            node = node.parent.get_child(index)

        else:
            while not node.is_root() and node.parent.get_index(node) == node.parent.length() - 1:
                node = node.parent
            if node.is_root():
                return
            else:
                node = node.parent.get_child(node.parent.get_index(node) + 1)

        self.current_node = node

    def get_node(self):
        return self.current_node

    def get_position(self):
        position = list()
        node = self.current_node
        while not node.is_root():
            position.insert(0, node.parent.get_index(node))
            node = node.parent

        return position

    def get_ancestors(self):
        node = self.current_node
        ancestors = [node]
        while not node.is_root():
            ancestors.insert(0, node.parent)
            node = node.parent

        return ancestors

    def is_first_in_parent(self):
        return self.current_node == self.current_node.parent.get_child(0)

    def is_last_in_parent(self):
        return self.current_node == self.current_node.parent.get_child(-1)


