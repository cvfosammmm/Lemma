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

    def __init__(self, paragraph_style):
        self.paragraph_style = paragraph_style
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        self.state['nodes_and_previous_paragraph_style'] = []

        first_node = document.cursor.get_first_node().paragraph_start()
        if document.cursor.has_selection():
            next_to_last = document.cursor.get_last_node().prev_in_parent()
            if next_to_last != None:
                last_node = next_to_last.paragraph_end()
            else:
                last_node = document.cursor.get_last_node().paragraph_end()
        else:
            last_node = first_node.paragraph_end()

        for node in document.ast.get_subtree(first_node.get_position(), last_node.get_position()):
            self.state['nodes_and_previous_paragraph_style'].append([node, node.paragraph_style])
            node.paragraph_style = self.paragraph_style
        self.state['nodes_and_previous_paragraph_style'].append([last_node, last_node.paragraph_style])
        last_node.paragraph_style = self.paragraph_style

        for paragraph_no in range(first_node.paragraph_no(), last_node.paragraph_no() + 1):
            document.invalidate(paragraph_no)
        document.update_last_modified()

    def undo(self, document):
        for node, paragraph_style in self.state['nodes_and_previous_paragraph_style']:
            node.paragraph_style = paragraph_style

        first_node = self.state['nodes_and_previous_paragraph_style'][0][0]
        last_node = self.state['nodes_and_previous_paragraph_style'][-1][0]
        for paragraph_no in range(first_node.paragraph_no(), last_node.paragraph_no() + 1):
            document.invalidate(paragraph_no)
        document.update_last_modified()


