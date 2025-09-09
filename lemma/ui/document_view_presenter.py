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

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject

import time

from lemma.application_state.application_state import ApplicationState


class DocumentViewPresenter():

    def __init__(self, model):
        self.model = model
        self.view = self.model.view
        self.content = self.view.content

    def update(self):
        if self.model.document == None: return

        self.update_size()
        self.update_scrollbars()
        self.update_pointer()

    def update_size(self):
        if self.model.document == None: return

        document = self.model.document
        height = self.model.document.get_height() + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')
        scrolling_offset_y = document.clipping.offset_y

        self.view.adjustment_x.set_page_size(1)
        self.view.adjustment_y.set_page_size(ApplicationState.get_value('document_view_height'))
        self.view.adjustment_x.set_upper(1)
        self.view.adjustment_y.set_upper(height)

        if scrolling_offset_y > self.view.adjustment_y.get_upper() - ApplicationState.get_value('document_view_height'):
            self.view.adjustment_y.set_value(self.view.adjustment_y.get_upper())

    def update_scrollbars(self):
        if self.model.document == None: return

        document = self.model.document
        height = self.model.document.get_height() + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')

        self.view.scrollbar_x.set_visible(False)
        self.view.scrollbar_y.set_visible(height > ApplicationState.get_value('document_view_height'))
        self.view.adjustment_x.set_value(document.clipping.offset_x)
        self.view.adjustment_y.set_value(document.clipping.offset_y)

        if self.model.cursor_x != None and self.model.cursor_x > self.view.get_allocated_width() - 24:
            self.view.scrollbar_y.add_css_class('hovering')
        else:
            self.view.scrollbar_y.remove_css_class('hovering')
            if self.model.last_cursor_or_scrolling_change < time.time() - 1.5:
                self.view.scrollbar_x.add_css_class('hidden')
                self.view.scrollbar_y.add_css_class('hidden')
            else:
                self.view.scrollbar_x.remove_css_class('hidden')
                self.view.scrollbar_y.remove_css_class('hidden')

        GObject.timeout_add(1750, self.update_scrollbars)
        return False

    def update_pointer(self):
        if self.model.document == None: return

        document = self.model.document
        if document == None:
            self.content.set_cursor_from_name('default')
            return

        x = document.clipping.offset_x + (self.model.cursor_x if self.model.cursor_x != None else 0)
        y = document.clipping.offset_y + (self.model.cursor_y if self.model.cursor_y != None else 0)
        x -= ApplicationState.get_value('document_padding_left')
        y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')

        if y < -ApplicationState.get_value('subtitle_height'):
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


