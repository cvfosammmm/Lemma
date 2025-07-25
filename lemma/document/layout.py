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
from lemma.db.character_db import CharacterDB
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
        self.layout(layout_tree)
        self.document.layout = layout_tree

    @timer.timer
    def make_layout_tree(self, node, parent=None):
        layout_tree = {'type': None,
                       'node': None,
                       'parent': parent,
                       'children': [],
                       'x': 0,
                       'y': 0,
                       'width': 0,
                       'height': 0,
                       'left': 0,
                       'top': 0}

        if node.type == 'char':
            layout_tree['type'] = 'char'
            layout_tree['node'] = node
            layout_tree['width'], layout_tree['height'], layout_tree['left'], layout_tree['top'] = FontManager.measure_single(node.value, fontname=FontManager.get_fontname_from_node(node))
            node.layout = layout_tree
        elif node.type == 'eol':
            layout_tree['type'] = 'eol'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'end':
            layout_tree['type'] = 'end'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'placeholder':
            layout_tree['type'] = 'placeholder'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'widget':
            layout_tree['type'] = 'widget'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'mathscript':
            layout_tree['type'] = 'mathscript'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'mathfraction':
            layout_tree['type'] = 'mathfraction'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'mathroot':
            layout_tree['type'] = 'mathroot'
            layout_tree['node'] = node
            node.layout = layout_tree
        elif node.type == 'mathlist':
            layout_tree['type'] = 'hbox'
            layout_tree['node'] = node
        elif node.type == 'root':
            layout_tree['type'] = 'document'
            layout_tree['node'] = node
            node.layout = layout_tree
        else:
            return None

        if node.type == 'root':
            for child in self.group_words(node):
                if isinstance(child, list):
                    subtree = {'type': 'word', 'node': node, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                    char_nodes = child
                    text = ''.join([char.value for char in char_nodes])
                    fontname = FontManager.get_fontname_from_node(char_nodes[0])
                    for char_node, extents in zip(char_nodes, FontManager.measure(text, fontname=fontname)):
                        subsubtree = {'type': 'char', 'node': char_node, 'parent': subtree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                        subsubtree['width'], subsubtree['height'], subsubtree['left'], subsubtree['top'] = extents
                        char_node.layout = subsubtree
                        subtree['children'].append(subsubtree)
                else:
                    subtree = self.make_layout_tree(child, layout_tree)
                if subtree != None:
                    layout_tree['children'].append(subtree)
        else:
            for child in node:
                subtree = self.make_layout_tree(child, layout_tree)
                if subtree != None:
                    layout_tree['children'].append(subtree)

        return layout_tree

    @timer.timer
    def group_words(self, parent_node):
        last_type = None
        last_tags = set()
        result = list()
        for node in parent_node:
            if node.type != 'char' or node.is_whitespace() or CharacterDB.is_mathsymbol(node.value) or CharacterDB.is_emoji(node.value):
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

    def layout(self, layout_tree):
        if layout_tree['type'] == 'document':
            for child in layout_tree['children']:
                self.layout(child)

            lines = list()
            current_line = {'type': 'hbox', 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
            current_line_width = 0
            for child in layout_tree['children']:
                if child['type'] == 'eol':
                    current_line['children'].append(child)
                    child['parent'] = current_line
                    lines.append(current_line)
                    current_line = {'type': 'hbox', 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                    current_line_width = 0
                else:
                    break_after_char = (child['type'] == 'char' and child['node'].is_whitespace()) or child['type'] == 'end' or child['type'] == 'eol'
                    if break_after_char:
                        current_line['children'].append(child)
                        child['parent'] = current_line
                        current_line_width += child['width']
                        if current_line_width > 0 and child['width'] + current_line_width > LayoutInfo.get_layout_width():
                            lines.append(current_line)
                            current_line = {'type': 'hbox', 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                            current_line_width = 0
                    else:
                        if current_line_width > 0 and child['width'] + current_line_width > LayoutInfo.get_layout_width():
                            lines.append(current_line)
                            current_line = {'type': 'hbox', 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                            current_line_width = 0
                        current_line['children'].append(child)
                        child['parent'] = current_line
                        current_line_width += child['width']
            lines.append(current_line)

            layout_tree['height'] = 0
            for line in lines:
                self.layout(line)
                line['x'] = 0
                line['y'] = layout_tree['height']
                layout_tree['height'] += line['height']
            layout_tree['children'] = lines
            layout_tree['width'] = LayoutInfo.get_layout_width()
            layout_tree['x'] = 0
            layout_tree['y'] = 0

        elif layout_tree['type'] == 'vbox':
            for child in layout_tree['children']:
                self.layout(child)

            layout_tree['width'] = 0
            layout_tree['height'] = 0
            for child in layout_tree['children']:
                child['x'] = 0
                child['y'] = layout_tree['height']

                layout_tree['height'] += child['height']
                layout_tree['width'] = max(layout_tree['width'], child['width'])

            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'hbox':
            new_children = []
            for child in layout_tree['children']:
                if child['type'] == 'word':
                    for word_child in child['children']:
                        word_child['parent'] = layout_tree
                        new_children.append(word_child)
                else:
                    new_children.append(child)
            layout_tree['children'] = new_children

            for child in layout_tree['children']:
                self.layout(child)

            min_descend = 0
            for child in layout_tree['children']:
                fontname = FontManager.get_fontname_from_node(child['node'])
                min_descend = min(min_descend, FontManager.get_descend(fontname=fontname))

            for child in layout_tree['children']:
                fontname = FontManager.get_fontname_from_node(child['node'])
                child['height'] -= min_descend - FontManager.get_descend(fontname=fontname)

            layout_tree['width'] = 0
            layout_tree['height'] = 0
            for child in layout_tree['children']:
                fontname = FontManager.get_fontname_from_node(child['node'])
                child['x'] = layout_tree['width']

                layout_tree['width'] += child['width']
                layout_tree['height'] = max(layout_tree['height'], child['height'] - min_descend + FontManager.get_descend(fontname=fontname))

            for child in layout_tree['children']:
                fontname = FontManager.get_fontname_from_node(child['node'])
                child['y'] = layout_tree['height'] - child['height']

        elif layout_tree['type'] == 'mathscript':
            if len(layout_tree['children']) == 2:
                for child in layout_tree['children']:
                    self.layout(child)

                vbox = {'type': 'vbox', 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                height = 0
                for child in layout_tree['children']:
                    child['parent'] = vbox
                    child['x'] = 0
                    child['y'] = height
                    height += child['height']
                    vbox['children'].insert(0, child)

                layout_tree['children'] = [vbox]

            for child in layout_tree['children']:
                self.layout(child)

            if layout_tree['children'][0]['children'][0]['height'] == 0:
                layout_tree['children'][0]['children'][0]['height'] = layout_tree['children'][0]['children'][1]['height']
                layout_tree['children'][0]['children'][1]['y'] = layout_tree['children'][0]['children'][1]['height']
                layout_tree['children'][0]['height'] += layout_tree['children'][0]['children'][0]['height']

            if layout_tree['children'][0]['children'][1]['height'] == 0:
                layout_tree['children'][0]['children'][1]['height'] = layout_tree['children'][0]['children'][0]['height']
                layout_tree['children'][0]['height'] += layout_tree['children'][0]['children'][1]['height']

            fontname = FontManager.get_fontname_from_node(layout_tree['node'])
            extents = FontManager.measure_single(' ', fontname=fontname)

            layout_tree['children'][0]['x'] = 1
            layout_tree['children'][0]['y'] = extents[1] / 2 - layout_tree['children'][0]['height'] / 2

            layout_tree['width'] = layout_tree['children'][0]['width'] + 1
            layout_tree['height'] = layout_tree['children'][0]['height']
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'mathfraction':
            if len(layout_tree['children']) == 2:
                for child in layout_tree['children']:
                    self.layout(child)

                vbox = {'type': 'vbox', 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'left': 0, 'top': 0}
                height = 0
                for child in layout_tree['children']:
                    child['parent'] = vbox
                    child['x'] = 0
                    child['y'] = height
                    height += child['height']
                    vbox['children'].append(child)

                layout_tree['children'] = [vbox]

            for child in layout_tree['children']:
                self.layout(child)

            # centering
            if layout_tree['children'][0]['children'][0]['width'] < layout_tree['children'][0]['children'][1]['width']:
                min_child = layout_tree['children'][0]['children'][0]
                padding = (layout_tree['children'][0]['width'] - layout_tree['children'][0]['children'][0]['width']) / 2
            else:
                min_child = layout_tree['children'][0]['children'][1]
                padding = (layout_tree['children'][0]['width'] - layout_tree['children'][0]['children'][1]['width']) / 2
            for child in min_child['children']:
                child['x'] += padding
            layout_tree['children'][0]['children'][0]['width'] = layout_tree['children'][0]['width']
            layout_tree['children'][0]['children'][1]['width'] = layout_tree['children'][0]['width']

            for child in layout_tree['children'][0]['children'][1]['children']:
                child['y'] += 2

            fontname = FontManager.get_fontname_from_node(layout_tree['node'])
            extents = FontManager.measure_single(' ', fontname=fontname)

            layout_tree['children'][0]['x'] = 1
            layout_tree['children'][0]['y'] = extents[1] / 2 - layout_tree['children'][0]['height'] / 2

            layout_tree['width'] = layout_tree['children'][0]['width'] + 2
            layout_tree['height'] = layout_tree['children'][0]['height']
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'mathroot':
            for child in layout_tree['children']:
                self.layout(child)

            layout_tree['children'][0]['x'] = max(7, layout_tree['children'][1]['width']) + 10
            layout_tree['children'][0]['y'] = 0
            layout_tree['children'][1]['x'] = 1
            layout_tree['children'][1]['y'] = layout_tree['children'][0]['height'] - 13 - layout_tree['children'][1]['height']

            layout_tree['width'] = layout_tree['children'][0]['width'] + max(7, layout_tree['children'][1]['width']) + 10
            layout_tree['height'] = layout_tree['children'][0]['height']
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'word':
            for child in layout_tree['children']:
                self.layout(child)

            layout_tree['width'] = 0
            layout_tree['height'] = 0
            for child in layout_tree['children']:
                child['x'] = layout_tree['width']

                layout_tree['width'] += child['width']
                layout_tree['height'] = max(layout_tree['height'], child['height'])

        elif layout_tree['type'] == 'char':
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'placeholder':
            fontname = FontManager.get_fontname_from_node(layout_tree['node'])
            width, height, left, top = FontManager.measure_single('▯', fontname=fontname)

            layout_tree['width'] = width
            layout_tree['height'] = height
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'widget':
            width, height = layout_tree['node'].value.get_width(), layout_tree['node'].value.get_height()
            fontname = FontManager.get_fontname_from_node(layout_tree['node'])
            height -= 2 * FontManager.get_descend(fontname=fontname)

            layout_tree['width'] = width
            layout_tree['height'] = height
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'eol':
            fontname = FontManager.get_fontname_from_node(layout_tree['node'])
            width, height, left, top = FontManager.measure_single('\n', fontname=fontname)

            layout_tree['width'] = 1
            layout_tree['height'] = height
            layout_tree['x'] = None
            layout_tree['y'] = None

        elif layout_tree['type'] == 'end':
            fontname = FontManager.get_fontname_from_node(layout_tree['node'])
            width, height, left, top = FontManager.measure_single('\n', fontname=fontname)

            layout_tree['width'] = 1
            layout_tree['height'] = height
            layout_tree['x'] = None
            layout_tree['y'] = None

    def get_ancestors(self, layout):
        ancestors = []
        while layout['parent'] != None:
            ancestors.append(layout['parent'])
            layout = layout['parent']
        return ancestors

    def get_leaf_at_xy(self, x, y):
        line = self.get_line_at_y(y)

        if y >= line['y'] and y < line['y'] + line['height']:
            for node in [node for node in self.flatten(line) if node['node'] != None and node['node'].is_leaf()]:
                node_x, node_y = self.get_absolute_xy(node)
                if x >= node_x and x <= node_x + node['width'] and y >= node_y and y <= node_y + node['height']:
                    return node
        return None

    def get_cursor_holding_layout_close_to_xy(self, x, y):
        if y < 0: x = 0
        if y > self.document.layout['height']: x = self.document.layout['width']

        hbox = self.get_line_at_y(y)
        if y >= hbox['y'] and y < hbox['y'] + hbox['height']:
            for layout in self.flatten(hbox):
                if layout['type'] == 'hbox':
                    layout_x, layout_y = self.get_absolute_xy(layout)
                    if x >= layout_x and x <= layout_x + layout['width'] \
                            and y >= layout_y and y <= layout_y + layout['height'] \
                            and hbox in self.get_ancestors(layout):
                        hbox = layout

        closest_layout = None
        min_distance = 10000
        for layout in hbox['children']:
            layout_x, layout_y = self.get_absolute_xy(layout)
            distance = abs(layout_x - x)
            if distance < min_distance:
                closest_layout = layout
                min_distance = distance

        return closest_layout

    def flatten(self, layout_tree):
        result = [layout_tree]
        for child in layout_tree['children']:
            result += self.flatten(child)
        return result

    def get_line_at_y(self, y):
        layout = self.document.layout

        if y < 0:
            return layout['children'][0]
        elif y > layout['height']:
            return layout['children'][-1]
        else:
            for child in layout['children']:
                if y >= child['y'] and y < child['y'] + child['height']:
                    return child

    def get_absolute_xy(self, layout):
        x, y = (0, 0)

        while not layout['parent'] == None:
            x += layout['x']
            y += layout['y']
            layout = layout['parent']

        return x, y


