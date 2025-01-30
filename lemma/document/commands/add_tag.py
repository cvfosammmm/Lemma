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

    def __init__(self, tag_name):
        self.tag_name = tag_name
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        char_nodes = [node for node in document.ast.get_subtree(*document.cursor.get_state()) if node.is_char()]

        self.state['affected_nodes'] = list()
        for node in char_nodes:
            if self.tag_name not in node.tags:
                self.state['affected_nodes'].append(node)
                node.tags.add(self.tag_name)

        document.ast.mark_changed()

    def run_after_layout(self, document):
        pass

    def undo(self, document):
        for node in self.state['affected_nodes']:
            node.tags.remove(self.tag_name)

        document.ast.mark_changed()


