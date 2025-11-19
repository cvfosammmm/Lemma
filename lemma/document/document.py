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

from lemma.document.ast import Root, Cursor
from lemma.document.command_manager import CommandManager
from lemma.document.layouter import Layouter
from lemma.document.plaintext_scanner import PlaintextScanner
from lemma.document.links_scanner import LinksScanner
from lemma.document.clipping import Clipping
from lemma.document.xml_scanner import XMLScanner
from lemma.services.layout_info import LayoutInfo
from lemma.application_state.application_state import ApplicationState


class Document():

    def __init__(self, id=None):
        self.last_modified = time.time()
        self.last_cursor_movement = time.time()

        self.id = id
        self.title = ''
        self.ast = Root()
        self.cursor = Cursor(self, self.ast[0], self.ast[0])
        self.plaintext = None
        self.xml = None
        self.links = set()

        self.change_flag = dict()

        self.command_manager = CommandManager(self)
        self.layouter = Layouter(self)
        self.clipping = Clipping(self)
        self.plaintext_scanner = PlaintextScanner(self)
        self.links_scanner = LinksScanner(self)
        self.xml_scanner = XMLScanner(self)

    def add_command(self, name, *parameters):
        self.command_manager.add_command(name, *parameters)

    def add_composite_command(self, *command_specs):
        self.command_manager.add_composite_command(*command_specs)

    def select_node(self, node):
        next_node = node.next_in_parent()
        self.add_command('move_cursor_to_node', node, next_node)

    def delete_selection(self):
        node_from = self.cursor.get_first_node()
        node_to = self.cursor.get_last_node()
        self.add_command('delete', node_from, node_to)
        self.add_command('update_implicit_x_position')

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
        elif self.get_absolute_xy(self.get_line_at_y(insert_position[1]))[1] == 0:
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

    def update_last_cursor_movement(self):
        self.last_cursor_movement = time.time()

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

    def can_undo(self):
        return self.command_manager.can_undo()

    def can_redo(self):
        return self.command_manager.can_redo()

    def get_height(self):
        return self.ast.paragraphs[-1].layout['y'] + self.ast.paragraphs[-1].layout['height']

    def get_width(self):
        return self.ast.paragraphs[0].layout['width']

    def get_current_scrolling_offsets(self):
        return self.clipping.get_current_offsets()

    def get_ancestors(self, layout):
        ancestors = []
        while layout['parent'] != None:
            ancestors.append(layout['parent'])
            layout = layout['parent']
        return ancestors

    def get_leaf_at_xy(self, x, y):
        line = self.get_line_at_y(y)

        if y >= line['y'] + line['parent']['y'] and y < line['y'] + line['parent']['y'] + line['height']:
            for node in [node for node in self.layouter.flatten_layout(line) if node['node'] != None and node['node'].type in {'char', 'widget', 'placeholder', 'eol', 'end'}]:
                node_x, node_y = self.get_absolute_xy(node)
                if x >= node_x and x <= node_x + node['width'] and y >= node_y and y <= node_y + node['height']:
                    return node
        return None

    def get_cursor_holding_layout_close_to_xy(self, x, y):
        if y < 0: x = 0
        if y > self.get_height(): x = LayoutInfo.get_max_layout_width()

        hbox = self.get_line_at_y(y)
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

    def get_line_at_y(self, y):
        if y < 0:
            return self.ast.paragraphs[0].layout['children'][0]
        elif y > self.get_height():
            return self.ast.paragraphs[-1].layout['children'][-1]
        else:
            for paragraph in self.ast.paragraphs:
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


