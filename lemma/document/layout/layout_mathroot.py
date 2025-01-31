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

from lemma.document.layout.layout import Layout


class LayoutMathRoot(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        for child in self.children:
            child.layout()

        self.children[0].x = max(7, self.children[1].width) + 10
        self.children[0].y = 0
        self.children[1].x = 1
        self.children[1].y = self.children[0].height - 13 - self.children[1].height

        self.width = self.children[0].width + max(7, self.children[1].width) + 10
        self.height = self.children[0].height
        self.x = None
        self.y = None


