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

from lemma.services.node_type_db import NodeTypeDB
import lemma.services.timer as timer


class Root():

    def __init__(self):
        self.parent = None
        self.paragraphs = []
        self.type = 'root'

        paragraph = Paragraph()
        paragraph.append(Node('eol'))
        self.append(paragraph)

    def insert(self, offset, paragraph):
        self.paragraphs.insert(offset, paragraph)
        paragraph.set_parent(self)

    def append(self, paragraph):
        self.paragraphs.append(paragraph)
        paragraph.set_parent(self)

    def remove(self, paragraph):
        self.paragraphs.remove(paragraph)

    def remove_range(self, index_from, index_to):
        del(self.paragraphs[index_from:index_to])

    def index(self, paragraph):
        return self.paragraphs.index(paragraph)

    def get_position(self):
        return Position(*list())

    def __len__(self): return len(self.paragraphs)
    def __iter__(self): return self.paragraphs.__iter__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.paragraphs.__getitem__(key)
        else:
            return self.paragraphs.__getitem__(key)

    def ancestors(self):
        return []

    def __str__(self):
        return 'root'


class Paragraph():

    def __init__(self):
        self.parent = None
        self.children = []
        self.layout = None
        self.xml = None
        self.plaintext = None
        self.type = 'paragraph'

        self.style = 'p'
        self.indentation_level = 0
        self.state = None

    def invalidate(self):
        self.layout = None
        self.xml = None
        self.plaintext = None

    def set_parent(self, parent):
        self.parent = parent

    def insert(self, offset, node):
        self.children.insert(offset, node)
        node.set_parent(self)

    def append(self, node):
        self.children.append(node)
        node.set_parent(self)

    def remove(self, node):
        self.children.remove(node)

    def remove_range(self, index_from, index_to):
        del(self.children[index_from:index_to])

    def index(self, node):
        return self.children.index(node)

    def get_position(self):
        return Position(self.parent.index(self))

    def ancestors(self):
        return [node.parent]

    def is_first_in_parent(self):
        return self == self.parent[0]

    def is_last_in_parent(self):
        return self == self.parent[-1]

    def prev_in_parent(self):
        if not self.is_first_in_parent():
            index = self.parent.index(self) - 1
            return self.parent[index]
        return None

    def next_in_parent(self):
        if not self.is_last_in_parent():
            index = self.parent.index(self) + 1
            return self.parent[index]
        return None

    def __len__(self): return len(self.children)
    def __iter__(self): return self.children.__iter__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.children.__getitem__(key)
        else:
            return self.children.__getitem__(key)


