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

from lemma.document.layout.layout_word import LayoutWord
from lemma.infrastructure.font_manager import FontManager
from lemma.document.layout.layout import Layout


class LayoutLine(Layout):

    def __init__(self, parent, prev_line):
        Layout.__init__(self)

        self.node = None
        self.parent = parent
        self.prev_line = prev_line
        self.children = list()

    def layout(self):
        self.x = 0
        self.y = 0 if not self.prev_line else self.prev_line.y + self.prev_line.height

        new_children = []
        for child in self.children:
            if isinstance(child, LayoutWord):
                for word_child in child.children:
                    word_child.parent = self
                    new_children.append(word_child)
            else:
                new_children.append(child)
        self.children = new_children

        min_descend = 0
        for child in self.children:
            fontname = FontManager.get_fontname_from_node(child.node)
            min_descend = min(min_descend, FontManager.get_descend(fontname=fontname))

        self.width = 0
        self.height = 0
        for child in self.children:
            fontname = FontManager.get_fontname_from_node(child.node)
            child.x = self.width

            self.width += child.width
            self.height = max(self.height, child.height - min_descend + FontManager.get_descend(fontname=fontname))

        for child in self.children:
            fontname = FontManager.get_fontname_from_node(child.node)
            child.y = self.height - child.height + min_descend - FontManager.get_descend(fontname=fontname)

    def accept_presenter(self, presenter):
        presenter.draw_layout_line(self)


