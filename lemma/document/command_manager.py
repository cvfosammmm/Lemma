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

import os.path


for (path, directories, files) in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands')):
    for file in files:
        if file.endswith('.py'):
            name = os.path.basename(file[:-3])
            exec('import lemma.document.commands.' + name + ' as ' + name)


class CommandManager():

    def __init__(self, document):
        self.document = document

        self.commands = list()
        self.commands_preedit = list()
        self.last_command = -1

    def add_command(self, name, *parameters):
        command = eval(name + '.Command')(*parameters)
        self.run_command(command)

    def add_composite_command(self, *command_specs):
        commands = [eval(command_spec[0] + '.Command')(*command_spec[1:]) for command_spec in command_specs]
        self.run_command(composite.Command(commands))

    def run_command(self, command):
        command.run(self.document)
        self.document.update()

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
            command.undo(self.document)
            self.document.update()
        self.commands_preedit = list()

        for command in reversed(self.commands[:self.last_command + 1]):
            command.undo(self.document)
            self.document.update()
            self.last_command -= 1

            if command.is_undo_checkpoint: break

    def redo(self):
        for command in self.commands[self.last_command + 1:]:
            command.run(self.document)
            self.document.update()

            self.last_command += 1

            if command.is_undo_checkpoint: break


