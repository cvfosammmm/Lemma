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

from lemma.document.ast.node import Node
from lemma.document.ast.link import Link


class Command():

    def __init__(self, paragraph_style):
        self.paragraph_style = paragraph_style
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        self.state['nodes_and_previous_paragraph_style'] = []

        first_node = document.cursor.get_first_node().line_start()
        last_node = document.cursor.get_last_node().line_end()
        for node in document.ast.get_subtree(first_node.get_position(), last_node.get_position()):
            self.state['nodes_and_previous_paragraph_style'].append([node, node.paragraph_style])
            node.paragraph_style = self.paragraph_style
        self.state['nodes_and_previous_paragraph_style'].append([last_node, last_node.paragraph_style])
        last_node.paragraph_style = self.paragraph_style

    def undo(self, document):
        for node, paragraph_style in self.state['nodes_and_previous_paragraph_style']:
            node.paragraph_style = paragraph_style


