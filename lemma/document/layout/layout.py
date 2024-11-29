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


class Box(object):

    def __init__(self, box_type, width=0, height=0, left=0, top=0, node=None):
        self.type = box_type
        self.width = width
        self.height = height
        self.left = left
        self.top = top

        self.parent = None
        self.children = list()

        self.classes = set()
        self.node = node

    def add(self, child):
        self.children.append(child)
        child.set_parent(self)
        self.update_size(child)

    def insert(self, position, child):
        self.children.insert(position, child)
        child.set_parent(self)
        self.update_size(child)

    def update_size(self, new_child):
        if self.is_vertical():
            self.height += new_child.height
            self.width = max(new_child.width, self.width)
        else:
            self.height = max(new_child.height, self.height)
            self.width += new_child.width

    def get_xy_at_child(self, box):
        x = 0
        y = 0
        for child in self.children:
            if child == box:
                break
            if self.is_vertical():
                y += child.height
            else:
                x += child.width
        return (x, y)

    def get_node_at_xy(self, x, y):
        x = max(0, min(self.width, x))
        if y > self.height: x = self.width
        y = max(0, min(self.height, y))

        x_offset, y_offset = (0, 0)
        if not self.is_leaf():
            box, x_offset, y_offset = self.get_child_at_xy(x, y)
            x -= x_offset
            y -= y_offset
            return box.get_node_at_xy(x, y)

        else:
            node = self.get_node()
            if x > self.width / 2 and x < self.width:
                x_self, y_self = self.parent.get_xy_at_child(self)
                return self.parent.get_node_at_xy(x_self + self.width, y_self + y)
            return node

    def get_link_at_xy(self, x, y):
        box = self.get_leaf_at_xy(x, y)

        if box != None:
            return box.get_node().link
        else:
            return None

    def get_leaf_at_xy(self, x, y):
        x_offset, y_offset = (0, 0)
        if not self.is_leaf():
            if y > self.height or y < 0 or x > self.width or x < 0: return None

            box, x_offset, y_offset = self.get_child_at_xy(x, y)
            x -= x_offset
            y -= y_offset
            return box.get_leaf_at_xy(x, y)

        else:
            if y > self.parent.height or y < self.parent.height - self.height or x > self.width or x < 0: return None

            return self

    def get_child_at_xy(self, x, y):
        if self.is_vertical():
            current_child, current_height = (None, 0)

            for child in self.children:
                current_child = child
                if current_height + child.height <= y:
                    current_height += child.height
                else:
                    break
            return (current_child, 0, current_height)

        else:
            current_child, current_width = (None, 0)

            for child in self.children:
                current_child = child
                if current_width == x:
                    break
                elif current_width + child.width <= x:
                    current_width += child.width
                else:
                    break
            return (current_child, current_width, 0)

    def set_parent(self, parent): self.parent = parent
    def is_vertical(self): return self.type == 'vcontainer'
    def is_leaf(self): return len(self.children) == 0
    def get_node(self): return self.node

    def __str__(self):
        string = self.type + '\n  '
        for box in self.children:
            string += box.__str__()

        return string


