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

import time, os.path, datetime

from lemma.document.ast.node import Node
from lemma.document.ast.cursor import Cursor
from lemma.document.layout.layouter import Layouter
from lemma.document.housekeeper.housekeeper import Housekeeper
from lemma.document.clipping.clipping import Clipping
from lemma.document.html.html_scanner import HTMLScanner
from lemma.document.plaintext.plaintext_scanner import PlaintextScanner
from lemma.document.command_processor.command_processor import CommandProcessor
from lemma.infrastructure.service_locator import ServiceLocator
from lemma.helpers.observable import Observable
for (path, directories, files) in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands')):
    for file in files:
        if file.endswith('.py'):
            name = os.path.basename(file[:-3])
            exec('import lemma.document.commands.' + name + ' as ' + name)


class Document(Observable):

    def __init__(self, id):
        Observable.__init__(self)

        self.last_modified = time.time()
        self.command_processor = CommandProcessor(self)

        self.id = id
        self.title = ''
        self.ast = Node('root')
        self.ast.insert(0, Node('end'))
        self.cursor = Cursor(self, self.ast[0], self.ast[0])
        self.implicit_x_position = 0
        self.scroll_insert_on_screen_after_layout_update = False
        self.html = None
        self.plaintext = None
        self.links = []

        self.layouter = Layouter(self)
        self.housekeeper = Housekeeper(self)
        self.clipping = Clipping(self)
        self.html_scanner = HTMLScanner(self)
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

    def update(self):
        self.housekeeper.update()
        self.layouter.update()
        self.clipping.update()
        self.html_scanner.update()
        self.plaintext_scanner.update()
        self.update_implicit_x_position()

        self.add_change_code('changed')

    def update_last_modified(self):
        self.last_modified = time.time()

    def update_implicit_x_position(self):
        last_command = self.command_processor.get_last_command()
        if last_command != None and last_command.update_implicit_x_position:
            x, y = self.cursor.get_insert_node().layout.get_absolute_xy()
            self.implicit_x_position = x

    def set_title(self, title):
        self.title = title
        self.html_scanner.update()

        self.update_last_modified()
        self.add_change_code('changed')

    def get_last_modified_string(self):
        datetime_today, datetime_this_week, datetime_this_year = ServiceLocator.get_datetimes_today_week_year()
        datetime_last_modified = datetime.datetime.fromtimestamp(self.last_modified)
        if self.last_modified >= datetime_today.timestamp():
            return '{datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified)
        elif self.last_modified >= datetime_this_week.timestamp():
            return '{datetime:%a}'.format(datetime=datetime_last_modified)
        elif self.last_modified >= datetime_this_year.timestamp():
            return '{datetime.day} {datetime:%b}'.format(datetime=datetime_last_modified)
        else:
            return '{datetime.day} {datetime:%b} {datetime.year}'.format(datetime=datetime_last_modified)

    def set_scroll_insert_on_screen_after_layout_update(self, animate=False):
        self.scroll_insert_on_screen_after_layout_update = True


