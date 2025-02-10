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

from lemma.document.ast.node import Node
from lemma.document.ast.cursor import Cursor
from lemma.document.layout.layouter import Layouter
from lemma.document.plaintext.plaintext_scanner import PlaintextScanner
from lemma.document.clipping.clipping import Clipping
from lemma.document.command_processor.command_processor import CommandProcessor
import lemma.infrastructure.timer as timer
for (path, directories, files) in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands')):
    for file in files:
        if file.endswith('.py'):
            name = os.path.basename(file[:-3])
            exec('import lemma.document.commands.' + name + ' as ' + name)


class Document():

    def __init__(self, id=None):
        self.last_modified = time.time()
        self.command_processor = CommandProcessor(self)

        self.id = id
        self.title = ''
        self.ast = Node('root')
        self.ast.insert(0, Node('end'))
        self.cursor = Cursor(self, self.ast[0], self.ast[0])
        self.layout = None
        self.plaintext = None

        self.change_flag = dict()

        self.layouter = Layouter(self)
        self.clipping = Clipping(self)
        self.plaintext_scanner = PlaintextScanner(self)

    def add_command(self, name, *parameters):
        command = eval(name + '.Command')(*parameters)
        self.command_processor.add_command(command)

    def add_composite_command(self, *commands):
        self.command_processor.begin_chain_of_commands()
        for command in commands:
            self.add_command(*command)
        self.command_processor.end_chain_of_commands()

    def can_undo(self): return self.command_processor.can_undo()
    def can_redo(self): return self.command_processor.can_redo()
    def undo(self): self.command_processor.undo()
    def redo(self): self.command_processor.redo()

    def update_last_modified(self):
        for client in self.change_flag:
            self.change_flag[client] = True
        self.last_modified = time.time()

    @timer.timer
    def update(self):
        self.layouter.update()
        self.clipping.update()
        self.plaintext_scanner.update()

    def has_changed(self, client):
        if client not in self.change_flag:
            self.change_flag[client] = True

        result = self.change_flag[client]
        self.change_flag[client] = False
        return result


