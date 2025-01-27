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


class Layout():

    def __init__(self):
        pass

    def get_absolute_xy(self):
        layout = self
        x, y = (0, 0)

        while not layout.parent == None:
            x += layout.x
            y += layout.y
            layout = layout.parent

        return x, y

    def flatten(self):
        result = [self]
        for child in self.children:
            result += child.flatten()
        return result

    def get_ancestors(self):
        ancestors = []
        node = self
        while node.parent != None:
            ancestors.append(node.parent)
            node = node.parent
        return ancestors


