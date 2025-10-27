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

    def __init__(self, paragraph_style, node=None):
        self.paragraph_style = paragraph_style
        self.node = node
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        self.state['paragraphs_and_previous_style'] = []

        if self.node != None:
            paragraphs = [self.node.paragraph()]
        else:
            if document.cursor.has_selection():
                first_node = document.cursor.get_first_node().paragraph_start()
                next_to_last = document.cursor.get_last_node().prev_in_parent()
                if next_to_last != None:
                    last_node = next_to_last.paragraph_end()
                else:
                    last_node = document.cursor.get_last_node().paragraph_end()

                paragraph_nos = range(document.ast.paragraph_no_offset(first_node)[0], document.ast.paragraph_no_offset(last_node)[0] + 1)
                paragraphs = []
                for paragraph_no in paragraph_nos:
                    paragraphs.append(document.ast.paragraphs[paragraph_no])
            else:
                paragraphs = [document.cursor.get_insert_node().paragraph()]

        for paragraph in paragraphs:
            self.state['paragraphs_and_previous_style'].append([paragraph, paragraph.style])
            paragraph.style = self.paragraph_style
            paragraph.invalidate()

        document.update_last_modified()

    def undo(self, document):
        for paragraph, style in self.state['paragraphs_and_previous_style']:
            paragraph.style = style
            paragraph.invalidate()

        document.update_last_modified()


