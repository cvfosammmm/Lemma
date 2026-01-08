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

    def __init__(self, position_node, nodes):
        self.position_node = position_node
        self.nodes = nodes
        self.state = dict()

    def run(self, document):
        self.position_node.paragraph().invalidate()

        offset = self.position_node.parent.index(self.position_node)
        for node in self.nodes:
            self.position_node.parent.insert(offset, node)

            if node.type == 'eol':
                paragraph = self.position_node.paragraph()
                paragraph_no = document.ast.index(paragraph)

                new_paragraph = Paragraph()
                for node in document.ast[paragraph_no][offset + 1:]:
                    new_paragraph.append(node)
                new_paragraph.style = document.ast[paragraph_no].style
                new_paragraph.indentation_level = document.ast[paragraph_no].indentation_level

                document.ast.insert(paragraph_no + 1, new_paragraph)
                del(document.ast[paragraph_no].children[offset + 1:])

                paragraph_no += 1
                offset = 0
            else:
                offset += 1

        document.update_last_modified()

    def undo(self, document):
        if len(self.nodes) > 0:
            self.nodes[0].paragraph().invalidate()
            self.nodes[-1].paragraph().invalidate()

        for node in self.nodes:
            if node.type == 'eol':
                paragraph_1 = node.paragraph()
                paragraph_2 = paragraph_1.next_in_parent()
                for next_line_node in paragraph_2:
                    paragraph_1.append(next_line_node)
                document.ast.remove(paragraph_2)
            node.parent.remove(node)

        document.update_last_modified()


