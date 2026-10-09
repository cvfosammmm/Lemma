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

from lemma.document.ast import Paragraph


class Command():

    def __init__(self, parent, index, nodes):
        self.parent = parent
        self.index = index
        self.nodes = nodes
        self.state = dict()

    def run(self, document):
        document.invalidate_paragraph(self.parent.paragraph())

        for node in reversed(self.nodes):
            self.parent.insert(self.index, node)

        document.update_last_modified()

    def undo(self, document):
        if len(self.nodes) > 0:
            document.invalidate_paragraph(self.parent.paragraph())

        for node in self.nodes:
            node.parent.remove(node)

        document.update_last_modified()


