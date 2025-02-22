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
        elif node.type == 'mathscript': layout_tree = LayoutMathScript(node, parent)
        elif node.type == 'mathfraction': layout_tree = LayoutMathFraction(node, parent)
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


class Layout():

    def __init__(self):
        pass

    def get_absolute_xy(self):
        layout = self
        x, y = (0, 0)

        while not layout.parent == None:
            x += layout.x
            y += layout.y
            layout = layout.parent

        return x, y

    def flatten(self):
        result = [self]
        for child in self.children:
            result += child.flatten()
        return result

    def get_ancestors(self):
        ancestors = []
        node = self
        while node.parent != None:
            ancestors.append(node.parent)
            node = node.parent
        return ancestors


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
                break_after_char = (isinstance(child, LayoutChar) and child.node.is_whitespace()) or isinstance(child, LayoutEnd) or isinstance(child, LayoutEOL)
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

    def get_leaf_at_xy(self, x, y):
        line = self.get_line_at_y(y)

        if y >= line.y and y < line.y + line.height:
            for node in [node for node in line.flatten() if node.node != None and node.node.is_leaf()]:
                node_x, node_y = node.get_absolute_xy()
                if x >= node_x and x <= node_x + node.width and y >= node_y and y <= node_y + node.height:
                    return node
        return None

    def get_cursor_holding_layout_close_to_xy(self, x, y):
        if y < 0: x = 0
        if y > self.height: x = self.width

        hbox = self.get_line_at_y(y)
        if y >= hbox.y and y < hbox.y + hbox.height:
            for layout in hbox.flatten():
                if isinstance(layout, LayoutHBox):
                    layout_x, layout_y = layout.get_absolute_xy()
                    if x >= layout_x and x <= layout_x + layout.width \
                            and y >= layout_y and y <= layout_y + layout.height \
                            and hbox in layout.get_ancestors():
                        hbox = layout

        closest_layout = None
        min_distance = 10000
        for layout in hbox.children:
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


class LayoutVBox(Layout):

    def __init__(self, parent):
        Layout.__init__(self)

        self.node = None
        self.parent = parent
        self.children = list()

    def layout(self):
        for child in self.children:
            child.layout()

        self.width = 0
        self.height = 0
        for child in self.children:
            child.x = 0
            child.y = self.height

            self.height += child.height
            self.width = max(self.width, child.width)

        self.x = None
        self.y = None


class LayoutHBox(Layout):

    def __init__(self, parent):
        Layout.__init__(self)

        self.node = None
        self.parent = parent
        self.children = list()

    def layout(self):
        new_children = []
        for child in self.children:
            if isinstance(child, LayoutWord):
                for word_child in child.children:
                    word_child.parent = self
                    new_children.append(word_child)
            else:
                new_children.append(child)
        self.children = new_children

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
            fontname = FontManager.get_fontname_from_node(child.node)
            child.x = self.width

            self.width += child.width
            self.height = max(self.height, child.height - min_descend + FontManager.get_descend(fontname=fontname))

        for child in self.children:
            fontname = FontManager.get_fontname_from_node(child.node)
            child.y = self.height - child.height


class LayoutMathScript(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        if len(self.children) == 2:
            for child in self.children:
                child.layout()

            vbox = LayoutVBox(self)
            height = 0
            for child in self.children:
                child.parent = vbox
                child.x = 0
                child.y = height
                height += child.height
                vbox.children.insert(0, child)

            self.children = [vbox]

        for child in self.children:
            child.layout()

        if self.children[0].children[0].height == 0:
            self.children[0].children[0].height = self.children[0].children[1].height
            self.children[0].children[1].y = self.children[0].children[1].height
            self.children[0].height += self.children[0].children[0].height

        if self.children[0].children[1].height == 0:
            self.children[0].children[1].height = self.children[0].children[0].height
            self.children[0].height += self.children[0].children[1].height

        fontname = FontManager.get_fontname_from_node(self.node)
        extents = FontManager.measure_single(' ', fontname=fontname)

        self.children[0].x = 1
        self.children[0].y = extents[1] / 2 - self.children[0].height / 2

        self.width = self.children[0].width + 1
        self.height = self.children[0].height
        self.x = None
        self.y = None


class LayoutMathFraction(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        if len(self.children) == 2:
            for child in self.children:
                child.layout()

            vbox = LayoutVBox(self)
            height = 0
            for child in self.children:
                child.parent = vbox
                child.x = 0
                child.y = height
                height += child.height
                vbox.children.append(child)

            self.children = [vbox]

        for child in self.children:
            child.layout()

        # centering
        if self.children[0].children[0].width < self.children[0].children[1].width:
            min_child = self.children[0].children[0]
            padding = (self.children[0].width - self.children[0].children[0].width) / 2
            print(padding)
        else:
            min_child = self.children[0].children[1]
            padding = (self.children[0].width - self.children[0].children[1].width) / 2
        for child in min_child.children:
            child.x += padding
        self.children[0].children[0].width = self.children[0].width
        self.children[0].children[1].width = self.children[0].width

        for child in self.children[0].children[1].children:
            child.y += 2

        fontname = FontManager.get_fontname_from_node(self.node)
        extents = FontManager.measure_single(' ', fontname=fontname)

        self.children[0].x = 1
        self.children[0].y = extents[1] / 2 - self.children[0].height / 2

        self.width = self.children[0].width + 2
        self.height = self.children[0].height
        self.x = None
        self.y = None


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


class LayoutWord(Layout):

    def __init__(self, parent):
        Layout.__init__(self)

        self.node = None

        self.parent = parent
        self.children = list()

    def layout(self):
        for child in self.children:
            child.layout()

        self.width = 0
        self.height = 0
        for child in self.children:
            child.x = self.width

            self.width += child.width
            self.height = max(self.height, child.height)


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


class LayoutPlaceholder(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        fontname = FontManager.get_fontname_from_node(self.node)
        width, height, left, top = FontManager.measure_single('▯', fontname=fontname)

        self.width = width
        self.height = height
        self.x = None
        self.y = None


class LayoutWidget(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        width, height = self.node.value.get_width(), self.node.value.get_height()
        fontname = FontManager.get_fontname_from_node(self.node)
        height -= 2 * FontManager.get_descend(fontname=fontname)

        self.width = width
        self.height = height
        self.x = None
        self.y = None


class LayoutEOL(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        fontname = FontManager.get_fontname_from_node(self.node)
        width, height, left, top = FontManager.measure_single('\n', fontname=fontname)

        self.width = 1
        self.height = height
        self.x = None
        self.y = None


class LayoutEnd(Layout):

    def __init__(self, node, parent):
        Layout.__init__(self)

        self.node = node
        node.layout = self

        self.parent = parent
        self.children = list()

    def layout(self):
        fontname = FontManager.get_fontname_from_node(self.node)
        width, height, left, top = FontManager.measure_single('\n', fontname=fontname)

        self.width = 1
        self.height = height
        self.x = None
        self.y = None


