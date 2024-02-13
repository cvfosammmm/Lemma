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
from gi.repository import Gtk, Gdk, Pango

from lemma.scrolling_widget.scrolling_widget import ScrollingWidget


class DocumentViewView(Gtk.Overlay):

    def __init__(self, document_view):
        Gtk.Overlay.__init__(self)

        self.padding_bottom = 120
        self.padding_top = 49
        self.title_height = 49
        self.subtitle_height = 50
        self.title_buttons_height = 0
        self.title_width = 500

        self.layout_title = Pango.Layout(self.get_pango_context())
        self.layout_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_title.set_width(self.title_width * Pango.SCALE)
        font_description = self.layout_title.get_context().get_font_description()
        font_description.set_weight(Pango.Weight.BOLD)
        font_description.set_size(24 * Pango.SCALE)
        self.layout_title.set_font_description(font_description)

        self.layout_subtitle = Pango.Layout(self.get_pango_context())
        self.layout_subtitle.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_subtitle.set_width(self.title_width * Pango.SCALE)
        font_description = self.layout_subtitle.get_context().get_font_description()
        font_description.set_size(11 * Pango.SCALE)
        self.layout_subtitle.set_font_description(font_description)

        self.scrolling_widget = ScrollingWidget()

        self.content = self.scrolling_widget.content
        self.content.set_focusable(True)
        self.content.set_vexpand(True)

        self.mouse_cursor_default = Gdk.Cursor.new_from_name('default')
        self.mouse_cursor_text = Gdk.Cursor.new_from_name('text')
        self.mouse_cursor_pointer = Gdk.Cursor.new_from_name('pointer')

        self.set_child(self.scrolling_widget.view)


