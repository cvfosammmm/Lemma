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


class Node():

    def __init__(self, type_str, value=None):
        self.parent = None
        self.children = []
        self.type = type_str
        self.value = value
        self.tags = set()
        self.link = None
        self.paragraph_style = 'p'
        self.layout = None

    def set_parent(self, parent):
        self.parent = parent

    def insert(self, index, node):
        self.children.insert(index, node)
        node.set_parent(self)

    def insert_before(self, child, node):
        index = self.index(child)
        self.insert(index, node)

    def append(self, node):
        self.insert(len(self.children), node)

    def remove(self, node):
        self.children.remove(node)
        node.set_parent(None)

    def remove_range(self, first_node, last_node):
        index_1 = self.index(first_node)
        index_2 = self.index(last_node)
        nodes = self.children[index_1:index_2]
        del(self.children[index_1:index_2])
        for node in nodes:
            node.set_parent(None)

        return nodes

    def remove_from_parent(self):
        self.parent.remove(self)

    def index(self, node):
        return self.children.index(node)

    def get_position(self):
        node = self
        position = list()
        while not node.is_root():
            position.insert(0, node.parent.index(node))
            node = node.parent

        return Position(*position)

    def get_paragraph_style(self):
        node = self
        while not node.parent.is_root():
            node = node.parent
        return node.paragraph_style

    def copy(self):
        node = Node(self.type, self.value)
        node.tags = self.tags
        node.link = self.link
        node.children = self.children
        return node

    def get_subtree(self, pos1, pos2):
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        parent = self.get_node_at_position(pos1[:-1])

        return parent[pos1[-1]:pos2[-1]]

    def __len__(self): return len(self.children)
    def __iter__(self): return self.children.__iter__()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.children.__getitem__(key)
        else:
            return self.children.__getitem__(key)

    def ancestors(self):
        node = self
        ancestors = []
        while not node.is_root():
            ancestors.insert(0, node.parent)
            node = node.parent

        return ancestors

    def is_eol(self): return self.type == 'eol'
    def is_end(self): return self.type == 'end'
    def is_whitespace(self): return self.type == 'eol' or (self.is_char() and self.value.isspace())
    def is_symbol(self): return self.type == 'char' and not self.is_whitespace()
    def is_char(self): return self.type == 'char'
    def is_placeholder(self): return self.type == 'placeholder'
    def is_widget(self): return self.type == 'widget'
    def is_mathscript(self): return self.type == 'mathscript'
    def is_mathfraction(self): return self.type == 'mathfraction'
    def is_mathroot(self): return self.type == 'mathroot'
    def is_mathlist(self): return self.type == 'mathlist'
    def can_hold_cursor(self): return self.type != 'mathlist' and self.type != 'list' and self.type != 'root'
    def focus_on_click(self): return self.type in {'widget', 'placeholder'}
    def is_leaf(self): return self.type in {'char', 'widget', 'placeholder', 'eol', 'end'}
    def is_first_in_parent(self): return self == self.parent[0]
    def is_last_in_parent(self): return self == self.parent[-1]
    def is_root(self): return self.parent == None
    def is_subscript(self):
        if self.parent.is_root(): return False

        if self.parent.parent.is_mathscript():
            return self.parent == self.parent.parent[0]
        return False
    def is_superscript(self):
        if self.parent.is_root(): return False

        if self.parent.parent.is_mathscript():
            return self.parent == self.parent.parent[1]
        if self.parent.parent.is_mathroot():
            return self.parent == self.parent.parent[1]
        return False
    def in_fraction(self):
        if self.parent.is_root(): return False
        return self.parent.parent.is_mathfraction()

    def is_first_in_line(self):
        if not self.parent.is_root(): return False
        if self.is_first_in_parent(): return True
        if self.prev_in_parent().is_eol(): return True

        return False

    def is_last_in_line(self):
        if not self.parent.is_root(): return False
        if self.is_last_in_parent(): return True
        if self.is_eol(): return True

        return False

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
        if self.is_whitespace(): return (None, None)

        node1 = self
        node2 = self

        while node2 != None:
            next_node = node2.next_in_parent()
            if next_node == None:
                break
            elif next_node.is_whitespace():
                node2 = next_node
                break
            else:
                node2 = next_node
        while node1 != None:
            prev_node = node1.prev_in_parent()
            if prev_node == None or prev_node.is_whitespace():
                break
            else:
                node1 = prev_node
        return (node1, node2)

    def line_bounds(self):
        return (self.line_start(), self.line_end())

    def prev_in_parent(self, steps=1):
        if self != self.parent[0]:
            index = self.parent.index(self) - steps
            return self.parent[index]
        return None

    def next_in_parent(self, steps=1):
        if self != self.parent[-1]:
            index = self.parent.index(self) + steps
            return self.parent[index]
        return None

    def flatten(self):
        result = [self]
        for child in self.children:
            result += child.flatten()
        return result

    def line_start(self):
        node = self

        while not node.parent.is_root():
            node = node.parent

        while not node.is_first_in_line():
            node = node.prev_in_parent()

        return node

    def line_end(self):
        node = self

        while not node.parent.is_root():
            node = node.parent

        while not node.is_last_in_line():
            node = node.next_in_parent()

        return node

    def get_node_at_position(self, pos):
        node = self
        for index in pos:
            node = node[index]
        return node

    def get_link_bounds_and_targets(self):
        current_target = None
        current_bounds = [None, None]
        result = list()
        for node in self:
            current_bounds[1] = node
            if current_target != node.link:
                if current_bounds[0] != None and current_target != None:
                    result.append([[current_bounds[0], current_bounds[1]], current_target])
                current_bounds[0] = node
            current_target = node.link
        if current_bounds[0] != None and current_target != None:
            result.append([[current_bounds[0], current_bounds[1]], current_target])

        return result

    def __str__(self):
        string = self.type + ':' + str(self.value)
        return string

    def validate(self):
        if self.type == 'root':
            return all([child.type in {'char', 'placeholder', 'eol', 'widget', 'mathscript', 'mathfraction', 'mathroot'} for child in self.children]) \
                and all([child.validate() for child in self.children])

        if self.type == 'mathscript':
            return len(self.children) == 2 \
                and all([child.type == 'mathlist' for child in self.children]) \
                and all([child.validate() for child in self.children])

        if self.type == 'mathfraction':
            return len(self.children) == 2 \
                and all([child.type == 'mathlist' for child in self.children]) \
                and all([child.validate() for child in self.children])

        if self.type == 'mathroot':
            return len(self.children) == 2 \
                and all([child.type == 'mathlist' for child in self.children]) \
                and all([child.validate() for child in self.children])

        if self.type == 'mathlist':
            return len(self.children) == 0 \
                or all([child.type in {'char', 'placeholder', 'end'} for child in self.children]) \
                and all([child.validate() for child in self.children])

        if self.type in {'char', 'widget', 'placeholder', 'eol', 'end'}:
            return len(self.children) == 0


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
        self.node_insert = self.document.ast.get_node_at_position(position[0])
        self.node_selection = self.document.ast.get_node_at_position(position[1])

    def update_implicit_x_position(self, x):
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
            self.node_insert = self.document.ast.get_node_at_position(pos1)
            self.node_selection = self.document.ast.get_node_at_position(pos2)
        else:
            self.node_insert = self.document.ast.get_node_at_position(pos2)
            self.node_selection = self.document.ast.get_node_at_position(pos1)


