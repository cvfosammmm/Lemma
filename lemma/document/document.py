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

import time, os.path

from lemma.document.ast import RootNode, Node, Cursor
from lemma.document.layouter import Layouter
from lemma.document.plaintext_and_links_scanner import PlaintextAndLinksScanner
from lemma.document.clipping import Clipping
from lemma.infrastructure.layout_info import LayoutInfo
import lemma.infrastructure.timer as timer

for (path, directories, files) in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands')):
    for file in files:
        if file.endswith('.py'):
            name = os.path.basename(file[:-3])
            exec('import lemma.document.commands.' + name + ' as ' + name)


class Document():

    def __init__(self, id=None):
        self.last_modified = time.time()
        self.commands = list()
        self.commands_preedit = list()
        self.last_command = -1

        self.id = id
        self.title = ''
        self.ast = RootNode('root')
        self.cursor = Cursor(self, self.ast[0], self.ast[0])
        self.plaintext = None
        self.links = set()

        self.change_flag = dict()

        self.layouter = Layouter(self)
        self.clipping = Clipping(self)
        self.plaintext_and_links_scanner = PlaintextAndLinksScanner(self)

    def add_command(self, name, *parameters):
        command = eval(name + '.Command')(*parameters)
        self.run_command(command)

    def add_composite_command(self, *command_specs):
        commands = [eval(command_spec[0] + '.Command')(*command_spec[1:]) for command_spec in command_specs]
        self.run_command(composite.Command(commands))

    def run_command(self, command):
        command.run(self)
        self.update()

        self.commands_preedit.append(command)

        if command.is_undo_checkpoint:
            self.commands = self.commands[:self.last_command + 1] + self.commands_preedit
            self.last_command += len(self.commands_preedit)
            self.commands_preedit = list()

    def can_undo(self):
        return self.last_command >= 0

    def can_redo(self):
        return self.last_command < len(self.commands) - 1

    def undo(self):
        for command in reversed(self.commands_preedit):
            command.undo(self)
            self.update()
        self.commands_preedit = list()

        for command in reversed(self.commands[:self.last_command + 1]):
            command.undo(self)
            self.update()
            self.last_command -= 1

            if command.is_undo_checkpoint: break

    def redo(self):
        for command in self.commands[self.last_command + 1:]:
            command.run(self)
            self.update()

            self.last_command += 1

            if command.is_undo_checkpoint: break

    def update_last_modified(self):
        for client in self.change_flag:
            self.change_flag[client] = True
        self.last_modified = time.time()

    @timer.timer
    def update(self):
        self.layouter.update()
        self.clipping.update()
        self.plaintext_and_links_scanner.update()

    def has_changed(self, client):
        if client not in self.change_flag:
            self.change_flag[client] = True

        result = self.change_flag[client]
        self.change_flag[client] = False
        return result

    def get_height(self):
        return self.ast.lines[-1]['layout']['y'] + self.ast.lines[-1]['layout']['height']

    def get_ancestors(self, layout):
        ancestors = []
        while layout['parent'] != None:
            ancestors.append(layout['parent'])
            layout = layout['parent']
        return ancestors

    def get_leaf_at_xy(self, x, y):
        line = self.get_line_at_y(y)

        if y >= line['y'] + line['parent']['y'] and y < line['y'] + line['parent']['y'] + line['height']:
            for node in [node for node in self.flatten(line) if node['node'] != None and node['node'].type in {'char', 'widget', 'placeholder', 'eol', 'end'}]:
                node_x, node_y = self.get_absolute_xy(node)
                if x >= node_x and x <= node_x + node['width'] and y >= node_y and y <= node_y + node['height']:
                    return node
        return None

    def get_cursor_holding_layout_close_to_xy(self, x, y):
        if y < 0: x = 0
        if y > self.get_height(): x = LayoutInfo.get_layout_width()

        hbox = self.get_line_at_y(y)
        if y >= hbox['y'] + hbox['parent']['y'] and y < hbox['y'] + hbox['parent']['y'] + hbox['height']:
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
        if y < 0:
            return self.ast.lines[0]['layout']['children'][0]
        elif y > self.get_height():
            return self.ast.lines[-1]['layout']['children'][-1]
        else:
            for paragraph in self.ast.lines:
                if y >= paragraph['layout']['y'] and y < paragraph['layout']['y'] + paragraph['layout']['height']:
                    y -= paragraph['layout']['y']
                    for line in paragraph['layout']['children']:
                        if y >= line['y'] and y < line['y'] + line['height']:
                            return line

    def get_absolute_xy(self, layout):
        x, y = (0, 0)

        while not layout == None:
            x += layout['x']
            y += layout['y']
            layout = layout['parent']

        return x, y


