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
from gi.repository import Gtk, Pango


class AutocompleteWidgetView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.entry = Gtk.Entry()

        self.layout = Pango.Layout(self.get_pango_context())
        self.layout.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout.set_font_description(Pango.FontDescription.from_string('Cantarell Bold 11'))
        self.list = Gtk.DrawingArea()

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.list)

        self.append(self.entry)
        self.append(self.scrolled_window)

        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)


