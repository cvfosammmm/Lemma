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

from lemma.helpers.observable import Observable
from lemma.app.font_manager import FontManager
from lemma.layout.layout import *
import lemma.helpers.helpers as helpers


class Layouter(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.root = BoxVContainer()
        self.current_line_box = BoxHContainer()
        self.current_word = []

    def update(self):
        self.root = BoxVContainer()
        self.document.lines.accept(self)
        self.document.layout = self.root

    def visit_lines(self, lines):
        for line in lines.children:
            line.accept(self)

    def visit_line(self, line):
        for char in line.children:
            char.accept(self)

    def visit_char(self, char):
        if char.is_whitespace:
            if len(self.current_word) > 0:
                self.process_current_word()

            width, height, left, top = FontManager.get_char_extents_single(char.content)
            self.add_box_to_current_line(BoxGlyph(width, height, left, top, char.content, node=char))
        else:
            self.current_word.append(char)

    def visit_eol(self, node):
        self.process_current_word()
        self.add_box_to_current_line(BoxEOL(node=node))
        self.root.add(self.current_line_box)
        self.current_line_box = BoxHContainer()

    def visit_node(self, node):
        pass

    def process_current_word(self):
        text = ''
        for char in self.current_word:
            text += char.content

        total_width = 0
        char_boxes = []
        for char, extents in zip(self.current_word, FontManager.get_char_extents_multi(text)):
            width, height, left, top = extents
            total_width += width

            box = BoxGlyph(width, height, left, top, char.content, node=char)
            char_boxes.append(box)

        if self.current_line_box.width + total_width > 670:
            self.root.add(self.current_line_box)
            self.current_line_box = BoxHContainer()

        for i, box in enumerate(char_boxes):
            self.add_box_to_current_line(box)

        self.current_word = []

    def add_box_to_current_line(self, box):
        if self.document.insert.get_node() == box.get_node():
            self.current_line_box.add(BoxInsert(height=26, top=7))

        self.current_line_box.add(box)


