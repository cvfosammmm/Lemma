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

    def __init__(self, node_from, node_to):
        self.node_from = node_from
        self.node_to = node_to
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()
        self.state['deleted_nodes'] = []

        self.node_from.paragraph().invalidate()
        self.node_to.paragraph().invalidate()

        node = self.node_from
        while node != self.node_to:
            next_node = node.next_no_descent()
            node.parent.remove(node)
            if node.type == 'eol':
                for node_to_move in reversed(node.paragraph().nodes):
                    self.node_to.paragraph().insert(0, node_to_move)
                document.ast.remove(node.paragraph())
            self.state['deleted_nodes'].append(node)

            node = next_node

        document.cursor.set_insert_selection_nodes(self.node_to, self.node_to)

        document.update_last_modified()

    def undo(self, document):
        self.node_to.paragraph().invalidate()

        offset = self.node_to.parent.index(self.node_to)
        for node in self.state['deleted_nodes']:
            self.node_to.parent.insert(offset, node)

            if node.type == 'eol':
                paragraph = self.node_to.paragraph()
                paragraph_no = document.ast.index(paragraph)

                new_paragraph = Paragraph()
                for node in document.ast[paragraph_no].nodes[offset + 1:]:
                    new_paragraph.append(node)
                new_paragraph.style = document.ast[paragraph_no].style
                new_paragraph.indentation_level = document.ast[paragraph_no].indentation_level

                document.ast.insert(paragraph_no + 1, new_paragraph)
                del(document.ast[paragraph_no].nodes[offset + 1:])

                paragraph_no += 1
                offset = 0
            else:
                offset += 1

        document.cursor.set_state(self.state['cursor_state_before'])

        document.update_last_modified()


