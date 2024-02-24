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
        parent = self.current_node.parent
        index = parent.get_index(self.current_node)
        if index > 0:
            self.current_node = parent.get_child(index - 1)
        else:
            if parent.parent.get_child(0) == parent:
                return False
            else:
                index = parent.parent.get_index(parent)
                self.current_node = parent.parent.get_child(index - 1).get_child(-1)
        return True

    def next(self):
        parent = self.current_node.parent
        index = parent.get_index(self.current_node)
        if index < parent.length() - 1:
            self.current_node = parent.get_child(index + 1)
        else:
            if parent.parent.get_child(-1) == parent:
                return False
            else:
                index = parent.parent.get_index(parent)
                self.current_node = parent.parent.get_child(index + 1).get_child(0)
        return True

    def get_node(self):
        return self.current_node

    def starts_line(self):
        line = self.get_line()
        return (line.length() > 0 and line.get_child(0) == self.current_node)

    def ends_line(self):
        line = self.get_line()
        return (line.length() > 0 and line.get_child(-1) == self.current_node)

    def get_line(self):
        node = self.current_node
        while node.parent.parent != None:
            node = node.parent
        return node


