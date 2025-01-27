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

from lemma.infrastructure.layout_info import LayoutInfo
from lemma.document.layout.layout_hbox import LayoutHBox
from lemma.document.layout.layout_eol import LayoutEOL
from lemma.document.layout.layout_char import LayoutChar
from lemma.document.layout.layout import Layout


class LayoutDocument(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        for child in self.children:
            child.layout()

        lines = list()
        current_line = LayoutHBox(self)
        current_line_width = 0
        for child in self.children:
            if isinstance(child, LayoutEOL):
                current_line.children.append(child)
                child.parent = current_line
                lines.append(current_line)
                current_line = LayoutHBox(self)
                current_line_width = 0
            else:
                break_after_char = isinstance(child, LayoutChar) and child.node.is_whitespace()
                if break_after_char:
                    current_line.children.append(child)
                    child.parent = current_line
                    current_line_width += child.width
                    if current_line_width > 0 and child.width + current_line_width > LayoutInfo.get_layout_width():
                        lines.append(current_line)
                        current_line = LayoutHBox(self)
                        current_line_width = 0
                else:
                    if current_line_width > 0 and child.width + current_line_width > LayoutInfo.get_layout_width():
                        lines.append(current_line)
                        current_line = LayoutHBox(self)
                        current_line_width = 0
                    current_line.children.append(child)
                    child.parent = current_line
                    current_line_width += child.width
        lines.append(current_line)

        self.height = 0
        for line in lines:
            line.layout()
            line.x = 0
            line.y = self.height
            self.height += line.height
        self.children = lines
        self.width = LayoutInfo.get_layout_width()
        self.x = 0
        self.y = 0

    def accept_presenter(self, presenter):
        presenter.draw_layout(self)

    def get_leaf_at_xy(self, x, y):
        line = self.get_line_at_y(y)

        if y >= line.y and y < line.y + line.height:
            for node in [node for node in line.flatten() if node.node != None and node.node.is_leaf()]:
                node_x, node_y = node.get_absolute_xy()
                if x >= node_x and x <= node_x + node.width and y >= node_y and y <= node_y + node.height:
                    return node
        return None

    def get_cursor_holding_layout_close_to_xy(self, x, y):
        vbox = self.get_line_at_y(y)
        if y >= vbox.y and y < vbox.y + vbox.height:
            for layout in vbox.flatten():
                if isinstance(layout, LayoutHBox):
                    layout_x, layout_y = layout.get_absolute_xy()
                    if x >= layout_x and x <= layout_x + layout.width \
                            and y >= layout_y and y <= layout_y + layout.height \
                            and vbox in layout.get_ancestors():
                        vbox = layout

        closest_layout = None
        min_distance = 10000
        for layout in vbox.children:
            layout_x, layout_y = layout.get_absolute_xy()
            distance = abs(layout_x - x)
            if distance < min_distance:
                closest_layout = layout
                min_distance = distance

        return closest_layout

    def get_line_at_y(self, y):
        if y < 0:
            return self.children[0]
        elif y > self.height:
            return self.children[-1]
        else:
            for child in self.children:
                if y >= child.y and y < child.y + child.height:
                    return child


