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

from lemma.infrastructure.font_manager import FontManager
from lemma.latex_db.latex_db import LaTeXDB
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

        for child in self.document.ast.root:
            self.process_node(child)

        self.document.layout = self.root

    def process_node(self, node):
        if node.type == 'EOL':
            self.process_current_word()
            self.process_current_number()

            box = boxes.BoxEmpty(node=node)
            self.current_line_box.add(box)
            self.root.add(self.current_line_box)
            self.current_line_box = boxes.BoxHContainer()
            node.set_box(box)

        elif node.type == 'placeholder':
            self.process_current_word()
            self.process_current_number()

            if len(node.parent) == 1:
                width, height, left, top = FontManager.get_char_extents_single('•', fontname='math')
                box = boxes.BoxPlaceholder(width, height, left, top, node=node)
            else:
                box = boxes.BoxEmpty(node=node)
            self.current_line_box.add(box)
            node.set_box(box)

        elif node.type == 'mathsymbol':
            self.process_current_word()
            self.process_current_number()

            width, height, left, top = FontManager.get_char_extents_single(node.value, fontname='math')
            box = boxes.BoxGlyph(width, height, left, top, node.value, node=node)
            box.classes.add('math')
            node.set_box(box)
            self.current_line_box.add(box)

        elif node.type == 'char':
            if LaTeXDB.is_whitespace(node.value):
                self.process_current_word()
                width, height, left, top = FontManager.get_char_extents_single(node.value)
                box = boxes.BoxGlyph(width, height, left, top, node.value, node=node)
                self.current_line_box.add(box)
                node.set_box(box)
            else:
                self.current_word.append(node)

    def process_current_word(self):
        if len(self.current_word) == 0: return

        text = ''
        for char in self.current_word:
            text += char.value

        total_width = 0
        char_boxes = []

        node = self.current_word[0]
        if 'bold' in node.tags and 'italic' not in node.tags: fontname = 'bold'
        elif 'bold' in node.tags and 'italic' in node.tags: fontname = 'bolditalic'
        elif 'bold' not in node.tags and 'italic' in node.tags: fontname = 'italic'
        else: fontname = 'book'

        for char, extents in zip(self.current_word, FontManager.get_char_extents_multi(text, fontname=fontname)):
            width, height, left, top = extents
            total_width += width

            box = boxes.BoxGlyph(width, height, left, top, char.value, node=char)
            char.set_box(box)
            char_boxes.append(box)
        self.current_word = []

        self.add_boxes_and_break_lines_in_case(char_boxes, total_width)

    def process_current_number(self):
        if len(self.current_number) == 0: return

        text = ''
        for char in self.current_number:
            text += char.value

        total_width = 0
        for char, extents in zip(self.current_number, FontManager.get_char_extents_multi(text, fontname='math')):
            width, height, left, top = extents
            total_width += width

            box = boxes.BoxGlyph(width, height, left, top, char.value, node=char)
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


