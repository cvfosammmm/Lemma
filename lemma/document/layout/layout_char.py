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


class LayoutChar(Layout):

    def __init__(self, node, parent, extents=None):
        Layout.__init__(self)

        self.node = node
        node.layout = self
        self.extents = extents

        self.parent = parent
        self.children = list()

    def layout(self):
        if self.extents == None:
            fontname = FontManager.get_fontname_from_node(self.node)
            self.extents = FontManager.measure_single(self.node.value, fontname=fontname)

        self.width, self.height, self.left, self.top = self.extents
        self.x = None
        self.y = None


