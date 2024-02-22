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

from lemma.ast.node import *
from lemma.cursor.cursor import Cursor
from lemma.layouter.layouter import Layouter
from lemma.markdown_scanner.markdown_scanner import MarkdownScanner
from lemma.teaser_scanner.teaser_scanner import TeaserScanner
from lemma.helpers.observable import Observable


class Document(Observable):

    def __init__(self, workspace, id=None):
        Observable.__init__(self)
        self.workspace = workspace

        self.id = id
        self.title = ''
        self.lines = Lines()
        self.lines.insert(0, Line())
        self.insert = Cursor(self, self.lines.get_child(0).get_child(0))

        self.commands = list()
        self.last_command = -1
        self.last_modified = time.time()

        self.layouter = Layouter(self)
        self.markdown_scanner = MarkdownScanner(self)
        self.teaser_scanner = TeaserScanner(self)

    def set_last_modified(self):
        self.last_modified = time.time()
        self.add_change_code('changed')

    def add_command(self, command):
        self.commands = self.commands[:self.last_command + 1] + [command]
        self.last_command += 1
        command.run(self)

        self.update_visitors()
        self.set_last_modified()

    def undo(self):
        if self.last_command >= 0:
            command = self.commands[self.last_command]
            command.undo(self)
            self.last_command -= 1

            self.update_visitors()
            if not command.is_undo_checkpoint:
                self.undo()
            else:
                self.set_last_modified()
        else:
            self.set_last_modified()

    def redo(self):
        if self.last_command < len(self.commands) - 1:
            command = self.commands[self.last_command + 1]
            command.run(self)
            self.last_command += 1

            self.update_visitors()
            if not command.is_undo_checkpoint:
                self.redo()
            else:
                self.set_last_modified()
        else:
            self.set_last_modified()

    def update_visitors(self):
        self.layouter.update()
        self.markdown_scanner.update()
        self.teaser_scanner.update()


