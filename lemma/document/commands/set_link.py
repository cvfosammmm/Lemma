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

    def __init__(self, nodes, target=None):
        self.nodes = nodes
        self.target = target
        self.is_undo_checkpoint = True
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()

        prev_links = []
        for node in self.nodes:
            prev_links.append(node.link)
            node.link = self.target
        self.state['nodes_and_prev_target'] = list(zip(self.nodes, prev_links))

        if len(self.nodes) > 0:
            for line_no in range(self.nodes[0].line_no(), self.nodes[-1].line_no() + 1):
                document.invalidate(line_no)
            document.update_last_modified()

    def undo(self, document):
        for item in self.state['nodes_and_prev_target']:
            item[0].link = item[1]
        document.cursor.set_state(self.state['cursor_state_before'])

        if len(self.nodes) > 0:
            for line_no in range(self.nodes[0].line_no(), self.nodes[-1].line_no() + 1):
                document.invalidate(line_no)
            document.update_last_modified()


