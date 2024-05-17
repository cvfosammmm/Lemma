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


class Command():

    def __init__(self):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.ast.get_cursor_state()

        char_nodes = [node for node in document.ast.get_subtree(*document.ast.get_cursor_state()) if node.is_char()]
        prev_targets = []
        for node in char_nodes:
            prev_targets.append(node.link_target)
            node.link_target = None
        self.state['nodes_and_prev_target'] = list(zip(char_nodes, prev_targets))

    def undo(self, document):
        document.ast.set_cursor_state(self.state['cursor_state_before'])

        for item in self.state['nodes_and_prev_target']:
            item[0].link_target = item[1]

        document.set_scroll_insert_on_screen_after_layout_update()

