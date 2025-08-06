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


class NodeTypeDB(object):

    def can_hold_cursor(node):
        return node.type != 'mathlist' and node.type != 'list' and node.type != 'root'

    def focus_on_click(node):
        return node.type in {'widget', 'placeholder'}

    def is_whitespace(node):
        return node.type == 'eol' or (node.type == 'char' and node.value.isspace())

    def is_subscript(node):
        if node.parent.type == 'root': return False

        if node.parent.parent.type == 'mathscript':
            return node.parent == node.parent.parent[0]
        return False

    def is_superscript(node):
        if node.parent.type == 'root': return False

        if node.parent.parent.type == 'mathscript':
            return node.parent == node.parent.parent[1]
        if node.parent.parent.type == 'mathroot':
            return node.parent == node.parent.parent[1]
        return False

    def in_fraction(node):
        if node.parent.type == 'root': return False
        return node.parent.parent.type == 'mathfraction'


