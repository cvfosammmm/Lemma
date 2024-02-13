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

from lemma.ast.node import *


class InsertTextAtCursor():

    def __init__(self, text):
        self.text = text
        self.state = dict()

    def run(self, document):
        for char in self.text:
            if char == '\n':
    	        self.insert_linebreak(document)
            else:
    	        self.insert_character(document, char)

    def undo(self, document):
        for char in reversed(self.text):
            if char == '\n':
                iterator = document.insert.get_node().get_iterator()
                line_2 = iterator.get_line()
                iterator = line_2.get_iterator()
                iterator.prev()
                line_1 = iterator.get_node()
                new_line = self.merge_lines(line_1, line_2)
                index = document.lines.get_index(line_1)
                document.lines.insert(index, new_line)
                document.lines.remove(line_1)
                document.lines.remove(line_2)
                document.insert.set_node(new_line.get_child(-1))
            else:
                iterator = document.insert.get_node().get_iterator()
                line = iterator.get_line()
                index = line.get_index(document.insert.get_node())
                if index > 0:
                    child = line.get_child(index - 1)
                    line.remove(child)

    def insert_character(self, document, char):
        character = UnicodeCharacter(char)
        iterator = document.insert.get_node().get_iterator()
        line = iterator.get_line()
        index = line.get_index(document.insert.get_node())
        line.insert(index, character)

    def insert_linebreak(self, document):
        iterator = document.insert.get_node().get_iterator()
        orig_line = iterator.get_line()
        line_1, line_2 = self.split_line(orig_line, document.insert.get_node())
        index = document.lines.get_index(orig_line)
        document.lines.remove(orig_line)
        document.lines.insert(index, line_2)
        document.lines.insert(index, line_1)
        document.insert.set_node(line_2.get_child(0))

    def split_line(self, line, separating_child):
        line_1 = Line()
        line_2 = Line()

        current_line = line_1
        for child in line:
            if child == separating_child:
                current_line = line_2
            if child != line.get_child(-1):
                current_line.append(child)

        return (line_1, line_2)

    def merge_lines(self, line_1, line_2):
        new_line = Line()

        for child in line_1:
            if child != line_1.get_child(-1):
                new_line.append(child)
        for child in line_2:
            if child != line_2.get_child(-1):
                new_line.append(child)

        return new_line


class DeleteTextAtCursor():

    def __init__(self):
        self.state = dict()

    def run(self, document):
        iterator = document.insert.get_node().get_iterator()
        line = iterator.get_line()
        if document.insert.get_node() == line.get_child(-1):
            if line.parent.get_child(-1) == line:
                self.state['deleted_char'] = None
            else:
                self.state['deleted_char'] = '\n'

                iterator = document.insert.get_node().get_iterator()
                line_1 = iterator.get_line()
                iterator = line_1.get_iterator()
                iterator.next()
                line_2 = iterator.get_node()
                new_line = self.merge_lines(line_1, line_2)
                index = document.lines.get_index(line_1)
                document.lines.insert(index, new_line)
                document.lines.remove(line_1)
                document.lines.remove(line_2)
                document.insert.set_node(new_line.get_child(line_1.length() - 1))
        else:
            self.state['deleted_char'] = document.insert.get_node()

            iterator = document.insert.get_node().get_iterator()
            line = iterator.get_line()
            index = line.get_index(document.insert.get_node())
            line.remove(document.insert.get_node())
            document.insert.set_node(line.get_child(index))

    def undo(self, document):
        if self.state['deleted_char'] == '\n':
            iterator = document.insert.get_node().get_iterator()
            orig_line = iterator.get_line()
            line_1, line_2 = self.split_line(orig_line, document.insert.get_node())
            index = document.lines.get_index(orig_line)
            document.lines.remove(orig_line)
            document.lines.insert(index, line_2)
            document.lines.insert(index, line_1)
            document.insert.set_node(line_1.get_child(-1))
        elif self.state['deleted_char'] != None:
            iterator = document.insert.get_node().get_iterator()
            line = iterator.get_line()
            index = line.get_index(document.insert.get_node())
            line.insert(index, self.state['deleted_char'])
            document.insert.set_node(self.state['deleted_char'])

    def split_line(self, line, separating_child):
        line_1 = Line()
        line_2 = Line()

        current_line = line_1
        for child in line:
            if child == separating_child:
                current_line = line_2
            if child != line.get_child(-1):
                current_line.append(child)

        return (line_1, line_2)

    def merge_lines(self, line_1, line_2):
        new_line = Line()

        for child in line_1:
            if child != line_1.get_child(-1):
                new_line.append(child)
        for child in line_2:
            if child != line_2.get_child(-1):
                new_line.append(child)

        return new_line


class MoveCursorByOffset():

    def __init__(self, offset):
        self.offset = offset
        self.state = dict()

    def run(self, document):
        if self.offset < 0:
            self.state['offset'] = self.move_left(document, -self.offset)
        else:
            self.state['offset'] = self.move_right(document, self.offset)

    def undo(self, document):
        if self.offset < 0:
            self.move_right(document, self.state['offset'])
        else:
            self.move_left(document, self.state['offset'])

    def move_left(self, document, offset):
        offset_moved = 0

        while offset > offset_moved:
            iterator = document.insert.get_node().get_iterator()
            line = iterator.get_line()
            if not iterator.starts_line():
                iterator.prev()
                document.insert.set_node(iterator.get_node())
                offset_moved += 1
            else:
                if line.parent.get_child(0) == line:
                    break
                else:
                    index = line.parent.get_index(line)
                    document.insert.set_node(line.parent.get_child(index - 1).get_child(-1))
                    offset_moved += 1

        return offset_moved

    def move_right(self, document, offset):
        offset_moved = 0

        while offset > offset_moved:
            iterator = document.insert.get_node().get_iterator()
            line = iterator.get_line()
            if not iterator.ends_line():
                iterator.next()
                document.insert.set_node(iterator.get_node())
                offset_moved += 1
            else:
                if line.parent.get_child(-1) == line:
                    break
                else:
                    index = line.parent.get_index(line)
                    document.insert.set_node(line.parent.get_child(index + 1).get_child(0))
                    offset_moved += 1

        return offset_moved


