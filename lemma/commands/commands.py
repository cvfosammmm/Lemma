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

import os.path
from lemma.ast.node import *


class SetTitle():

    def __init__(self, new_title):
        self.new_title = new_title
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['prev_title'] = document.title
        document.title = self.new_title

    def undo(self, document):
        document.title = self.state['prev_title']


class PopulateFromPath():

    def __init__(self, path):
        self.path = path
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True

    def run(self, document):
        document.last_modified = os.path.getmtime(self.path)
        document_lines = Lines()

        with open(self.path, 'r') as file:
            for line in file:
                if document.title == '' and line.startswith('# '):
                    document.title = line[1:].strip()
                else:
                    document_line = Line()
                    for char in line:
                        if char != '\n':
                            document_line.append(UnicodeCharacter(char))
                    document_lines.append(document_line)

        if document_lines.length() == 0: document_lines.append(Line())

        document.lines = document_lines
        document.insert.set_position([0, 0])

    def undo(self, document):
        pass


class Click():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['previous_cursor_position'] = document.insert.get_position()

        document.insert.set_node(document.get_node_at_xy(self.x, self.y))

    def undo(self, document):
        document.insert.set_position(self.state['previous_cursor_position'])


class Left():

    def __init__(self, offset):
        self.offset = -offset
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['offset_moved'] = document.move_cursor_by_offset(self.offset)

    def undo(self, document):
        document.move_cursor_by_offset(-self.state['offset_moved'])


class Right():

    def __init__(self, offset):
        self.offset = offset
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['offset_moved'] = document.move_cursor_by_offset(self.offset)

    def undo(self, document):
        document.move_cursor_by_offset(-self.state['offset_moved'])


class Up():

    def __init__(self):
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['previous_cursor_position'] = document.insert.get_position()

        x, y = document.get_xy_at_node(document.insert.get_node())
        if document.implicit_x_position != None:
            x = document.implicit_x_position
        if y == 0:
            document.insert.set_node(document.get_node_at_xy(0, 0))
        else:
            document.insert.set_node(document.get_node_at_xy(x, y - 1))

    def undo(self, document):
        document.insert.set_position(self.state['previous_cursor_position'])


class Down():

    def __init__(self):
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['previous_cursor_position'] = document.insert.get_position()

        x, y = document.get_xy_at_node(document.insert.get_node())
        if document.implicit_x_position != None:
            x = document.implicit_x_position
        document.insert.set_node(document.get_node_at_xy(x, y + document.insert.get_node().box.parent.height))

    def undo(self, document):
        document.insert.set_position(self.state['previous_cursor_position'])


class LineStart():

    def __init__(self):
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['previous_cursor_position'] = document.insert.get_position()

        x, y = document.get_xy_at_node(document.insert.get_node())
        document.insert.set_node(document.get_node_at_xy(0, y))

    def undo(self, document):
        document.insert.set_position(self.state['previous_cursor_position'])


class LineEnd():

    def __init__(self):
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['previous_cursor_position'] = document.insert.get_position()

        x, y = document.get_xy_at_node(document.insert.get_node())
        document.insert.set_node(document.get_node_at_xy(document.layout.width, y))

    def undo(self, document):
        document.insert.set_position(self.state['previous_cursor_position'])


class Return():

    def __init__(self):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True

    def run(self, document):
        document.insert_text_at_cursor('\n')

    def undo(self, document):
        document.move_cursor_by_offset(-1)
        document.delete_char_at_cursor()


class IMCommit():

    def __init__(self, text):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.text = text

    def run(self, document):
        document.insert_text_at_cursor(self.text)

    def undo(self, document):
        for char in reversed(self.text):
            document.move_cursor_by_offset(-1)
            document.delete_char_at_cursor()


class Delete():

    def __init__(self):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        line = document.insert.get_node().get_iterator().get_line()
        if document.insert.get_node() != line.get_child(-1) or line.parent.get_child(-1) != line:
            self.state['deleted_char'] = document.delete_char_at_cursor()
            self.is_undo_checkpoint = True
        else:
            self.state['deleted_char'] = None
            self.is_undo_checkpoint = False

    def undo(self, document):
        if self.state['deleted_char'] != None:
            document.insert_text_at_cursor(self.state['deleted_char'])
            document.move_cursor_by_offset(-1)


class Backspace():

    def __init__(self):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        line = document.insert.get_node().get_iterator().get_line()
        index = line.get_index(document.insert.get_node())
        if document.lines.get_index(line) != 0 or index != 0:
            document.move_cursor_by_offset(-1)
            self.state['deleted_char'] = document.delete_char_at_cursor()
            self.is_undo_checkpoint = True
        else:
            self.state['deleted_char'] = None
            self.is_undo_checkpoint = False

    def undo(self, document):
        if self.state['deleted_char'] != None:
            document.insert_text_at_cursor(self.state['deleted_char'])


