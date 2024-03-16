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
from lemma.app.latex_db import LaTeXDB
import lemma.document.layout.layout as boxes
import lemma.helpers.helpers as helpers


class Layouter(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.root = boxes.BoxVContainer()
        self.current_line_box = boxes.BoxHContainer()
        self.current_math_box = boxes.BoxHContainer()
        self.current_word = []
        self.current_number = []
        self.in_math_mode = False

    def update(self):
        self.root = boxes.BoxVContainer()
        self.document.ast.root.accept(self)
        self.document.layout = self.root

    def visit_root(self, root):
        for line in root.children:
            line.accept(self)

    def visit_line(self, line):
        for char in line.children:
            char.accept(self)

    def visit_beforemath(self, beforemath):
        self.process_current_word()
        box = boxes.BoxEmpty(node=beforemath)
        beforemath.set_box(box)
        self.current_line_box.add(box)
        self.in_math_mode = True

    def visit_matharea(self, matharea):
        self.current_math_box = boxes.BoxHContainer()
        for char in matharea.children:
            char.accept(self)

        self.add_boxes_and_break_lines_in_case([self.current_math_box], self.current_math_box.width)

    def visit_aftermath(self, aftermath):
        self.in_math_mode = False
        self.process_current_number()

        if aftermath.parent.length() == 1:
            width, height, left, top = FontManager.get_char_extents_single('•', fontname='math')
            box = boxes.BoxPlaceholder(width, height, left, top, node=aftermath)
        else:
            box = boxes.BoxEmpty(node=aftermath)
        box.classes.add('math')
        aftermath.set_box(box)

        self.current_math_box.add(box)

    def visit_char(self, char):
        if self.in_math_mode:
            if char.content.isdigit():
                self.current_number.append(char)
            else:
                self.process_current_number()

                if char.content.isalpha() and char.content.islower():
                    char_string = chr(ord(char.content) + 119789)
                elif char.content.isalpha() and char.content.isupper():
                    char_string = chr(ord(char.content) + 119795)
                else:
                    char_string = char.content

                width, height, left, top = FontManager.get_char_extents_single(char_string, fontname='math')
                box = boxes.BoxGlyph(width, height, left, top, char_string, node=char)
                box.classes.add('math')
                char.set_box(box)
                self.current_math_box.add(box)

        else:
            if char.is_whitespace:
                self.process_current_word()

                width, height, left, top = FontManager.get_char_extents_single(char.content)
                box = boxes.BoxGlyph(width, height, left, top, char.content, node=char)
                self.current_line_box.add(box)
                char.set_box(box)

            else:
                self.current_word.append(char)

    def visit_eol(self, node):
        self.process_current_word()
        box = boxes.BoxEmpty(node=node)
        self.current_line_box.add(box)
        node.set_box(box)
        self.root.add(self.current_line_box)
        self.current_line_box = boxes.BoxHContainer()

    def process_current_word(self):
        if len(self.current_word) == 0: return

        text = ''
        for char in self.current_word:
            text += char.content

        total_width = 0
        char_boxes = []
        for char, extents in zip(self.current_word, FontManager.get_char_extents_multi(text)):
            width, height, left, top = extents
            total_width += width

            box = boxes.BoxGlyph(width, height, left, top, char.content, node=char)
            char.set_box(box)
            char_boxes.append(box)
        self.current_word = []

        self.add_boxes_and_break_lines_in_case(char_boxes, total_width)

    def process_current_number(self):
        if len(self.current_number) == 0: return

        text = ''
        for char in self.current_number:
            text += char.content

        total_width = 0
        for char, extents in zip(self.current_number, FontManager.get_char_extents_multi(text, fontname='math')):
            width, height, left, top = extents
            total_width += width

            box = boxes.BoxGlyph(width, height, left, top, char.content, node=char)
            box.classes.add('math')
            char.set_box(box)
            self.current_math_box.add(box)
        self.current_number = []

    def add_boxes_and_break_lines_in_case(self, boxes_list, width):
        if self.current_line_box.width + width > 670:
            self.root.add(self.current_line_box)
            self.current_line_box = boxes.BoxHContainer()

        for i, box in enumerate(boxes_list):
            self.current_line_box.add(box)


