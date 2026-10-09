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


class Command():

    def __init__(self, node):
        self.node = node
        self.state = dict()

    def run(self, document):
        self.state['parent'] = self.node.parent
        self.state['index'] = self.node.parent.index(self.node)

        self.node.parent.remove(self.node)

        document.invalidate_paragraph(self.node.paragraph())
        document.update_last_modified()

    def undo(self, document):
        self.state['parent'].insert(self.state['index'], self.node)

        document.invalidate_paragraph(self.node.paragraph())
        document.update_last_modified()


