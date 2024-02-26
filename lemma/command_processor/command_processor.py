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


class CommandProcessor(object):

    def __init__(self, document):
        self.document = document
        self.commands = list()
        self.last_command = -1

    def add_command(self, command):
        self.commands = self.commands[:self.last_command + 1] + [command]
        self.last_command += 1
        command.run(self.document)

        self.document.update()

    def undo(self):
        if self.last_command >= 0:
            command = self.commands[self.last_command]
            command.undo(self.document)
            self.last_command -= 1

            if not command.is_undo_checkpoint:
                self.undo()
            else:
                self.document.update()
        else:
            self.document.update()

    def redo(self):
        if self.last_command < len(self.commands) - 1:
            command = self.commands[self.last_command + 1]
            command.run(self.document)
            self.last_command += 1

            if not command.is_undo_checkpoint:
                self.redo()
            else:
                self.document.update()
        else:
            self.document.update()

    def reset_undo_stack(self):
        self.commands = list()
        self.last_command = -1


