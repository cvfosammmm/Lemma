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

import lemma.document.commands.composite as composite


class CommandProcessor(object):

    def __init__(self, document):
        self.document = document
        self.commands = list()
        self.commands_preedit = list()
        self.last_command = -1
        self.command_buffer = None

    def begin_chain_of_commands(self):
        self.command_buffer = []

    def end_chain_of_commands(self):
        commands = self.command_buffer
        self.command_buffer = None
        self.add_command(composite.Command(commands))

    def add_command(self, command):
        if self.command_buffer != None:
            self.command_buffer.append(command)
            return

        command.run(self.document)
        self.document.update()
        command.run_after_layout(self.document)

        self.commands_preedit.append(command)

        if command.is_undo_checkpoint:
            self.commands = self.commands[:self.last_command + 1] + self.commands_preedit
            self.last_command += len(self.commands_preedit)
            self.commands_preedit = list()
            self.document.update_last_modified()
        self.document.signal_changes()

    def can_undo(self):
        return self.last_command >= 0

    def can_redo(self):
        return self.last_command < len(self.commands) - 1

    def get_last_command(self):
        if len(self.commands_preedit) > 0:
            return self.commands_preedit[-1]
        elif self.last_command >= 0:
            return self.commands[self.last_command]
        else:
            return None

    def undo(self):
        for command in reversed(self.commands_preedit):
            command.undo(self.document)
            self.document.update()
        self.commands_preedit = list()

        for command in reversed(self.commands[:self.last_command + 1]):
            command.undo(self.document)
            self.document.update()
            self.last_command -= 1
            if command.is_undo_checkpoint:
                self.document.update_last_modified()
                break

        self.document.signal_changes()

    def redo(self):
        for command in self.commands[self.last_command + 1:]:
            command.run(self.document)
            self.document.update()
            command.run_after_layout(self.document)

            self.last_command += 1
            if command.is_undo_checkpoint:
                self.document.update_last_modified()
                break

        self.document.signal_changes()


