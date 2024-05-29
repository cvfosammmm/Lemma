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
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Pango, PangoCairo

from lemma.view.main_window.scrolling_widget import ScrollingWidget


class DocumentListView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.add_css_class('document-list')
        self.set_focusable(True)
        self.set_size_request(262, -1)

        self.page_size = 1
        self.line_height = 67

        self.layout_header = Pango.Layout(self.get_pango_context())
        self.layout_header.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_header.set_font_description(Pango.FontDescription.from_string('Cantarell Bold 11'))

        self.layout_date = Pango.Layout(self.get_pango_context())
        self.layout_date.set_alignment(Pango.Alignment.RIGHT)
        self.layout_date.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.layout_teaser = Pango.Layout(self.get_pango_context())
        self.layout_teaser.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_teaser.set_font_description(Pango.FontDescription.from_string('NewComputerModern08 Book 13px'))

        self.scrolling_widget = ScrollingWidget()
        self.content = self.scrolling_widget.content
        self.set_child(self.scrolling_widget.view)

    def get_item_at_cursor(self):
        y = self.scrolling_widget.cursor_y
        x = self.scrolling_widget.cursor_x

        if y == None or x == None or x > self.scrolling_widget.width - 12: return None
        return int((y + self.scrolling_widget.adjustment_y.get_value()) // self.line_height)


