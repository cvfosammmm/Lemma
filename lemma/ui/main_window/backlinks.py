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
from gi.repository import Gtk, Adw, Pango


class BacklinksView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('backlinks')
        self.set_size_request(262, 280)

        self.headline = Gtk.Label.new('Backlinks')
        self.headline.add_css_class('headline')
        self.headline.set_xalign(0)
        self.append(self.headline)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_child(self.listbox)

        self.append(self.scrolled_window)

    def reset(self):
        self.listbox.remove_all()

    def add_item(self, document):
        self.listbox.append(BacklinksListItem(document))


class BacklinksListItem(Gtk.Box):
    
    def __init__(self, document):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.document = document

        self.label_header = Gtk.Label.new(document.title)
        self.label_header.set_xalign(0)
        self.label_header.set_ellipsize(Pango.EllipsizeMode.END)
        self.label_header.add_css_class('header')
        self.append(self.label_header)

        teaser_text = ' '.join(document.plaintext.splitlines())[:100].strip()
        self.label_teaser = Gtk.Label.new(teaser_text)
        self.label_teaser.set_xalign(0)
        self.label_teaser.set_ellipsize(Pango.EllipsizeMode.END)
        self.label_teaser.add_css_class('teaser')
        self.append(self.label_teaser)


