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
            while not node.is_root() and node.parent.index(node) == node.parent.length() - 1:
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
            while not node.is_root() and node.parent.index(node) == node.parent.length() - 1:
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


def position_less_than(pos1, pos2):
    if len(pos1) < len(pos2):
        for i in range(len(pos1)):
            if pos1[i] < pos2[i]: return True
            if pos1[i] > pos2[i]: return False
        return True
    if len(pos1) > len(pos2):
        for i in range(len(pos2)):
            if pos1[i] < pos2[i]: return True
            if pos1[i] > pos2[i]: return False
        return False
    else:
        for i in range(len(pos1)):
            if pos1[i] < pos2[i]: return True
            if pos1[i] > pos2[i]: return False
        return False


def sort_positions(pos1, pos2):
    if position_less_than(pos2, pos1):
        return (pos2, pos1)
    else:
        return (pos1, pos2)


def position_to_node(pos, root_node):
    node = root_node

    for index in pos:
        node = node[index]
    return node


def node_to_position(node):
    position = list()
    while not node.is_root():
        position.insert(0, node.parent.index(node))
        node = node.parent

    return position


def node_to_char(node):
    if not node.is_char(): return None

    if node.type == 'EOL': return '\n'
    else: return node.value


def flatten(list_of_nodes):
    def append(flatlist, node):
        flatlist.append(node)
        for child in node:
            append(flatlist, child)

    flatlist = []
    for node in list_of_nodes:
        append(flatlist, node)
    return flatlist


def insert_inside_link_no_selection(document):
    ins = document.ast.get_insert_node()
    prev = ASTIterator.prev_in_parent(ins)
    return prev != None and prev.link != None and ins.link == prev.link


def node_inside_link(node):
    if node.link == None: return False
    if node.is_first_in_parent(): return False

    return node.link == ASTIterator.prev_in_parent(node).link


def get_link_bounds_by_node(node):
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

    return (node_to_position(node1), node_to_position(node2))


