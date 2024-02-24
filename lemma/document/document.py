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
        offset_moved = 0
        iterator = self.insert.get_node().get_iterator()

        if offset < 0:
            while offset < offset_moved:
                if iterator.prev() == False:
                    break
                offset_moved -= 1
        else:
            while offset > offset_moved:
                if iterator.next() == False:
                    break
                offset_moved += 1
        self.insert.set_node(iterator.get_node())

        return offset_moved

    def insert_text_at_cursor(self, text):
        for char in text:
            if char == '\n':
    	        self.insert_linebreak()
            else:
    	        self.insert_character(char)

    def insert_character(self, char):
        character = UnicodeCharacter(char)
        line = self.insert.get_node().get_iterator().get_line()
        index = line.get_index(self.insert.get_node())
        line.insert(index, character)

    def insert_linebreak(self):
        orig_line = self.insert.get_node().get_iterator().get_line()
        line_1, line_2 = orig_line.split(self.insert.get_node())
        index = self.lines.get_index(orig_line)
        self.lines.remove(orig_line)
        self.lines.insert(index, line_2)
        self.lines.insert(index, line_1)
        self.insert.set_node(line_2.get_child(0))

    def delete_char_at_cursor(self):
        deleted_char = None

        line = self.insert.get_node().get_iterator().get_line()
        if self.insert.get_node() == line.get_child(-1):
            if self.lines.get_child(-1) != line:
                deleted_char = '\n'

                line_1 = self.insert.get_node().get_iterator().get_line()
                line_2 = self.lines.get_child(self.lines.get_index(line_1) + 1)
                new_line = Line()
                new_line.add(line_1)
                new_line.add(line_2)
                index = self.lines.get_index(line_1)
                self.lines.insert(index, new_line)
                self.lines.remove(line_1)
                self.lines.remove(line_2)
                self.insert.set_node(new_line.get_child(line_1.length() - 1))
        else:
            deleted_char = self.insert.get_node().content

            line = self.insert.get_node().get_iterator().get_line()
            index = line.get_index(self.insert.get_node())
            line.remove(self.insert.get_node())
            self.insert.set_node(line.get_child(index))

        return deleted_char