class Node():

    def __init__(self, type_str, value=None):
        self.parent = None
        self.children = []
        self.type = type_str
        self.value = value
        self.tags = set()
        self.link = None
        self.layout = None

    def set_parent(self, parent):
        self.parent = parent

    def insert(self, offset, node):
        self.children.insert(offset, node)
        node.set_parent(self)

    def append(self, node):
        self.children.append(node)
        node.set_parent(self)

    def remove(self, node):
        self.children.remove(node)

    def remove_range(self, index_from, index_to):
        del(self.children[index_from:index_to])

    def index(self, node):
        return self.children.index(node)

    def get_position(self):
        node = self
        position = list()
        while not node.type == 'root':
            position.insert(0, node.parent.index(node))
            node = node.parent

        return Position(*position)

    def ancestors(self):
        node = self
        ancestors = []
        while not node.type == 'root':
            ancestors.insert(0, node.parent)
            node = node.parent

        return ancestors

    def is_first_in_parent(self):
        return self == self.parent[0]

    def is_last_in_parent(self):
        return self == self.parent[-1]

    def is_inside_link(self):
        if self.link == None: return False
        if self.is_first_in_parent(): return False
        return self.link == self.prev_in_parent().link

    def link_bounds(self):
        if self.link == None: return (None, None)
        if self.is_first_in_parent(): return (None, None)

        node1 = self
        node2 = self

        while node2 != None:
            next_node = node2.next_in_parent()
            if next_node != None and next_node.link == self.link:
                node2 = next_node
            else:
                if next_node != self and next_node != None:
                    node2 = next_node
                break
        while node1 != None:
            prev_node = node1.prev_in_parent()
            if prev_node != None and prev_node.link == self.link:
                node1 = prev_node
            else:
                break
        return (node1, node2)

    def word_bounds(self):
        if NodeTypeDB.is_whitespace(self): return (None, None)

        node1 = self
        node2 = self

        while node2 != None:
            next_node = node2.next_in_parent()
            if next_node == None:
                break
            elif NodeTypeDB.is_whitespace(next_node):
                node2 = next_node
                break
            else:
                node2 = next_node
        while node1 != None:
            prev_node = node1.prev_in_parent()
            if prev_node == None or NodeTypeDB.is_whitespace(prev_node):
                break
            else:
                node1 = prev_node
        return (node1, node2)

    def paragraph(self):
        node = self

        while not node.type == 'paragraph':
            node = node.parent

        return node

    def prev_in_parent(self):
        if not self.is_first_in_parent():
            index = self.parent.index(self) - 1
            return self.parent[index]
        return None

    def next_in_parent(self):
        if not self.is_last_in_parent():
            index = self.parent.index(self) + 1
            return self.parent[index]
        return None

    def first_in_parent(self):
        return self.parent[0]

    def last_in_parent(self):
        return self.parent[-1]

    def prev(self):
        node = self

        if not node.is_first_in_parent():
            node = node.parent[node.parent.index(node) - 1]
            while not len(node.children) == 0:
                node = node[-1]

        elif not node.parent.type == 'paragraph':
            node = node.parent

        elif not node.parent.is_first_in_parent():
            node = node.parent.prev_in_parent()[-1]

        if not NodeTypeDB.can_hold_cursor(node):
            return node.prev()

        return node

    def next(self):
        node = self

        if not len(node.children) == 0:
            node = node[0]

        else:
            while not node.type == 'paragraph' and node.parent.index(node) == len(node.parent) - 1:
                node = node.parent
            if not node.type == 'paragraph':
                node = node.parent[node.parent.index(node) + 1]
            elif not node.is_last_in_parent():
                node = node.next_in_parent()[0]
            else:
                node = node[-1]

        if not NodeTypeDB.can_hold_cursor(node):
            return node.next()

        return node

    def prev_no_descent(self):
        node = self

        if not node.is_first_in_parent():
            index = node.parent.index(node) - 1
            node = node.parent[index]

        elif not node.parent.type == 'paragraph':
            node = node.parent

        elif not node.parent.is_first_in_parent():
            node = node.parent.prev_in_parent()[-1]

        if not NodeTypeDB.can_hold_cursor(node):
            return node.prev_no_descent()

        return node

    def next_no_descent(self):
        node = self

        if not node.is_last_in_parent():
            index = node.parent.index(node) + 1
            node = node.parent[index]

        else:
            while not node.type == 'paragraph' and node.parent.index(node) == len(node.parent) - 1:
                node = node.parent
            if not node.type == 'paragraph':
                node = node.parent[node.parent.index(node) + 1]
            elif not node.is_last_in_parent():
                node = node.next_in_parent()[0]
            else:
                node = node[-1]

        if not NodeTypeDB.can_hold_cursor(node):
            return node.next_no_descent()

        return node

    def paragraph_bounds(self):
        return (self.paragraph_start(), self.paragraph_end())

    def paragraph_start(self):
        return self.paragraph()[0]

    def paragraph_end(self):
        return self.paragraph()[-1]

    def flatten(self):
        result = [self]
        for child in self.children:
            result += child.flatten()
        return result

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return self.children.__iter__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.children.__getitem__(key)
        else:
            return self.children.__getitem__(key)

    def __str__(self):
        string = self.type + ':' + str(self.value)
        return string


