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


class ASTIterator():

    def prev(node):
        if node != node.parent[0]:
            node = node.parent[node.parent.index(node) - 1]
            while not node.is_leaf():
                node = node[-1]
            return node

        elif not node.parent.is_root():
            return node.parent

        return None

    def next(node):
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

    def prev_no_descent(node):
        if node != node.parent[0]:
            index = node.parent.index(node) - 1
            node = node.parent[index]

        elif not node.parent.is_root():
            node = node.parent

        return node

    def next_no_descent(node):
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

    def prev_in_parent(node):
        if node != node.parent[0]:
            index = node.parent.index(node) - 1
            return node.parent[index]
        return None

    def next_in_parent(node):
        if node != node.parent[-1]:
            index = node.parent.index(node) + 1
            return node.parent[index]
        return None


