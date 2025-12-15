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

        self.undoable_actions = []
        self.current_undoable_action = None
        self.last_undoable_action = -1

        self.commands = []
        self.last_command = -1

    def start_undoable_action(self):
        self.current_undoable_action = []

    def end_undoable_action(self):
        self.undoable_actions = self.undoable_actions[:self.last_undoable_action + 1] + [self.current_undoable_action]
        self.last_undoable_action += 1
        self.current_undoable_action = None

    def add_command(self, name, *parameters):
        command = eval(name + '.Command')(*parameters)
        command.run(self.document)
        self.document.update()

        if self.current_undoable_action == None:
            if self.last_undoable_action >= 0 and len(self.undoable_actions[self.last_undoable_action]) > 0:
                self.undoable_actions[self.last_undoable_action].append(command)
            else:
                self.start_undoable_action()
                self.current_undoable_action.append(command)
                self.end_undoable_action()
        else:
            self.current_undoable_action.append(command)

    def can_undo(self):
        return self.last_undoable_action >= 0

    def can_redo(self):
        return self.last_undoable_action < len(self.undoable_actions) - 1

    def undo(self):
        undoable_action = self.undoable_actions[self.last_undoable_action]

        for command in reversed(undoable_action):
            command.undo(self.document)
            self.document.update()

        self.last_undoable_action -= 1

    def redo(self):
        undoable_action = self.undoable_actions[self.last_undoable_action + 1]

        for command in undoable_action:
            command.run(self.document)
            self.document.update()

        self.last_undoable_action += 1


