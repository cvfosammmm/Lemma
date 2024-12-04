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
from lemma.infrastructure.layout_info import LayoutInfo
from lemma.document.layout.layout import Box
import lemma.helpers.helpers as helpers


class Layouter(object):

    def __init__(self, document):
        self.document = document

        self.root = Box('vcontainer', width=0, height=0, fontname=self.get_fontname())
        self.current_line_box = Box('hcontainer', width=0, height=FontManager.get_line_height(fontname=self.get_fontname()), fontname=self.get_fontname())

        self.current_number = []

    def update(self):
        self.root = Box('vcontainer', width=0, height=0, fontname=self.get_fontname())
        self.current_line_box = Box('hcontainer', width=0, height=FontManager.get_line_height(fontname=self.get_fontname()), fontname=self.get_fontname())

        node_lists = self.group_by_node_type(self.document.ast)
        for node_list in node_lists:
            self.process_list(node_list)

        self.document.layout = self.root

    def group_by_node_type(self, root_node):
        last_type = None
        last_tags = set()
        result = list()
        for node in root_node:
            if node.is_whitespace():
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
        if node_list[0].is_char() and not node_list[0].is_whitespace():
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

        for node, extents in zip(node_list, FontManager.get_char_extents_multi(text, fontname=self.get_fontname(node_list[0]))):
            width, height, left, top = extents
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            total_width += width
            box = Box('glyph', width=width, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)
            char_boxes.append(box)

        if self.current_line_box.width > 0 and self.current_line_box.width + total_width > LayoutInfo.get_layout_width():
            self.break_line()

        for i, box in enumerate(char_boxes):
            self.add_box(self.current_line_box, box)

    def process_node(self, node, container=None):
        if container == None:
            container = self.current_line_box

        if node.is_eol():
            width, height, left, top = FontManager.get_char_extents_single('\n', fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('empty', width=0, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)
            self.break_line()

        elif node.is_mathsymbol():
            width, height, left, top = FontManager.get_char_extents_single(node.value, fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('glyph', width=width, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)

        elif node.is_char() and node.is_whitespace():
            width, height, left, top = FontManager.get_char_extents_single(node.value, fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
 
            if self.current_line_box.width + width > LayoutInfo.get_layout_width():
                box = Box('empty', width=0, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
                node.set_box(box)
                self.current_line_box.add(box)
                self.break_line()
            else:
                box = Box('glyph', width=width, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
                node.set_box(box)
                self.current_line_box.add(box)

        elif node.is_char():
            width, height, left, top = FontManager.get_char_extents_single(node.value, fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('glyph', width=width, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)

        elif node.is_widget():
            width, height, left, top = node.value.get_width(), node.value.get_height(), 0, 0
            height += 2 * FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            top += FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('widget', width=width, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)

        elif node.is_mathatom():
            width, height, left, top = FontManager.get_char_extents_single('\n', fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('empty', width=0, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)

            for child in node[0]:
                self.process_node(child, container)

            super_box = Box('hcontainer', width=0, height=FontManager.get_line_height(fontname=self.get_fontname(node)) / 2, fontname=self.get_fontname(node))
            for child in node[2]:
                self.process_node(child, super_box)

            sub_box = Box('hcontainer', width=0, height=FontManager.get_line_height(fontname=self.get_fontname(node)) / 2, fontname=self.get_fontname(node))
            for child in node[1]:
                self.process_node(child, sub_box)

            super_sub_box = Box('vcontainer', width=0, height=0, fontname=self.get_fontname(node))
            super_sub_box.add(super_box)
            super_sub_box.add(sub_box)
            self.add_box(container, super_sub_box)

        elif node.is_composite():
            width, height, left, top = FontManager.get_char_extents_single('\n', fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('empty', width=0, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)

            for child in node:
                self.process_node(child, container)

        else:
            width, height, left, top = FontManager.get_char_extents_single('\n', fontname=self.get_fontname(node))
            top -= FontManager.get_cursor_offset(fontname=self.get_fontname(node))
            box = Box('empty', width=0, height=height, left=left, top=top, node=node, fontname=self.get_fontname(node))
            node.set_box(box)

            self.add_box(container, box)

    def add_box(self, container, box):
        if container == self.current_line_box.width:
            if self.current_line_box.width + box.width > LayoutInfo.get_layout_width():
                self.break_line()
                container = self.current_line_box
        container.add(box)

    def break_line(self):
        self.root.add(self.current_line_box)
        self.current_line_box = Box('hcontainer', width=0, height=FontManager.get_line_height(fontname=self.get_fontname()), fontname=self.get_fontname())

    def get_fontname(self, node=None):
        if node == None: return 'book'

        if node.is_subscript() or node.is_superscript():
            return 'math_small'
        if node.is_nucleus():
            return 'math'

        if node.is_mathsymbol():
            return 'math'

        if node.get_paragraph_style().startswith('h'): return node.get_paragraph_style()

        if 'bold' in node.tags and 'italic' not in node.tags: return 'bold'
        if 'bold' in node.tags and 'italic' in node.tags: return 'bolditalic'
        if 'bold' not in node.tags and 'italic' in node.tags: return 'italic'

        return 'book'


