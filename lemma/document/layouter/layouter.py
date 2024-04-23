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

from lemma.app.font_manager import FontManager
from lemma.app.latex_db import LaTeXDB
import lemma.document.layout.layout as boxes
import lemma.helpers.helpers as helpers


class Layouter(object):

    def __init__(self, document):
        self.document = document

        self.root = boxes.BoxVContainer()
        self.current_line_box = boxes.BoxHContainer()
        self.current_math_box = boxes.BoxHContainer()
        self.current_word = []
        self.current_number = []
        self.in_math_mode = False

    def update(self):
        self.root = boxes.BoxVContainer()

        for child in self.document.ast.root.children:
            self.process_node(child)

        self.document.layout = self.root

    def process_node(self, node):
        if node.is_matharea():
            self.in_math_mode = True
            self.current_math_box = boxes.BoxHContainer()
            box = boxes.BoxEmpty(node=node)
            node.set_box(box)
            self.current_math_box.add(box)
            for child in node.children:
                self.process_node(child)
            self.add_boxes_and_break_lines_in_case([self.current_math_box], self.current_math_box.width)
            self.in_math_mode = False

        elif node.head == 'EOL':
            self.process_current_word()
            self.process_current_number()
            box = boxes.BoxEmpty(node=node)
            self.current_line_box.add(box)
            self.root.add(self.current_line_box)
            self.current_line_box = boxes.BoxHContainer()
            node.set_box(box)

        elif node.head == 'placeholder':
            self.process_current_word()
            self.process_current_number()
            if node.parent.length() == 1:
                width, height, left, top = FontManager.get_char_extents_single('•', fontname='math')
                box = boxes.BoxPlaceholder(width, height, left, top, node=node)
            else:
                box = boxes.BoxEmpty(node=node)
            self.current_math_box.add(box)
            node.set_box(box)

        elif self.in_math_mode:
            if node.head.isdigit():
                self.current_number.append(node)
            else:
                self.process_current_number()

                width, height, left, top = FontManager.get_char_extents_single(node.head, fontname='math')

                if LaTeXDB.is_binary_operation(node.head):
                    width += FontManager.get_medspace() * 2
                    left += FontManager.get_medspace()

                if LaTeXDB.is_relation(node.head):
                    width += FontManager.get_thickspace() * 2
                    left += FontManager.get_thickspace()

                if LaTeXDB.is_punctuation_mark(node.head):
                    width += FontManager.get_thinspace()

                box = boxes.BoxGlyph(width, height, left, top, node.head, node=node)
                box.classes.add('math')
                node.set_box(box)
                self.current_math_box.add(box)

        elif LaTeXDB.is_whitespace(node.head):
            self.process_current_word()
            width, height, left, top = FontManager.get_char_extents_single(node.head)
            box = boxes.BoxGlyph(width, height, left, top, node.head, node=node)
            self.current_line_box.add(box)
            node.set_box(box)

        else:
            self.current_word.append(node)

    def process_current_word(self):
        if len(self.current_word) == 0: return

        text = ''
        for char in self.current_word:
            text += char.head

        total_width = 0
        char_boxes = []
        for char, extents in zip(self.current_word, FontManager.get_char_extents_multi(text)):
            width, height, left, top = extents
            total_width += width

            box = boxes.BoxGlyph(width, height, left, top, char.head, node=char)
            char.set_box(box)
            char_boxes.append(box)
        self.current_word = []

        self.add_boxes_and_break_lines_in_case(char_boxes, total_width)

    def process_current_number(self):
        if len(self.current_number) == 0: return

        text = ''
        for char in self.current_number:
            text += char.head

        total_width = 0
        for char, extents in zip(self.current_number, FontManager.get_char_extents_multi(text, fontname='math')):
            width, height, left, top = extents
            total_width += width

            box = boxes.BoxGlyph(width, height, left, top, char.head, node=char)
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


