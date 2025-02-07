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
from lemma.document.layout.layout_document import LayoutDocument
from lemma.document.layout.layout_word import LayoutWord
from lemma.document.layout.layout_char import LayoutChar
from lemma.document.layout.layout_placeholder import LayoutPlaceholder
from lemma.document.layout.layout_widget import LayoutWidget
from lemma.document.layout.layout_eol import LayoutEOL
from lemma.document.layout.layout_end import LayoutEnd
from lemma.document.layout.layout_mathatom import LayoutMathAtom
from lemma.document.layout.layout_mathroot import LayoutMathRoot
from lemma.document.layout.layout_hbox import LayoutHBox
import lemma.infrastructure.timer as timer


class Layouter(object):

    def __init__(self, document):
        self.document = document

    def update(self):
        if self.document.has_changed(self):
            self.update_layout()

    @timer.timer
    def update_layout(self):
        layout_tree = self.make_layout_tree(self.document.ast)
        layout_tree.layout()
        self.document.layout = layout_tree

    def make_layout_tree(self, node, parent=None):
        if node.type == 'root': layout_tree = LayoutDocument(node, parent)
        elif node.type == 'char': layout_tree = LayoutChar(node, parent)
        elif node.type == 'placeholder': layout_tree = LayoutPlaceholder(node, parent)
        elif node.type == 'eol': layout_tree = LayoutEOL(node, parent)
        elif node.type == 'end': layout_tree = LayoutEnd(node, parent)
        elif node.type == 'widget': layout_tree = LayoutWidget(node, parent)
        elif node.type == 'mathatom': layout_tree = LayoutMathAtom(node, parent)
        elif node.type == 'mathroot': layout_tree = LayoutMathRoot(node, parent)
        elif node.type == 'mathlist': layout_tree = LayoutHBox(parent)
        else: layout_tree = None

        if node.type == 'root':
            for child in self.group_words(node):
                if isinstance(child, list) and child[0].is_text():
                    subtree = LayoutWord(node)
                    char_nodes = child
                    text = ''.join([char.value for char in char_nodes])
                    fontname = FontManager.get_fontname_from_node(char_nodes[0])
                    for char_node, extents in zip(char_nodes, FontManager.measure(text, fontname=fontname)):
                        subtree.children.append(LayoutChar(char_node, node, extents=extents))
                else:
                    subtree = self.make_layout_tree(child, layout_tree)
                if subtree != None:
                    layout_tree.children.append(subtree)
        else:
            for child in node.children:
                subtree = self.make_layout_tree(child, layout_tree)
                if subtree != None:
                    layout_tree.children.append(subtree)

        return layout_tree

    @timer.timer
    def group_words(self, parent_node):
        last_type = None
        last_tags = set()
        result = list()
        for node in parent_node:
            if node.is_whitespace() or not node.is_text():
                result.append(node)
                last_type = None
                last_tags = set()
            elif node.type != last_type or node.tags.symmetric_difference(last_tags):
                result.append(list())
                last_type = node.type
                last_tags = node.tags
                result[-1].append(node)
            else:
                result[-1].append(node)
        return result


