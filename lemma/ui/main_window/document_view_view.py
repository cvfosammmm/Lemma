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

from lemma.infrastructure.color_manager import ColorManager


class DocumentViewView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.set_size_request(770, -1)

        self.padding_left = 48
        self.padding_bottom = 120
        self.padding_top = 49
        self.title_height = 49
        self.subtitle_height = 50
        self.title_buttons_height = 0
        self.title_width = 500
        self.insert_height = 25
        self.insert_drawing_offset = 9

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

        self.content = Gtk.DrawingArea()
        self.content.set_focusable(True)
        self.content.set_vexpand(True)

        self.set_child(self.content)

        self.scrollbar_x = Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL)
        self.scrollbar_x.set_valign(Gtk.Align.END)
        self.scrollbar_x.add_css_class('bottom')
        self.scrollbar_x.add_css_class('overlay-indicator')
        self.adjustment_x = self.scrollbar_x.get_adjustment()
        self.add_overlay(self.scrollbar_x)

        self.scrollbar_y = Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL)
        self.scrollbar_y.set_halign(Gtk.Align.END)
        self.scrollbar_y.add_css_class('right')
        self.scrollbar_y.add_css_class('overlay-indicator')
        self.adjustment_y = self.scrollbar_y.get_adjustment()
        self.add_overlay(self.scrollbar_y)

        self.link_overlay = Gtk.Label.new('http://url')
        self.link_overlay.set_valign(Gtk.Align.END)
        self.link_overlay.set_halign(Gtk.Align.END)
        self.link_overlay.add_css_class('link-overlay')
        self.add_overlay(self.link_overlay)


