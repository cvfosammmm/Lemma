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

    def __init__(self, index_from, index_to):
        self.index_from = index_from
        self.index_to = index_to
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()
        self.state['deleted_paragraphs'] = document.ast[self.index_from:self.index_to]

        first_paragraph = document.ast[self.index_from]
        last_paragraph = document.ast[self.index_to - 1]
        if not last_paragraph.is_last_in_parent():
            document.cursor.set_insert_selection_nodes(last_paragraph.next_in_parent()[0], last_paragraph.next_in_parent()[0])
        else:
            document.cursor.set_insert_selection_nodes(first_paragraph.prev_in_parent()[-1], first_paragraph.prev_in_parent()[-1])

        document.ast.remove_range(self.index_from, self.index_to)

        document.update_last_modified()

    def undo(self, document):
        for paragraph in reversed(self.state['deleted_paragraphs']):
            document.ast.insert(self.index_from, paragraph)

        document.cursor.set_state(self.state['cursor_state_before'])

        document.update_last_modified()


