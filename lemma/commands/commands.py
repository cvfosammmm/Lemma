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

from lemma.commands.primitives import *


class Command():

    def __init__(self):
        pass

    def add_child_and_run(self, child, document):
        self.children.append(child)
        child.run(document)

    def undo(self, document):
        for command in reversed(self.children):
            command.undo(document)


class SetTitle():

    def __init__(self, new_title):
        self.new_title = new_title
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        self.state['prev_title'] = document.title
        document.title = self.new_title

    def undo(self, document):
        document.title = self.state['prev_title']


class ReplaceAST():

    def __init__(self, ast):
        self.ast = ast
        self.is_undo_checkpoint = False

    def run(self, document):
        document.lines = self.ast
        document.insert.set_position([0, 0])
        del(self.ast)

    def undo(self, document):
        pass


class Left(Command):

    def __init__(self, offset):
        Command.__init__(self)
        self.offset = offset
        self.is_undo_checkpoint = False

    def run(self, document):
        self.children = list()
        self.add_child_and_run(MoveCursorByOffset(-self.offset), document)


class LineStart(Command):

    def __init__(self):
        Command.__init__(self)
        self.is_undo_checkpoint = False

    def run(self, document):
        self.children = list()
        line = document.insert.get_node().get_iterator().get_line()
        offset = line.get_index(document.insert.get_node())
        self.add_child_and_run(MoveCursorByOffset(-offset), document)


class Right(Command):

    def __init__(self, offset):
        Command.__init__(self)
        self.offset = offset
        self.is_undo_checkpoint = False

    def run(self, document):
        self.children = list()
        self.add_child_and_run(MoveCursorByOffset(self.offset), document)


class LineEnd(Command):

    def __init__(self):
        Command.__init__(self)
        self.is_undo_checkpoint = False

    def run(self, document):
        self.children = list()
        line = document.insert.get_node().get_iterator().get_line()
        index = line.get_index(document.insert.get_node())
        target_pos = line.length() - 1
        self.add_child_and_run(MoveCursorByOffset(target_pos - index), document)


class Return(Command):

    def __init__(self):
        Command.__init__(self)
        self.is_undo_checkpoint = True

    def run(self, document):
        self.children = list()
        self.add_child_and_run(InsertTextAtCursor('\n'), document)


class IMCommit(Command):

    def __init__(self, text):
        Command.__init__(self)
        self.is_undo_checkpoint = True
        self.text = text

    def run(self, document):
        self.children = list()

        self.add_child_and_run(InsertTextAtCursor(self.text), document)


class Delete(Command):

    def __init__(self):
        Command.__init__(self)
        self.is_undo_checkpoint = True

    def run(self, document):
        self.children = list()

        iterator = document.insert.get_node().get_iterator()
        line = iterator.get_line()
        if document.insert.get_node() != line.get_child(-1) or line.parent.get_child(-1) != line:
            self.add_child_and_run(DeleteTextAtCursor(), document)
            self.is_undo_checkpoint = True
        else:
            self.is_undo_checkpoint = False


class Backspace(Command):

    def __init__(self):
        Command.__init__(self)
        self.is_undo_checkpoint = True

    def run(self, document):
        self.children = list()

        line = document.insert.get_node().get_iterator().get_line()
        index = line.get_index(document.insert.get_node())
        if document.lines.get_index(line) != 0 or index != 0:
            self.add_child_and_run(MoveCursorByOffset(-1), document)
            self.add_child_and_run(DeleteTextAtCursor(), document)
            self.is_undo_checkpoint = True
        else:
            self.is_undo_checkpoint = False


