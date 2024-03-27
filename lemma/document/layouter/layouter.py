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

    def update(self):
        self.root = boxes.BoxVContainer()
        self.document.ast.root.accept(self)
        self.document.layout = self.root

    def visit_root(self, root):
        for child in root.children:
            child.accept(self)

    def visit_placeholder(self, placeholder):
        self.process_current_word()
        self.process_current_number()

        if placeholder.name == 'EOL':
            box = boxes.BoxEmpty(node=placeholder)
            self.current_line_box.add(box)
            self.root.add(self.current_line_box)
            self.current_line_box = boxes.BoxHContainer()
        elif placeholder.parent.is_math_area():
            if placeholder.parent.length() == 1:
                width, height, left, top = FontManager.get_char_extents_single('•', fontname='math')
                box = boxes.BoxPlaceholder(width, height, left, top, node=placeholder)
            else:
                box = boxes.BoxEmpty(node=placeholder)
            self.current_math_box.add(box)
        else:
            box = boxes.BoxEmpty(node=placeholder)
            self.current_line_box.add(box)
        placeholder.set_box(box)

    def visit_matharea(self, matharea):
        self.current_math_box = boxes.BoxHContainer()
        for char in matharea.children:
            char.accept(self)

        self.add_boxes_and_break_lines_in_case([self.current_math_box], self.current_math_box.width)

    def visit_mathsymbol(self, symbol):
        if symbol.content.isdigit():
            self.current_number.append(symbol)
        else:
            self.process_current_number()

            width, height, left, top = FontManager.get_char_extents_single(symbol.content, fontname='math')

            if symbol.layout_mode == 'bin':
                width += FontManager.get_medspace() * 2
                left += FontManager.get_medspace()

            if symbol.layout_mode == 'rel':
                width += FontManager.get_thickspace() * 2
                left += FontManager.get_thickspace()

            if symbol.layout_mode == 'punct':
                width += FontManager.get_thinspace()

            box = boxes.BoxGlyph(width, height, left, top, symbol.content, node=symbol)
            box.classes.add('math')
            symbol.set_box(box)
            self.current_math_box.add(box)

    def visit_char(self, char):
        if char.is_whitespace:
            self.process_current_word()

            width, height, left, top = FontManager.get_char_extents_single(char.content)
            box = boxes.BoxGlyph(width, height, left, top, char.content, node=char)
            self.current_line_box.add(box)
            char.set_box(box)

        else:
            self.current_word.append(char)

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


