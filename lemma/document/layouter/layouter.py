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
from lemma.document.layout.layout import Box
import lemma.helpers.helpers as helpers


class Layouter(object):

    def __init__(self, document):
        self.document = document

        self.root = Box('vcontainer', width=0, height=0)
        self.current_line_box = Box('hcontainer', width=0, height=FontManager.get_line_height())

        self.current_number = []

    def update(self):
        self.root = Box('vcontainer', width=0, height=0)
        self.current_line_box = Box('hcontainer', width=0, height=FontManager.get_line_height())

        node_lists = self.group_by_node_type(self.document.ast.root)
        for node_list in node_lists:
            self.process_list(node_list)

        self.document.layout = self.root

    def group_by_node_type(self, root_node):
        last_type = None
        last_tags = set()
        result = list()
        for node in root_node:
            if LaTeXDB.is_whitespace(node.value):
                result.append(list())
                last_type = None
                last_tags = set()
            elif node.type != last_type or node.tags.symmetric_difference(last_tags):
                result.append(list())
                last_type = node.type
                last_tags = node.tags
            result[-1].append(node)
        return result

    def process_list(self, node_list):
        if node_list[0].type == 'char' and not LaTeXDB.is_whitespace(node_list[0].value):
            self.process_word(node_list)
        else:
            for node in node_list:
                self.process_node(node)

    def process_word(self, node_list):
        if len(node_list) == 0: return

        text = ''
        for char in node_list:
            text += char.value

        total_width = 0
        char_boxes = []

        node = node_list[0]
        if 'bold' in node.tags and 'italic' not in node.tags: fontname = 'bold'
        elif 'bold' in node.tags and 'italic' in node.tags: fontname = 'bolditalic'
        elif 'bold' not in node.tags and 'italic' in node.tags: fontname = 'italic'
        else: fontname = 'book'

        for node, extents in zip(node_list, FontManager.get_char_extents_multi(text, fontname=fontname)):
            width, height, left, top = extents
            total_width += width
            box = Box('glyph', width=width, height=height, left=left, top=top, node=node)
            node.set_box(box)
            char_boxes.append(box)

        if self.current_line_box.width > 0 and self.current_line_box.width + total_width > 670:
            self.break_line()

        for i, box in enumerate(char_boxes):
            self.add_box(box)

    def process_node(self, node):
        if node.type == 'EOL':
            box = Box('empty', node=node)
            node.set_box(box)

            self.add_box(box)
            self.break_line()

        elif node.type == 'placeholder':
            width, height, left, top = FontManager.get_char_extents_single('•', fontname='math')
            box = Box('placeholder', width=width, height=height, left=left, top=top, node=node)
            node.set_box(box)

            self.add_box(box)

        elif node.type == 'mathsymbol':
            width, height, left, top = FontManager.get_char_extents_single(node.value, fontname='math')
            box = Box('glyph', width=width, height=height, left=left, top=top, node=node)
            box.classes.add('math')
            node.set_box(box)

            self.add_box(box)

        elif node.type == 'char' and LaTeXDB.is_whitespace(node.value):
            width, height, left, top = FontManager.get_char_extents_single(node.value)
            box = Box('glyph', width=width, height=height, left=left, top=top, node=node)
            node.set_box(box)

            self.add_box(box)

    def add_box(self, box):
        if self.current_line_box.width + box.width > 670:
            self.break_line()
        self.current_line_box.add(box)

    def break_line(self):
        self.root.add(self.current_line_box)
        self.current_line_box = Box('hcontainer', width=0, height=FontManager.get_line_height())


