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

from lemma.services.layout_info import LayoutInfo


class DocumentViewPresenter():

    def __init__(self, model):
        self.model = model
        self.view = self.model.view
        self.content = self.view.content

    def update(self):
        if self.model.document == None: return

        self.update_pointer()

    def update_pointer(self):
        if self.model.document == None: return

        document = self.model.document
        if document == None:
            self.content.set_cursor_from_name('default')
            return

        x = self.model.scrolling_position_x + (self.model.cursor_x if self.model.cursor_x != None else 0)
        y = self.model.scrolling_position_y + (self.model.cursor_y if self.model.cursor_y != None else 0)
        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()

        if y < -LayoutInfo.get_subtitle_height():
            self.content.set_cursor_from_name('text')
        elif y > 0:
            leaf_box = document.get_leaf_at_xy(x, y)
            if leaf_box != None:
                node = leaf_box['node']
                if node != None:
                    if node.link != None and not self.model.ctrl_pressed:
                        self.content.set_cursor_from_name('pointer')
                    elif node.type == 'widget':
                        self.content.set_cursor_from_name(node.value.get_cursor_name())
                    elif node.type == 'placeholder':
                        self.content.set_cursor_from_name('default')
                    else:
                        self.content.set_cursor_from_name('text')
                else:
                    self.content.set_cursor_from_name('text')
            else:
                self.content.set_cursor_from_name('text')
        else:
            self.content.set_cursor_from_name('default')


