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

    def __init__(self, width):
        self.width = int(width)
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['size_before'] = None

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        if len(selected_nodes) == 1 and selected_nodes[0].type == 'image':
            image = selected_nodes[0].value
            self.state['size_before'] = (image['pil_image_display'].width, image['pil_image_display'].height)
            self.state['image'] = image

            width = self.width
            height = int((self.width / image['pil_image'].width) * image['pil_image'].height)
            image['pil_image_display'] = image['pil_image'].resize((width, height))
            self.is_undo_checkpoint = True

    def undo(self, document):
        if self.state['size_before'] != None:
            image = self.state['image']
            width, height = self.state['size_before']
            image['pil_image_display'] = image['pil_image'].resize((width, height))


