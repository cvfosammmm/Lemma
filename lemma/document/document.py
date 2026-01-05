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

import lemma.services.xml_helpers as xml_helpers
import lemma.services.xml_parser as xml_parser
import lemma.services.xml_exporter as xml_exporter
from lemma.document.ast import Root, Cursor
from lemma.document.command_manager import CommandManager
from lemma.document.layouter import Layouter
from lemma.document.plaintext_scanner import PlaintextScanner
from lemma.services.character_db import CharacterDB
from lemma.document.links_scanner import LinksScanner
from lemma.document.clipping import Clipping
from lemma.document.xml_scanner import XMLScanner
from lemma.services.node_type_db import NodeTypeDB
from lemma.services.layout_info import LayoutInfo
from lemma.application_state.application_state import ApplicationState
import lemma.services.timer as timer


class Document():

    def __init__(self, id=None):
        self.last_modified = time.time()
        self.last_cursor_movement = time.time()
        self.last_scrolling_movement = time.time()

        self.id = id
        self.title = ''
        self.ast = Root()
        self.cursor = Cursor(self, self.ast[0][0], self.ast[0][0])
        self.plaintext = None
        self.xml = None
        self.links = set()

        self.change_flag = dict()
        self.query_cache = dict()

        self.command_manager = CommandManager(self)
        self.layouter = Layouter(self)
        self.clipping = Clipping(self)
        self.plaintext_scanner = PlaintextScanner(self)
        self.links_scanner = LinksScanner(self)
        self.xml_scanner = XMLScanner(self)

    def start_undoable_action(self):
        self.command_manager.start_undoable_action()

    def end_undoable_action(self):
        self.command_manager.end_undoable_action()

    def undoable_action(original_function):
        def new_function(*args, **kwargs):
            start_new_action = args[0].command_manager.current_undoable_action == None
            if start_new_action:
                args[0].command_manager.start_undoable_action()
            original_function(*args, **kwargs)
            if start_new_action:
                args[0].command_manager.end_undoable_action()

        return new_function

    @undoable_action
    def insert_xml(self, xml):
        parser = xml_parser.XMLParser()

        if self.has_selection() and xml.find('<placeholder marks="prev_selection"/>') >= 0:
            if not self.has_multiple_lines_selected():
                prev_selection = self.get_selected_nodes()
                prev_selection_xml = xml_exporter.XMLExporter.export_paragraph(prev_selection)
                xml = xml.replace('<placeholder marks="prev_selection"/>', prev_selection_xml[prev_selection_xml.find('>') + 1:prev_selection_xml.rfind('<')])

        nodes = []
        paragraphs = parser.parse(xml)
        for paragraph in paragraphs:
            nodes += paragraph.nodes

        selection_from = self.get_first_selection_bound()
        selection_to = self.get_last_selection_bound()
        node_before = selection_from.prev_in_parent()
        node_after = selection_to

        self.delete_selected_nodes()
        self.insert_nodes(self.cursor.get_insert_node(), nodes)

        for paragraph in paragraphs:
            if paragraph == paragraphs[0]:
                if node_before != None:
                    continue
                elif node_after.type != 'eol' and len(paragraphs) == 1 and paragraphs[-1].nodes[-1].type != 'eol':
                    continue
            elif paragraph == paragraphs[-1]:
                if node_after != 'eol':
                    continue
                elif node_before != None and len(paragraphs) == 1 and paragraphs[-1].nodes[-1].type != 'eol':
                    continue
            if len(paragraphs) == 1 and paragraphs[-1].nodes[-1].type != 'eol' and not paragraph.style.startswith('h'):
                continue
            if len(paragraphs) == 1 and len(paragraphs[-1].nodes) == 1 and paragraphs[-1].nodes[-1].type == 'eol':
                continue

            self.command_manager.add_command('set_paragraph_style', paragraph.nodes[0].paragraph(), paragraph.style)
            self.command_manager.add_command('set_indentation_level', paragraph.nodes[0].paragraph(), paragraph.indentation_level)

        for paragraph in paragraphs:
            if paragraph.style == 'cl':
                paragraph_in_ast = paragraph.nodes[0].paragraph()
                self.command_manager.add_command('set_paragraph_state', paragraph_in_ast, paragraph.state)

        placeholder_found = False
        for node_list in (node.flatten() for node in nodes):
            for node in node_list:
                if node.type == 'placeholder':
                    self.select_node(node)

                    placeholder_found = True
                    break
            if placeholder_found:
                break

        self.command_manager.add_command('update_implicit_x_position')

    @undoable_action
    def insert_nodes(self, cursor, nodes):
        self.command_manager.add_command('insert', cursor, nodes)

    @undoable_action
    def replace_max_string_before_cursor(self):
        insert_node = self.cursor.get_insert_node()
        last_node = insert_node.prev()
        first_node = last_node
        for i in range(5):
            prev_node = first_node.prev_in_parent()
            if prev_node != None and prev_node.type == 'char':
                first_node = prev_node
            else:
                break

        subtree = self.get_subtree(first_node, last_node)
        chars = ''.join([node.value for node in subtree])
        if len(chars) >= 2:
            for i in range(len(chars) - 1):
                if CharacterDB.has_replacement(chars[i:]):
                    length = len(chars) - i
                    text = xml_helpers.escape(CharacterDB.get_replacement(chars[i:]))
                    xml = xml_helpers.embellish_with_link_and_tags(text, None, first_node.tags)
                    parser = xml_parser.XMLParser()
                    start_node = last_node
                    for i in range(length):
                        start_node = start_node.prev_in_parent()

                    nodes = []
                    paragraphs = parser.parse(xml)
                    for paragraph in paragraphs:
                        nodes += paragraph.nodes

                    self.command_manager.add_command('delete', start_node, last_node)
                    self.command_manager.add_command('insert', last_node, nodes)
                    self.command_manager.add_command('move_cursor_to_node', insert_node)
                    self.command_manager.add_command('update_implicit_x_position')

    @undoable_action
    def delete_selected_nodes(self):
        node_from = self.get_first_selection_bound()
        node_to = self.get_last_selection_bound()
        self.delete_nodes(node_from, node_to)

    @undoable_action
    def delete_nodes(self, node_from, node_to):
        self.command_manager.add_command('delete', node_from, node_to)

    @undoable_action
    def resize_widget(self, node, new_width):
        if node.type != 'widget': return

        self.command_manager.add_command('resize_widget', node, new_width)

    @undoable_action
    def add_tag(self, tagname):
        self.command_manager.add_command('add_tag', tagname)

    @undoable_action
    def remove_tag(self, tagname):
        self.command_manager.add_command('remove_tag', tagname)

    @undoable_action
    def set_link(self, bounds, target):
        char_nodes = [node for node in self.get_subtree(*bounds) if node.type == 'char']

        self.command_manager.add_command('set_link', char_nodes, target)

    @undoable_action
    def set_paragraph_style(self, paragraph, style):
        self.command_manager.add_command('set_paragraph_style', paragraph, style)

    @undoable_action
    def set_indentation_level(self, paragraph, level):
        self.command_manager.add_command('set_indentation_level', paragraph, level)

    @undoable_action
    def set_paragraph_state(self, paragraph, state):
        self.command_manager.add_command('set_paragraph_state', paragraph, state)

    @timer.timer
    def set_insert_and_selection_node(self, new_insert, new_selection_bound=None):
        self.command_manager.add_command('move_cursor_to_node', new_insert, new_selection_bound)

    def move_cursor_to_xy(self, x, y, do_selection):
        self.command_manager.add_command('move_cursor_to_xy', x, y, do_selection)

    def select_node(self, node):
        next_node = node.next_in_parent()
        self.command_manager.add_command('move_cursor_to_node', node, next_node)

    def update_implicit_x_position(self):
        self.command_manager.add_command('update_implicit_x_position')

    def scroll_insert_on_screen(self, window_height, animation_type=None):
        insert_node = self.cursor.get_insert_node()
        insert_position = self.get_absolute_xy(insert_node.layout)

        content_offset = LayoutInfo.get_normal_document_offset()
        insert_y = insert_position[1] + content_offset
        insert_height = insert_node.layout['height']
        scrolling_offset_y = self.get_current_scrolling_offsets()[1]
        content_height = self.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

        if window_height <= 0:
            new_position = (0, 0)
        elif self.get_absolute_xy(self.get_line_layout_at_y(insert_position[1]))[1] == 0:
            new_position = (0, 0)
        elif insert_y < scrolling_offset_y:
            if insert_height > window_height:
                new_position = (0, insert_y - window_height + insert_height)
            else:
                new_position = (0, insert_y)
        elif insert_position[1] >= self.get_height() - insert_height and content_height >= window_height:
            new_position = (0, self.get_height() + content_offset + LayoutInfo.get_document_padding_bottom() - window_height)
        elif insert_y > scrolling_offset_y - insert_height + window_height:
            new_position = (0, insert_y - window_height + insert_height)
        else:
            new_position = self.clipping.get_target_offsets()

        if new_position[0] != self.clipping.target_x or new_position[1] != self.clipping.target_y:
            self.command_manager.add_command('scroll_to_xy', *new_position, animation_type)

    def scroll_to_xy(self, x, y, animation_type=None):
        self.command_manager.add_command('scroll_to_xy', x, y, animation_type)

    def undo(self):
        self.command_manager.undo()

    def redo(self):
        self.command_manager.redo()

    def update_last_modified(self):
        for client in self.change_flag:
            self.change_flag[client] = True

        self.last_modified = time.time()
        self.last_cursor_movement = time.time()
        self.query_cache = dict()

    def update_last_cursor_movement(self):
        self.last_cursor_movement = time.time()
        self.query_cache = dict()

    def update_last_scrolling_movement(self):
        self.last_scrolling_movement = time.time()
        self.query_cache = dict()

    @timer.timer
    def update(self):
        self.layouter.update()
        self.plaintext_scanner.update()
        self.links_scanner.update()
        self.xml_scanner.update()

    def has_changed(self, client):
        if client not in self.change_flag:
            self.change_flag[client] = True

        result = self.change_flag[client]
        self.change_flag[client] = False
        return result

    def has_multiple_lines_selected(self):
        if 'multiple_lines_selected' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['multiple_lines_selected'] = any(node.type == 'eol' for node in selected_nodes)
        return self.query_cache['multiple_lines_selected']

    def cursor_at_paragraph_start(self):
        if 'cursor_at_paragraph_start' not in self.query_cache:
            insert = self.cursor.get_insert_node()
            self.query_cache['cursor_at_paragraph_start'] = (insert == insert.paragraph_start())
        return self.query_cache['cursor_at_paragraph_start']

    def cursor_inside_link(self):
        if 'cursor_inside_link' not in self.query_cache:
            self.query_cache['cursor_inside_link'] = (not self.has_selection() and self.cursor.get_insert_node().is_inside_link())
        return self.query_cache['cursor_inside_link']

    def links_inside_selection(self):
        if 'links_inside_selection' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['links_inside_selection'] = any(node.link != None for node in selected_nodes)
        return self.query_cache['links_inside_selection']

    def whole_selection_is_one_link(self):
        if 'whole_selection_is_one_link' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['whole_selection_is_one_link'] = self.links_inside_selection() and all(node.link == selected_nodes[0].link for node in selected_nodes)
        return self.query_cache['whole_selection_is_one_link']

    def widget_selected(self):
        if 'widget_selected' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['widget_selected'] = (len(selected_nodes) == 1 and selected_nodes[0].type == 'widget')
        return self.query_cache['widget_selected']

    def selected_widget_is_max(self):
        if 'selected_widget_is_max' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['selected_widget_is_max'] = (self.widget_selected() and (selected_nodes[0].value.get_width() == LayoutInfo.get_max_layout_width() or not selected_nodes[0].value.is_resizable()))
        return self.query_cache['selected_widget_is_max']

    def selected_widget_is_min(self):
        if 'selected_widget_is_min' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['selected_widget_is_min'] = (self.widget_selected() and (selected_nodes[0].value.get_width() == selected_nodes[0].value.get_minimum_width() or not selected_nodes[0].value.is_resizable()))
        return self.query_cache['selected_widget_is_min']

    def get_insert_node(self):
        return self.cursor.get_insert_node()

    def get_selection_node(self):
        return self.cursor.get_selection_node()

    def insert_parent_is_root(self):
        if 'insert_parent_is_root' not in self.query_cache:
            self.query_cache['insert_parent_is_root'] = (self.cursor.get_insert_node().parent.type == 'paragraph')
        return self.query_cache['insert_parent_is_root']

    def has_selection(self):
        if 'has_selection' not in self.query_cache:
            self.query_cache['has_selection'] = self.cursor.has_selection()
        return self.query_cache['has_selection']

    def get_selected_nodes(self):
        if 'selected_nodes' not in self.query_cache:
            bounds = self.get_insert_node(), self.get_selection_node()
            self.query_cache['selected_nodes'] = self.get_subtree(*bounds)
        return self.query_cache['selected_nodes']

    @timer.timer
    def get_subtree(self, node1, node2):
        pos1 = node1.get_position()
        pos2 = node2.get_position()

        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        parent1, parent2 = self.get_node_at_position(pos1[:-1]), self.get_node_at_position(pos2[:-1])

        # this can happen, when the selection stretches over multiple paragraphs
        if parent1 != parent2:
            result = parent1[pos1[-1]:]
            for paragraph in self.ast[pos1[0] + 1:pos2[0]]:
                result += paragraph.nodes
            result += parent2[:pos2[-1]]
            return result
        else:
            return parent1[pos1[-1]:pos2[-1]]

    def get_node_at_position(self, pos):
        node = self.ast
        for index in pos:
            node = node[index]
        return node

    def get_first_selection_bound(self):
        if 'selection_bounds' not in self.query_cache:
            self.query_cache['selection_bounds'] = self.cursor.get_first_and_last_node()
        return self.query_cache['selection_bounds'][0]

    def get_last_selection_bound(self):
        if 'selection_bounds' not in self.query_cache:
            self.query_cache['selection_bounds'] = self.cursor.get_first_and_last_node()
        return self.query_cache['selection_bounds'][1]

    def get_implicit_x_position(self):
        return self.cursor.implicit_x_position

    def can_undo(self):
        if 'can_undo' not in self.query_cache:
            self.query_cache['can_undo'] = self.command_manager.can_undo()
        return self.query_cache['can_undo']

    def can_redo(self):
        if 'can_redo' not in self.query_cache:
            self.query_cache['can_redo'] = self.command_manager.can_redo()
        return self.query_cache['can_redo']

    def get_height(self):
        if 'height' not in self.query_cache:
            self.query_cache['height'] = self.ast[-1].layout['y'] + self.ast[-1].layout['height']
        return self.query_cache['height']

    def get_width(self):
        return self.ast[0].layout['width']

    def get_current_scrolling_offsets(self):
        return self.clipping.get_current_offsets()

    def get_link_at_xy(self, x, y):
        layout = self.get_leaf_layout_at_xy(x, y)

        if layout != None:
            return layout['node'].link
        else:
            return None

    def get_link_bounds_and_targets(self):
        current_target = None
        current_bounds = [None, None]
        result = list()
        for paragraph in self.ast:
            for node in paragraph:
                current_bounds[1] = node
                if current_target != node.link:
                    if current_bounds[0] != None and current_target != None:
                        result.append([[current_bounds[0], current_bounds[1]], current_target])
                    current_bounds[0] = node
                current_target = node.link
        if current_bounds[0] != None and current_target != None:
            result.append([[current_bounds[0], current_bounds[1]], current_target])
        return result

    def get_ancestors(self, layout):
        ancestors = []
        while layout['parent'] != None:
            ancestors.append(layout['parent'])
            layout = layout['parent']
        return ancestors

    @timer.timer
    def get_leaf_layout_at_xy(self, x, y):
        line = self.get_line_layout_at_y(y)

        if y >= line['y'] + line['parent']['y'] and y < line['y'] + line['parent']['y'] + line['height']:
            for layout in self.layouter.flatten_layout(line):
                if layout['node'] != None and layout['node'].type in {'char', 'widget', 'placeholder', 'eol', 'end'}:
                    layout_x, layout_y = self.get_absolute_xy(layout)
                    if x >= layout_x and x <= layout_x + layout['width'] and y >= layout_y and y <= layout_y + layout['height']:
                        return layout
        return None

    def get_cursor_holding_layout_close_to_xy(self, x, y):
        if y < 0: x = 0
        if y > self.get_height(): x = LayoutInfo.get_max_layout_width()

        hbox = self.get_line_layout_at_y(y)
        if y >= hbox['y'] + hbox['parent']['y'] and y < hbox['y'] + hbox['parent']['y'] + hbox['height']:
            for layout in self.layouter.flatten_layout(hbox):
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

    def get_line_layout_at_y(self, y):
        if y < 0:
            return self.ast[0].layout['children'][0]
        elif y > self.get_height():
            return self.ast[-1].layout['children'][-1]
        else:
            for paragraph in self.ast:
                if y >= paragraph.layout['y'] and y < paragraph.layout['y'] + paragraph.layout['height']:
                    y -= paragraph.layout['y']
                    for line in paragraph.layout['children']:
                        if y >= line['y'] and y < line['y'] + line['height']:
                            return line

    def get_absolute_xy(self, layout):
        x, y = (0, 0)

        while not layout == None:
            x += layout['x']
            y += layout['y']
            layout = layout['parent']

        return x, y


