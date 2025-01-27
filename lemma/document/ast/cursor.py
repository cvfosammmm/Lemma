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

    def __init__(self, document, node_insert=None, node_selection=None):
        self.document = document
        self.node_insert = node_insert
        self.node_selection = node_selection
        self.implicit_x_position = 0

    def set_insert_node(self, node):
        self.node_insert = node

    def set_selection_node(self, node):
        self.node_selection = node

    def set_insert_selection_nodes(self, node_insert, node_selection):
        self.node_insert = node_insert
        self.node_selection = node_selection

    def set_insert_position(self, position):
        self.set_insert_node(self.document.ast.get_node_at_position(position))

    def set_selection_position(self, position):
        self.set_selection_node(self.document.ast.get_node_at_position(position))

    def update_implicit_x_position(self):
        x, y = self.get_insert_node().layout.get_absolute_xy()
        self.implicit_x_position = x

    def prev(self, node):
        if not node.is_first_in_parent():
            node = node.parent[node.parent.index(node) - 1]
            while not len(node.children) == 0:
                node = node[-1]

        elif not node.parent.is_root():
            node = node.parent

        if not node.can_hold_cursor():
            return self.prev(node)

        return node

    def next(self, node):
        if not len(node.children) == 0:
            node = node[0]

        else:
            while not node.is_root() and node.parent.index(node) == len(node.parent) - 1:
                node = node.parent
            if not node.is_root():
                node = node.parent[node.parent.index(node) + 1]
            else:
                node = node[-1]

        if not node.can_hold_cursor():
            return self.next(node)

        return node

    def prev_no_descent(self, node):
        if node != node.parent[0]:
            index = node.parent.index(node) - 1
            node = node.parent[index]

        elif not node.parent.is_root():
            node = node.parent

        if not node.can_hold_cursor():
            return self.prev_no_descent(node)

        return node

    def next_no_descent(self, node):
        if node != node.parent[-1]:
            index = node.parent.index(node) + 1
            node = node.parent[index]

        else:
            while not node.is_root() and node.parent.index(node) == len(node.parent) - 1:
                node = node.parent
            if not node.is_root():
                node = node.parent[node.parent.index(node) + 1]
            else:
                node = node[-1]

        if not node.can_hold_cursor():
            return self.next_no_descent(node)

        return node

    def move_insert_to_node(self, node):
        if node != None:
            self.set_insert_selection_nodes(node, node)

    def move_selection_bound_to_node(self, node):
        if node != None:
            self.set_selection_node(node)

    def move_insert_to_node_with_selection(self, node):
        if node != None:
            self.set_insert_node(node)
            self.restore_selection_invariant()

    def set_state(self, position):
        self.set_insert_position(position[0])
        self.set_selection_position(position[1])

    def get_state(self):
        return [self.get_insert_position(), self.get_selection_position()]

    def get_insert_node(self):
        return self.node_insert

    def get_selection_node(self):
        return self.node_selection

    def get_insert_position(self):
        return self.node_insert.get_position()

    def get_selection_position(self):
        return self.node_selection.get_position()

    def get_first_node(self):
        if self.get_insert_position() < self.get_selection_position():
            return self.node_insert
        else:
            return self.node_selection

    def get_last_node(self):
        if self.get_insert_position() < self.get_selection_position():
            return self.node_selection
        else:
            return self.node_insert

    def get_first_cursor_pos(self):
        if self.get_insert_position() < self.get_selection_position():
            return self.get_insert_position()
        else:
            return self.get_selection_position()

    def get_last_cursor_pos(self):
        if self.get_insert_position() < self.get_selection_position():
            return self.get_selection_position()
        else:
            return self.get_insert_position()

    def has_selection(self):
        return self.get_insert_node() != self.get_selection_node()

    # restore the invariant that both the insert and the selection bound have the same parent.
    def restore_selection_invariant(self):

        # special cases where the invariant already holds
        if not self.has_selection(): return
        if self.node_insert.parent == self.node_selection.parent: return

        # compute the smallest common ancestor of both the insert and the selection node.
        ancestors = list(zip(self.node_insert.ancestors() + [self.node_insert], self.node_selection.ancestors() + [self.node_selection]))
        common_ancestors_and_their_children = [(node_1, node_2) for (node_1, node_2) in list(ancestors) if node_1.parent == node_2.parent or node_1.is_root()]

        # if the children of the sca can't hold the cursor, go up some more
        for node_1, node_2 in reversed(common_ancestors_and_their_children):
            if node_1.can_hold_cursor() and node_2.can_hold_cursor():
                sca = node_1.parent
                break

        # compute the new positions
        sca_pos = sca.get_position()
        pos1, pos2 = self.get_selection_position(), self.get_insert_position()
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        if len(pos1) > len(sca_pos) + 1:
            pos1 = pos1[:len(sca_pos) + 1]
        if len(pos2) > len(sca_pos) + 1:
            pos2 = pos2[:len(sca_pos) + 1]
            pos2[-1] += 1

        # move both insert and selection bound to the sca
        if self.get_insert_position() < self.get_selection_position():
            self.set_insert_position(pos1)
            self.set_selection_position(pos2)
        else:
            self.set_insert_position(pos2)
            self.set_selection_position(pos1)


