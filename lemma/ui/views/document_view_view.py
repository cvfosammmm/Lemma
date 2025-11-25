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

from lemma.use_cases.use_cases import UseCases
from lemma.ui.views.autocomplete_view import AutocompleteView


class DocumentView(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)

        self.set_size_request(770, -1)
        self.set_vexpand(True)
        self.set_hexpand(True)

        self.content = DocumentViewDrawingArea()
        self.content.set_parent(self)

        self.scrollbar_vertical = ScrollbarViewVertical()
        self.scrollbar_vertical.set_parent(self)

        self.title_widget = TitleWidget()
        self.title_widget.set_parent(self)

        self.link_overlay = Gtk.Label.new('')
        self.link_overlay.set_valign(Gtk.Align.END)
        self.link_overlay.set_halign(Gtk.Align.END)
        self.link_overlay.add_css_class('link-overlay')
        self.link_overlay.set_visible(False)
        self.link_overlay.set_parent(self)

        self.autocomplete_view = AutocompleteView()
        self.autocomplete_view.set_parent(self)

    def do_snapshot(self, snapshot):
        self.snapshot_child(self.content, snapshot)
        self.snapshot_child(self.scrollbar_vertical, snapshot)
        self.snapshot_child(self.title_widget, snapshot)
        self.snapshot_child(self.link_overlay, snapshot)
        self.snapshot_child(self.autocomplete_view, snapshot)

    def do_measure(self, orientation, for_size):
        return self.content.measure(orientation, for_size)

    def do_size_allocate(self, width, height, baseline):
        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y, rectangle.width, rectangle.height = (0, 0, width, height)
        self.content.size_allocate(rectangle, baseline)

        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y, rectangle.width, rectangle.height = (0, 0, width, height)
        self.scrollbar_vertical.size_allocate(rectangle, baseline)

        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y, rectangle.width, rectangle.height = (0, -self.title_widget.offset_y, width, height)
        self.title_widget.size_allocate(rectangle, baseline)

        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y, rectangle.width, rectangle.height = (0, 0, width, height)
        self.link_overlay.size_allocate(rectangle, baseline)

        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y, rectangle.width, rectangle.height = (0, 0, width, height)
        self.autocomplete_view.size_allocate(rectangle, baseline)


class DocumentViewDrawingArea(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)

        self.add_css_class('document-view')
        self.set_focusable(True)
        self.set_vexpand(True)

        self.draw_func = lambda: None

    def set_draw_func(self, draw_func):
        self.draw_func = draw_func

    def do_snapshot(self, snapshot):
        self.draw_func(snapshot)

    def do_size_allocate(self, width, height, baseline):
        UseCases.app_state_set_values({'document_view_width': width, 'document_view_height': height})


class ScrollbarViewVertical(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)
        self.add_css_class('scrollbar-vertical')

        self.set_size_request(20, -1)

        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.FILL)
        self.set_can_target(False)

        self.draw_func = lambda: None

    def do_snapshot(self, snapshot):
        self.draw_func(snapshot)

    def set_draw_func(self, draw_func):
        self.draw_func = draw_func


class TitleWidget(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.add_css_class('document-title')
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)

        self.offset_y = 0

        self.outer_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.set_size_request(640, -1)

        self.title_entry = Gtk.Entry()

        self.subtext = Gtk.Label()
        self.subtext.set_xalign(0)

        self.submit_button = Gtk.Button.new_with_label('Change Name')
        self.submit_button.set_can_focus(False)
        self.submit_button.add_css_class('suggested-action')
        self.submit_button.add_css_class('submit')

        self.cancel_button = Gtk.Button.new_with_label('Cancel')
        self.cancel_button.set_can_focus(False)

        self.button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.button_box.append(self.submit_button)
        self.button_box.append(self.cancel_button)
        self.button_revealer = Gtk.Revealer()
        self.button_revealer.set_child(self.button_box)

        self.vbox.append(self.title_entry)
        self.vbox.append(self.subtext)
        self.vbox.append(self.button_revealer)

        self.outer_vbox.append(self.vbox)
        self.outer_vbox.append(Gtk.DrawingArea())

        self.append(self.outer_vbox)

    def set_offset_y(self, offset):
        self.offset_y = offset


