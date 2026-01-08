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

    def __init__(self, paragraph):
        self.paragraph = paragraph
        self.state = dict()

    def run(self, document):
        index = self.paragraph.parent.index(self.paragraph)
        self.state['index'] = index
        self.state['cursor_state_before'] = document.cursor.get_state()

        if not self.paragraph.is_last_in_parent():
            document.cursor.set_insert_selection_nodes(self.paragraph.next_in_parent()[0], self.paragraph.next_in_parent()[0])
        else:
            document.cursor.set_insert_selection_nodes(self.paragraph.prev_in_parent()[-1], self.paragraph.prev_in_parent[-1])
        self.paragraph.parent.remove_range(index, index + 1)

        document.update_last_modified()

    def undo(self, document):
        self.paragraph.parent.insert(self.state['index'], self.paragraph)

        document.cursor.set_state(self.state['cursor_state_before'])
        document.update_last_modified()


