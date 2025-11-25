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
from gi.repository import Gtk, Gdk


class AutocompleteView(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.add_css_class('autocomplete')

        self.width = 300
        self.height = 0
        self.x = 0
        self.y = 0
        self.line_height = 35
        self.max_height = 5 * self.line_height + 2
        self.focus_hide = True
        self.set_size_request(self.width, self.height)
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)

        self.listbox = Gtk.ListBox()
        self.listbox.set_activate_on_single_click(True)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_can_focus(False)

        self.listbox.connect('selected-rows-changed', self.on_selected_rows_changed)

        self.set_child(self.listbox)

    def set_items(self, items):
        self.listbox.remove_all()
        for item in items:
            self.listbox.append(ACItem('\\' + item))
        self.listbox.select_row(self.listbox.get_first_child())

        self.height = min(len(items), 5) * self.line_height + 2
        self.width = 300
        self.set_size_request(self.width, self.height)

    def select_next(self):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row == listbox.get_last_child():
            listbox.select_row(listbox.get_first_child())
        else:
            listbox.select_row(listbox.get_row_at_index(selected_row.get_index() + 1))

    def select_prev(self):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row == listbox.get_first_child():
            listbox.select_row(listbox.get_last_child())
        else:
            listbox.select_row(listbox.get_row_at_index(selected_row.get_index() - 1))

    def on_selected_rows_changed(self, listbox):
        selected_row = self.listbox.get_selected_row()
        adjustment = self.get_vadjustment()

        if selected_row == None:
            adjustment.set_value(0)
        else:
            bounds = selected_row.compute_bounds(self.listbox).out_bounds
            item_height = bounds.size.height
            y = bounds.origin.y
            page_size = adjustment.get_page_size()
            offset = adjustment.get_value()
            if offset > y:
                adjustment.set_value(y)
            if offset < y + item_height - page_size:
                adjustment.set_value(y + item_height - page_size)


class ACItem(Gtk.ListBoxRow):

    def __init__(self, title):
        Gtk.ListBoxRow.__init__(self)
        self.set_size_request(-1, 30)

        self.title = title

        label = Gtk.Label.new(self.title)
        label.set_xalign(Gtk.Align.FILL)
        self.set_child(label)


