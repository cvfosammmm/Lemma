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

    def __init__(self, paragraph, new_level):
        self.paragraph = paragraph
        self.new_level = new_level
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        self.state['node'] = self.paragraph.nodes[0]
        self.state['previous_level'] = self.paragraph.indentation_level
        self.paragraph.indentation_level = self.new_level
        self.paragraph.invalidate()

        document.update_last_modified()

    def undo(self, document):
        paragraph = self.state['node'].paragraph()

        paragraph.indentation_level = self.state['previous_level']
        paragraph.invalidate()

        document.update_last_modified()