class Position(object):

    def __init__(self, *level_positions):
        self.level_positions = list(level_positions)

    def __str__(self): return self.level_positions.__str__()
    def __len__(self): return len(self.level_positions)
    def __iter__(self): return self.level_positions.__iter__()
    def __getitem__(self, key): return self.level_positions.__getitem__(key)
    def __eq__(self, other): return not self.__ne__(other)
    def __ne__(self, other): return other == None or self.__lt__(other) or self.__gt__(other)
    def __le__(self, other): return not self.__gt__(other)
    def __gt__(self, other): return other.__lt__(self)
    def __ge__(self, other): return not self.__lt__(other)

    def __lt__(self, other):
        if len(self) < len(other):
            for i in range(len(self)):
                if self[i] < other[i]: return True
                if self[i] > other[i]: return False
            return True
        if len(self) > len(other):
            for i in range(len(other)):
                if self[i] < other[i]: return True
                if self[i] > other[i]: return False
            return False
        else:
            for i in range(len(self)):
                if self[i] < other[i]: return True
                if self[i] > other[i]: return False
            return False


class Cursor():

    def __init__(self, document, node_insert=None, node_selection=None):
        self.document = document
        self.node_insert = node_insert
        self.node_selection = node_selection
        self.implicit_x_position = 0

    @timer.timer
    def set_insert_selection_nodes(self, node_insert, node_selection):
        self.node_insert = node_insert
        self.node_selection = node_selection
        self.restore_selection_invariant()

    def move_insert_to_node(self, node):
        if node != None:
            self.set_insert_selection_nodes(node, node)

    def move_insert_to_node_with_selection(self, node):
        if node != None:
            self.node_insert = node
            self.restore_selection_invariant()

    def set_state(self, position):
        self.node_insert = self.document.get_node_at_position(position[0])
        self.node_selection = self.document.get_node_at_position(position[1])

    def update_implicit_x_position(self, x):
        self.implicit_x_position = x

    @timer.timer
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

    @timer.timer
    def get_first_and_last_node(self):
        if self.get_insert_position() < self.get_selection_position():
            return (self.node_insert, self.node_selection)
        else:
            return (self.node_selection, self.node_insert)

    def has_selection(self):
        return self.get_insert_node() != self.get_selection_node()

    # restore the invariant that both the insert and the selection bound
    # have either the same parent or their parents are paragraphs.
    @timer.timer
    def restore_selection_invariant(self):

        # special cases where the invariant already holds
        if not self.has_selection(): return
        if self.node_insert.parent == self.node_selection.parent: return
        if self.node_insert.parent.type == 'paragraph' and self.node_selection.parent.type == 'paragraph': return

        first_node, last_node = self.get_first_and_last_node()

        # compute the smallest common ancestor of both the insert and the selection node.
        ancestors = list(zip(first_node.ancestors() + [first_node], last_node.ancestors() + [last_node]))

        common_ancestors_and_their_children = list()
        for (node_1, node_2) in ancestors:
            if node_1.type == 'root' or node_1.parent.type in ['root', 'paragraph'] or node_1.parent == node_2.parent and NodeTypeDB.can_hold_cursor(node_1):
                common_ancestors_and_their_children.append((node_1, node_2))
            else:
                break

        # compute the new positions
        pos1, pos2 = first_node.get_position(), last_node.get_position()
        ancestor_1_pos = pos1[:len(common_ancestors_and_their_children) - 2]
        ancestor_2_pos = pos2[:len(common_ancestors_and_their_children) - 2]

        if len(pos1) > len(ancestor_1_pos) + 1:
            pos1 = pos1[:len(ancestor_1_pos) + 1]
        if len(pos2) > len(ancestor_2_pos) + 1:
            pos2 = pos2[:len(ancestor_2_pos) + 1]
            pos2[-1] += 1

        # move both insert and selection bound to either a common ancestor or a paragraph
        if self.get_insert_node() == first_node:
            self.node_insert = self.document.get_node_at_position(pos1)
            self.node_selection = self.document.get_node_at_position(pos2)
        else:
            self.node_insert = self.document.get_node_at_position(pos2)
            self.node_selection = self.document.get_node_at_position(pos1)


