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

from lemma.document.ast.ast import AST
from lemma.document.housekeeper.housekeeper import Housekeeper
from lemma.document.layouter.layouter import Layouter
from lemma.document.markdown_scanner.markdown_scanner import MarkdownScanner
from lemma.document.plaintext_scanner.plaintext_scanner import PlaintextScanner
from lemma.document.command_processor.command_processor import CommandProcessor
from lemma.helpers.observable import Observable
import lemma.document.commands.populate_from_path as populate_from_path
for (path, directories, files) in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands')):
    for file in files:
        if file.endswith('.py'):
            name = os.path.basename(file[:-3])
            exec('import lemma.document.commands.' + name + ' as ' + name)


class Document(Observable):

    def __init__(self, id, path=None):
        Observable.__init__(self)

        self.last_modified = time.time()
        self.command_processor = CommandProcessor(self)

        self.id = id
        self.title = ''
        self.ast = AST()
        self.implicit_x_position = 0
        self.scroll_insert_on_screen_after_layout_update = False
        self.layout = None
        self.markdown = None
        self.plaintext = None

        self.housekeeper = Housekeeper(self)
        self.layouter = Layouter(self)
        self.markdown_scanner = MarkdownScanner(self)
        self.plaintext_scanner = PlaintextScanner(self)
        self.update() # this will create an empty layout, markdown string, ...

        if path != None:
            self.add_command('populate_from_path', path)
            self.command_processor.reset_undo_stack()

    def add_command(self, name, *parameters): self.command_processor.add_command(eval(name + '.Command')(*parameters))
    def can_undo(self): return self.command_processor.can_undo()
    def can_redo(self): return self.command_processor.can_redo()
    def undo(self): self.command_processor.undo()
    def redo(self): self.command_processor.redo()

    def update(self):
        self.housekeeper.update()
        self.layouter.update()
        self.markdown_scanner.update()
        self.plaintext_scanner.update()
        self.update_implicit_x_position()

        self.last_modified = time.time()
        self.add_change_code('changed')

    def update_implicit_x_position(self):
        last_command = self.command_processor.get_last_command()
        if last_command != None and last_command.update_implicit_x_position:
            x, y = self.get_xy_at_node(self.ast.insert.get_node())
            self.implicit_x_position = x

    def set_scroll_insert_on_screen_after_layout_update(self, animate=False):
        self.scroll_insert_on_screen_after_layout_update = True

    def get_xy_at_node(self, node):
        box = node.box
        x, y = (0, 0)

        while not box == self.layout:
            new_x, new_y = box.parent.get_xy_at_child(box)
            x += new_x
            y += new_y
            box = box.parent

        return x, y

    def get_node_at_xy(self, x, y):
        box = self.layout
        x = max(0, min(box.width, x))
        y = max(0, y)
        if y > box.height: x, y = (box.width, box.height)

        while not box.is_leaf():
            box, x_offset, y_offset = box.get_child_at_xy(x, y)
            x -= x_offset
            y -= y_offset
        return box.get_node()


