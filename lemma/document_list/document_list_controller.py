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
from gi.repository import Gtk

import lemma.helpers.helpers as helpers


class DocumentListController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.scrolling_widget.connect('primary_button_press', self.on_primary_button_press)
        self.view.scrolling_widget.connect('primary_button_release', self.on_primary_button_release)

    def on_primary_button_press(self, scrolling_widget, data):
        x_offset, y_offset, state = data

        if state == 0:
            item_num = self.view.get_item_at_cursor()
            if item_num != None and item_num < len(self.model.documents):
                self.model.set_selected_index(item_num)

    def on_primary_button_release(self, scrolling_widget, data):
        x_offset, y_offset, state = data

        item_num = self.view.get_item_at_cursor()
        if item_num != None and item_num == self.model.selected_index:
            self.model.activate_item(item_num)
        self.model.set_selected_index(None)


