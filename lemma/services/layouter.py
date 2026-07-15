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

import time

from lemma.services.node_type_db import NodeTypeDB
from lemma.services.text_shaper import TextShaper
from lemma.services.character_db import CharacterDB
from lemma.services.layout_info import LayoutInfo
import lemma.services.timer as timer


class Layouter():

    document = None
    font_theme = None
    preedit_string = ''
    layouts = dict()
    paragraph_with_preedit = None

    line_layouts_by_y = dict()
    leaf_layouts_by_xy = dict()

    last_updated = 0
    is_valid = False

    current_paragraph_style = None
    current_node_layouts = dict()

    def get_height():
        Layouter.update_layout()

        layout = Layouter.get_paragraph_layout(Layouter.document.ast[-1])
        return layout['y'] + layout['height']

    def get_width():
        Layouter.update_layout()

        return Layouter.get_paragraph_layout(Layouter.document.ast[0])['width']

    def get_paragraph_layout(paragraph):
        Layouter.update_layout()

        if paragraph in Layouter.layouts:
            return Layouter.layouts[paragraph]['paragraph']
        return None

    def get_node_layout(node):
        Layouter.update_layout()

        paragraph = node.paragraph()
        if paragraph in Layouter.layouts and node in Layouter.layouts[paragraph]['nodes']:
            return Layouter.layouts[paragraph]['nodes'][node]
        return None

    def get_leaf_layout_at_xy(x, y):
        Layouter.update_layout()

        if (x, y) not in Layouter.leaf_layouts_by_xy:
            line = Layouter.get_line_layout_at_y(y)

            Layouter.leaf_layouts_by_xy[(x, y)] = None
            if y >= line['y'] + line['parent']['y'] and y < line['y'] + line['parent']['y'] + line['height']:
                for layout in Layouter.flatten_layout(line):
                    if layout['node'] != None and layout['node'].type in {'char', 'widget', 'placeholder', 'eol', 'end'}:
                        layout_x, layout_y = Layouter.get_absolute_xy(layout)
                        if x >= layout_x and x <= layout_x + layout['width'] and y >= layout_y and y <= layout_y + layout['height']:
                            Layouter.leaf_layouts_by_xy[(x, y)] = layout

        return Layouter.leaf_layouts_by_xy[(x, y)]

    def get_cursor_holding_layout_close_to_xy(x, y):
        Layouter.update_layout()

        if y < 0: x = 0
        if y > Layouter.get_height(): x = LayoutInfo.get_max_layout_width()

        hbox = Layouter.get_line_layout_at_y(y)
        if y >= hbox['y'] + hbox['parent']['y'] and y < hbox['y'] + hbox['parent']['y'] + hbox['height']:
            for layout in Layouter.flatten_layout(hbox):
                if layout['type'] == 'hbox':
                    layout_x, layout_y = Layouter.get_absolute_xy(layout)
                    if x >= layout_x and x <= layout_x + layout['width'] \
                            and y >= layout_y and y <= layout_y + layout['height'] \
                            and hbox in Layouter.get_ancestors(layout):
                        hbox = layout

        closest_layout = None
        min_distance = 10000
        for layout in hbox['children']:
            layout_x, layout_y = Layouter.get_absolute_xy(layout)
            distance = abs(layout_x - x)
            if distance < min_distance:
                closest_layout = layout
                min_distance = distance

        return closest_layout

    def get_line_layout_at_y(y):
        Layouter.update_layout()

        if y not in Layouter.line_layouts_by_y:
            if y < 0:
                layout = Layouter.get_paragraph_layout(Layouter.document.ast[0])
                Layouter.line_layouts_by_y[y] = layout['children'][0]
            elif y > Layouter.get_height():
                layout = Layouter.get_paragraph_layout(Layouter.document.ast[-1])
                Layouter.line_layouts_by_y[y] = layout['children'][-1]
            else:
                for paragraph in Layouter.document.ast:
                    layout = Layouter.get_paragraph_layout(paragraph)
                    if y >= layout['y'] and y < layout['y'] + layout['height']:
                        for line in layout['children']:
                            if y - layout['y'] >= line['y'] and y - layout['y'] < line['y'] + line['height']:
                                Layouter.line_layouts_by_y[y] = line

        return Layouter.line_layouts_by_y[y]

    def flatten_layout(layout_tree):
        result = [layout_tree]
        for child in layout_tree['children']:
            result += Layouter.flatten_layout(child)
        return result

    def get_ancestors(layout):
        ancestors = []
        while layout['parent'] != None:
            ancestors.append(layout['parent'])
            layout = layout['parent']
        return ancestors

    def get_absolute_xy(layout):
        x, y = (0, 0)
        while not layout == None:
            x += layout['x']
            y += layout['y']
            layout = layout['parent']

        return x, y

    def update_document(document):
        if document != Layouter.document:
            Layouter.document = document

            Layouter.layouts = dict()
            Layouter.is_valid = False

    def update_font_theme(font_theme):
        if font_theme != Layouter.font_theme:
            Layouter.font_theme = font_theme

            Layouter.layouts = dict()
            Layouter.is_valid = False

    def update_preedit(preedit_string):
        if preedit_string != Layouter.preedit_string:
            Layouter.preedit_string = preedit_string

            insert = Layouter.document.get_insert_node()
            paragraph = insert.paragraph()
            if paragraph in Layouter.layouts:
                del(Layouter.layouts[paragraph])
            if Layouter.paragraph_with_preedit in Layouter.layouts:
                del(Layouter.layouts[Layouter.paragraph_with_preedit])
                Layouter.paragraph_with_preedit = None
            Layouter.is_valid = False

    @timer.timer
    def update_layout():
        if Layouter.document == None: return
        if Layouter.document.last_modified <= Layouter.last_updated and Layouter.is_valid: return

        insert = Layouter.document.get_insert_node()
        insert_paragraph = insert.paragraph()

        y_offset = 0
        for paragraph in Layouter.document.ast:
            if paragraph not in Layouter.layouts or paragraph.last_modified > Layouter.last_updated:
                indentation = LayoutInfo.get_indentation(paragraph.style, paragraph.indentation_level)
                width = LayoutInfo.get_max_layout_width() - indentation

                layout_tree, node_layouts = Layouter.make_layout_tree_paragraph(Layouter.document.ast, paragraph)
                if paragraph == insert_paragraph:
                    if len(Layouter.preedit_string) > 0:
                        Layouter.add_preedit(layout_tree, insert, Layouter.preedit_string)
                        Layouter.paragraph_with_preedit = paragraph

                Layouter.layout_paragraph(layout_tree, width, indentation)
                Layouter.layouts[paragraph] = {'paragraph': layout_tree, 'nodes': node_layouts}
            else:
                layout_tree = Layouter.layouts[paragraph]['paragraph']
            layout_tree['y'] = y_offset
            y_offset += layout_tree['height']

        Layouter.line_layouts_by_y = dict()
        Layouter.leaf_layouts_by_xy = dict()
        Layouter.last_updated = time.time()
        Layouter.is_valid = True

    @timer.timer
    def make_layout_tree_paragraph(root, paragraph):
        Layouter.current_paragraph_style = paragraph.style
        Layouter.current_node_layouts = dict()

        layout_tree = {'type': 'paragraph',
                       'fixed': False,
                       'node': paragraph,
                       'parent': None,
                       'children': [],
                       'x': 0,
                       'y': 0,
                       'width': 0,
                       'height': 0,
                       'fontname': None}

        for child in Layouter.group_words(paragraph.children):
            if isinstance(child, list):
                char_nodes = child
                text = ''.join([char.value for char in char_nodes])
                fontname = Layouter.get_fontname_from_node(char_nodes[0])
                subtree = {'type': 'word', 'fixed': False, 'node': root, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'fontname': fontname}
                for char_node, extents in zip(char_nodes, TextShaper.measure(text, fontname=fontname)):
                    subsubtree = {'type': 'char', 'fixed': True, 'node': char_node, 'parent': subtree, 'children': [], 'x': 0, 'y': 0, 'width': extents[0], 'height': extents[1], 'fontname': fontname}
                    Layouter.current_node_layouts[char_node] = subsubtree
                    subtree['children'].append(subsubtree)
            else:
                subtree = Layouter.make_layout_tree(child, layout_tree)

            layout_tree['children'].append(subtree)

        return layout_tree, Layouter.current_node_layouts

    def make_layout_tree(node, parent=None):
        if node.type == 'char':
            fontname = Layouter.get_fontname_from_node(node)
            width, height = TextShaper.measure(node.value, fontname=fontname)[0]
            layout_tree = {'type': 'char', 'fixed': True, 'node': node, 'parent': parent, 'children': [], 'x': 0, 'y': 0, 'width': width, 'height': height, 'fontname': fontname}
            Layouter.current_node_layouts[node] = layout_tree
            return layout_tree

        layout_tree = {'type': None,
                       'fixed': False,
                       'node': node,
                       'parent': parent,
                       'children': [],
                       'x': 0,
                       'y': 0,
                       'width': 0,
                       'height': 0,
                       'fontname': None}

        if node.type == 'eol':
            layout_tree['type'] = 'eol'
            layout_tree['fixed'] = True
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            layout_tree['width'] = 1
            width, height = TextShaper.measure_single('\n', fontname=layout_tree['fontname'])
            layout_tree['height'] = height
            Layouter.current_node_layouts[node] = layout_tree
        elif node.type == 'end':
            layout_tree['type'] = 'end'
            layout_tree['fixed'] = True
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            layout_tree['width'] = 1
            width, height = TextShaper.measure_single('\n', fontname=layout_tree['fontname'])
            layout_tree['height'] = height
            Layouter.current_node_layouts[node] = layout_tree
        elif node.type == 'placeholder':
            layout_tree['type'] = 'placeholder'
            layout_tree['fixed'] = True
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            width, height = TextShaper.measure_single('▯', fontname=layout_tree['fontname'])
            layout_tree['width'] = width
            layout_tree['height'] = height
            Layouter.current_node_layouts[node] = layout_tree
        elif node.type == 'widget':
            layout_tree['type'] = 'widget'
            layout_tree['fixed'] = True
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            Layouter.current_node_layouts[node] = layout_tree
            width, height = layout_tree['node'].value.get_allocation(layout_tree['fontname'])
            layout_tree['width'] = width
            layout_tree['height'] = height
        elif node.type == 'mathscript':
            layout_tree['type'] = 'mathscript'
            layout_tree['fixed'] = False
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            Layouter.current_node_layouts[node] = layout_tree
        elif node.type == 'mathfraction':
            layout_tree['type'] = 'mathfraction'
            layout_tree['fixed'] = False
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            Layouter.current_node_layouts[node] = layout_tree
        elif node.type == 'mathroot':
            layout_tree['type'] = 'mathroot'
            layout_tree['fixed'] = False
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
            Layouter.current_node_layouts[node] = layout_tree
        elif node.type == 'mathlist':
            layout_tree['type'] = 'hbox'
            layout_tree['fixed'] = False
            layout_tree['fontname'] = Layouter.get_fontname_from_node(node)
        else:
            return None

        for child in node:
            subtree = Layouter.make_layout_tree(child, layout_tree)
            if subtree != None:
                layout_tree['children'].append(subtree)

        return layout_tree

    def add_preedit(layout_tree, insert, preedit_string):
        for i, child in enumerate(layout_tree['children']):
            if child['node'] == insert:
                fontname = Layouter.get_fontname_from_node(child['node'])

                width, height = TextShaper.measure(preedit_string, fontname=fontname)[0]
                layout_tree['children'].insert(i, {'type': 'preedit', 'fixed': False, 'node': child['node'], 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': width, 'height': height, 'fontname': fontname})
                break

            Layouter.add_preedit(child, insert, preedit_string)

    @timer.timer
    def group_words(nodes):
        last_type = None
        last_tags = set()
        result = list()
        for node in nodes:
            if node.type != 'char' or NodeTypeDB.is_whitespace(node) or CharacterDB.is_mathsymbol(node.value) or CharacterDB.is_emoji(node.value):
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

    def layout_tree(layout_tree):
        if layout_tree['type'] == 'word': Layouter.layout_word(layout_tree)
        elif layout_tree['type'] == 'hbox': Layouter.layout_hbox(layout_tree)
        elif layout_tree['type'] == 'vbox': Layouter.layout_vbox(layout_tree)
        elif layout_tree['type'] == 'mathscript': Layouter.layout_mathscript(layout_tree)
        elif layout_tree['type'] == 'mathfraction': Layouter.layout_mathfraction(layout_tree)
        elif layout_tree['type'] == 'mathroot': Layouter.layout_mathroot(layout_tree)

    def layout_word(layout_tree):
        layout_tree['width'] = 0
        layout_tree['height'] = 0
        for child in layout_tree['children']:
            child['x'] = layout_tree['width']

            layout_tree['width'] += child['width']
            layout_tree['height'] = max(layout_tree['height'], child['height'])

    @timer.timer
    def layout_paragraph(layout_tree, layout_width, indentation):
        for child in layout_tree['children']:
            if not child['fixed']:
                Layouter.layout_tree(child)

        lines = list()
        current_line = {'type': 'hbox', 'fixed': False, 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'fontname': None}
        current_line_width = 0
        for child in layout_tree['children']:
            if child['type'] == 'eol' or child['type'] == 'end':
                current_line['children'].append(child)
                child['parent'] = current_line
            else:
                break_after_char = (child['type'] == 'char' and NodeTypeDB.is_whitespace(child['node']))
                if break_after_char:
                    current_line['children'].append(child)
                    child['parent'] = current_line
                    current_line_width += child['width']
                    if current_line_width > 0 and child['width'] + current_line_width > layout_width:
                        lines.append(current_line)
                        current_line = {'type': 'hbox', 'fixed': False, 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'fontname': None}
                        current_line_width = 0
                else:
                    if current_line_width > 0 and child['width'] + current_line_width > layout_width:
                        lines.append(current_line)
                        current_line = {'type': 'hbox', 'fixed': False, 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'fontname': None}
                        current_line_width = 0
                    current_line['children'].append(child)
                    child['parent'] = current_line
                    current_line_width += child['width']
        lines.append(current_line)

        layout_tree['height'] = 0
        for line in lines:
            Layouter.layout_hbox(line)
            line['x'] = indentation
            line['y'] = layout_tree['height']
            layout_tree['height'] += line['height']
        layout_tree['children'] = lines
        layout_tree['width'] = layout_width
        layout_tree['x'] = 0
        layout_tree['y'] = 0

    def layout_vbox(layout_tree):
        for child in layout_tree['children']:
            if not child['fixed']:
                Layouter.layout_tree(child)

        layout_tree['width'] = 0
        layout_tree['height'] = 0
        for child in layout_tree['children']:
            child['x'] = 0
            child['y'] = layout_tree['height']

            layout_tree['height'] += child['height']
            layout_tree['width'] = max(layout_tree['width'], child['width'])

        layout_tree['x'] = None
        layout_tree['y'] = None

    def layout_hbox(layout_tree):
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
            if not child['fixed']:
                Layouter.layout_tree(child)

        min_descend = 0
        for child in layout_tree['children']:
            min_descend = min(min_descend, TextShaper.get_descend(fontname=child['fontname']))

        for child in layout_tree['children']:
            child['height'] -= min_descend - TextShaper.get_descend(fontname=child['fontname'])

        layout_tree['width'] = 0
        layout_tree['height'] = 0
        for child in layout_tree['children']:
            child['x'] = layout_tree['width']

            layout_tree['width'] += child['width']
            layout_tree['height'] = max(layout_tree['height'], child['height'] - min_descend + TextShaper.get_descend(fontname=child['fontname']))

        for child in layout_tree['children']:
            child['y'] = layout_tree['height'] - child['height']

    def layout_mathscript(layout_tree):
        if len(layout_tree['children']) == 2:
            for child in layout_tree['children']:
                if not child['fixed']:
                    Layouter.layout_tree(child)

            vbox = {'type': 'vbox', 'fixed': False, 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'fontname': None}
            height = 0
            for child in layout_tree['children']:
                child['parent'] = vbox
                child['x'] = 0
                child['y'] = height
                height += child['height']
                vbox['children'].insert(0, child)

            layout_tree['children'] = [vbox]

        for child in layout_tree['children']:
            if not child['fixed']:
                Layouter.layout_tree(child)

        if layout_tree['children'][0]['children'][0]['height'] == 0:
            layout_tree['children'][0]['children'][0]['height'] = layout_tree['children'][0]['children'][1]['height']
            layout_tree['children'][0]['children'][1]['y'] = layout_tree['children'][0]['children'][1]['height']
            layout_tree['children'][0]['height'] += layout_tree['children'][0]['children'][0]['height']

        if layout_tree['children'][0]['children'][1]['height'] == 0:
            layout_tree['children'][0]['children'][1]['height'] = layout_tree['children'][0]['children'][0]['height']
            layout_tree['children'][0]['height'] += layout_tree['children'][0]['children'][1]['height']

        fontname = Layouter.get_fontname_from_node(layout_tree['node'])
        extents = TextShaper.measure_single(' ', fontname=fontname)

        layout_tree['children'][0]['x'] = 1
        layout_tree['children'][0]['y'] = extents[1] / 2 - layout_tree['children'][0]['height'] / 2

        layout_tree['width'] = layout_tree['children'][0]['width'] + 1
        layout_tree['height'] = layout_tree['children'][0]['height']
        layout_tree['x'] = None
        layout_tree['y'] = None

    def layout_mathfraction(layout_tree):
        if len(layout_tree['children']) == 2:
            for child in layout_tree['children']:
                if not child['fixed']:
                    Layouter.layout_tree(child)

            vbox = {'type': 'vbox', 'fixed': False, 'node': None, 'parent': layout_tree, 'children': [], 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'fontname': None}
            height = 0
            for child in layout_tree['children']:
                child['parent'] = vbox
                child['x'] = 0
                child['y'] = height
                height += child['height']
                vbox['children'].append(child)

            layout_tree['children'] = [vbox]

        for child in layout_tree['children']:
            if not child['fixed']:
                Layouter.layout_tree(child)

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

        fontname = Layouter.get_fontname_from_node(layout_tree['node'])
        extents = TextShaper.measure_single(' ', fontname=fontname)

        layout_tree['children'][0]['x'] = 1
        layout_tree['children'][0]['y'] = extents[1] / 2 - layout_tree['children'][0]['height'] / 2

        layout_tree['width'] = layout_tree['children'][0]['width'] + 2
        layout_tree['height'] = layout_tree['children'][0]['height']
        layout_tree['x'] = None
        layout_tree['y'] = None

    def layout_mathroot(layout_tree):
        for child in layout_tree['children']:
            if not child['fixed']:
                Layouter.layout_tree(child)

        layout_tree['children'][0]['x'] = max(7, layout_tree['children'][1]['width']) + 10
        layout_tree['children'][0]['y'] = 0
        layout_tree['children'][1]['x'] = 1
        layout_tree['children'][1]['y'] = layout_tree['children'][0]['height'] - 13 - layout_tree['children'][1]['height']

        layout_tree['width'] = layout_tree['children'][0]['width'] + max(7, layout_tree['children'][1]['width']) + 10
        layout_tree['height'] = layout_tree['children'][0]['height']
        layout_tree['x'] = None
        layout_tree['y'] = None

    def get_fontname_from_node(node=None):
        if NodeTypeDB.is_subscript(node) or NodeTypeDB.is_superscript(node):
            return 'math_small'
        if NodeTypeDB.in_fraction(node):
            return 'math_small'
        if node.type == 'char' and CharacterDB.is_mathsymbol(node.value):
            return 'math'
        if node.type == 'placeholder':
            return 'math'

        if node.type == 'char' and CharacterDB.is_emoji(node.value):
            return 'emojis'

        if Layouter.current_paragraph_style.startswith('h'):
            return Layouter.current_paragraph_style

        if 'verbatim' in node.tags: return 'mono'
        if 'bold' in node.tags and 'italic' not in node.tags: return 'bold'
        if 'bold' in node.tags and 'italic' in node.tags: return 'bolditalic'
        if 'bold' not in node.tags and 'italic' in node.tags: return 'italic'

        return 'body'


