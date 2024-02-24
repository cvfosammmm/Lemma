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

import time

from lemma.ast.node import *
from lemma.cursor.cursor import Cursor
from lemma.layouter.layouter import Layouter
from lemma.markdown_scanner.markdown_scanner import MarkdownScanner
from lemma.teaser_scanner.teaser_scanner import TeaserScanner
from lemma.helpers.observable import Observable
from lemma.command_processor.command_processor import CommandProcessor


class Document(Observable):

    def __init__(self, workspace, id):
        Observable.__init__(self)
        self.workspace = workspace

        self.last_modified = time.time()
        self.command_processor = CommandProcessor(self)

        self.id = id
        self.title = ''
        self.lines = Lines()
        self.lines.insert(0, Line())
        self.insert = Cursor(self, self.lines.get_child(0).get_child(0))

        self.layouter = Layouter(self)
        self.markdown_scanner = MarkdownScanner(self)
        self.teaser_scanner = TeaserScanner(self)

    def set_last_modified(self):
        self.last_modified = time.time()
        self.add_change_code('changed')

    def move_cursor_by_offset(self, offset):
        if offset < 0:
            offset_moved = -self.move_left(-offset)
        else:
            offset_moved = self.move_right(offset)
        return offset_moved

    def move_left(self, offset):
        offset_moved = 0

        while offset > offset_moved:
            iterator = self.insert.get_node().get_iterator()
            line = iterator.get_line()
            if not iterator.starts_line():
                iterator.prev()
                self.insert.set_node(iterator.get_node())
                offset_moved += 1
            else:
                if line.parent.get_child(0) == line:
                    break
                else:
                    index = line.parent.get_index(line)
                    self.insert.set_node(line.parent.get_child(index - 1).get_child(-1))
                    offset_moved += 1

        return offset_moved

    def move_right(self, offset):
        offset_moved = 0

        while offset > offset_moved:
            iterator = self.insert.get_node().get_iterator()
            line = iterator.get_line()
            if not iterator.ends_line():
                iterator.next()
                self.insert.set_node(iterator.get_node())
                offset_moved += 1
            else:
                if line.parent.get_child(-1) == line:
                    break
                else:
                    index = line.parent.get_index(line)
                    self.insert.set_node(line.parent.get_child(index + 1).get_child(0))
                    offset_moved += 1

        return offset_moved

    def insert_text_at_cursor(self, text):
        for char in text:
            if char == '\n':
    	        self.insert_linebreak()
            else:
    	        self.insert_character(char)

    def insert_character(self, char):
        character = UnicodeCharacter(char)
        iterator = self.insert.get_node().get_iterator()
        line = iterator.get_line()
        index = line.get_index(self.insert.get_node())
        line.insert(index, character)

    def insert_linebreak(self):
        iterator = self.insert.get_node().get_iterator()
        orig_line = iterator.get_line()
        line_1 = Line()
        line_2 = Line()
        separating_child = self.insert.get_node()

        current_line = line_1
        for child in orig_line:
            if child == separating_child:
                current_line = line_2
            if child != orig_line.get_child(-1):
                current_line.append(child)

        index = self.lines.get_index(orig_line)
        self.lines.remove(orig_line)
        self.lines.insert(index, line_2)
        self.lines.insert(index, line_1)
        self.insert.set_node(line_2.get_child(0))

    def delete_char_at_cursor(self):
        deleted_char = None

        iterator = self.insert.get_node().get_iterator()
        line = iterator.get_line()
        if self.insert.get_node() == line.get_child(-1):
            if line.parent.get_child(-1) != line:
                deleted_char = '\n'

                iterator = self.insert.get_node().get_iterator()
                line_1 = iterator.get_line()
                iterator = line_1.get_iterator()
                iterator.next()
                line_2 = iterator.get_node()
                new_line = Line()
                for child in line_1:
                    if child != line_1.get_child(-1):
                        new_line.append(child)
                for child in line_2:
                    if child != line_2.get_child(-1):
                        new_line.append(child)
                index = self.lines.get_index(line_1)
                self.lines.insert(index, new_line)
                self.lines.remove(line_1)
                self.lines.remove(line_2)
                self.insert.set_node(new_line.get_child(line_1.length() - 1))
        else:
            deleted_char = self.insert.get_node().content

            iterator = self.insert.get_node().get_iterator()
            line = iterator.get_line()
            index = line.get_index(self.insert.get_node())
            line.remove(self.insert.get_node())
            self.insert.set_node(line.get_child(index))

        return deleted_char


