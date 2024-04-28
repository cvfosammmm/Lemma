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


class DocumentDraftView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox.get_style_context().add_class('document-title')
        self.hbox.set_valign(Gtk.Align.FILL)

        self.outer_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.set_size_request(640, -1)

        self.title_entry = Gtk.Entry()

        self.subtext = Gtk.Label()
        self.subtext.set_xalign(0)

        self.submit_button = Gtk.Button.new_with_label('Create Document')
        self.submit_button.set_can_focus(False)
        self.submit_button.get_style_context().add_class('suggested-action')

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

        self.hbox.append(self.outer_vbox)
        self.append(self.hbox)


