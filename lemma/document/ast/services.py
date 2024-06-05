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

from lemma.document.ast.iterator import ASTIterator


def node_inside_link(node):
    if node.link == None: return False
    if node.is_first_in_parent(): return False

    return node.link == ASTIterator.prev_in_parent(node).link


def get_bounds_for_link_at_node(node):
    if node.link == None: return (None, None)
    if node.is_first_in_parent(): return (None, None)

    node1 = node
    node2 = node

    while node2.link == node.link:
        next_node = ASTIterator.next_in_parent(node2)
        if next_node != None:
            node2 = next_node
        else:
            break
    while node1.link == node.link:
        prev_node = ASTIterator.prev_in_parent(node1)
        if prev_node != None:
            node1 = prev_node
        else:
            break

    return (node1.get_position(), node2.get_position())


