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
from lemma.document.layout.layout import Layout


class LayoutMathList(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        for child in self.children:
            child.layout()

        min_descend = 0
        for child in self.children:
            fontname = FontManager.get_fontname_from_node(child.node)
            min_descend = min(min_descend, FontManager.get_descend(fontname=fontname))

        for child in self.children:
            fontname = FontManager.get_fontname_from_node(child.node)
            child.height -= min_descend - FontManager.get_descend(fontname=fontname)

        self.width = 0
        self.height = 0
        for child in self.children:
            child.x = self.width

            self.width += child.width
            self.height = max(self.height, child.height)

        for child in self.children:
            child.y = self.height - child.height

    def accept_presenter(self, presenter):
        presenter.draw_layout(self)


