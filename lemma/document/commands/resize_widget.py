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

    def __init__(self, width):
        self.width = int(width)
        self.is_undo_checkpoint = False
        self.state = dict()

    def run(self, document):
        self.state['width_before'] = None
        self.state['widget'] = None
        self.state['node'] = None

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        if len(selected_nodes) == 1 and selected_nodes[0].type == 'widget' and selected_nodes[0].value.is_resizable():
            widget = selected_nodes[0].value
            self.state['width_before'] = widget.get_width()
            self.state['widget'] = widget
            self.state['node'] = selected_nodes[0]
            widget.set_width(self.width)
            self.is_undo_checkpoint = True

        if self.state['node'] != None:
            document.invalidate(self.state['node'].line_no())
            document.update_last_modified()

    def undo(self, document):
        if self.state['width_before'] != None:
            widget = self.state['widget']
            widget.set_width(self.state['width_before'])

        if self.state['node'] != None:
            document.invalidate(self.state['node'].line_no())
            document.update_last_modified()


