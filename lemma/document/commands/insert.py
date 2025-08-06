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

    def __init__(self, position_node, nodes):
        self.is_undo_checkpoint = True
        self.position_node = position_node
        self.nodes = nodes
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()

        self.position_node.parent.insert_before(self.position_node, self.nodes)
        self.state['nodes_added'] = self.nodes

        self.is_undo_checkpoint = (len(self.state['nodes_added']) > 0)
        document.update_last_modified()

    def undo(self, document):
        for node in self.state['nodes_added']:
            node.remove_from_parent()
        document.cursor.set_state(self.state['cursor_state_before'])
        document.update_last_modified()


