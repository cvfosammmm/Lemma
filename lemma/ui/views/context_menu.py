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


class ContextMenu():

    def __init__(self):
        self.popover = Gtk.Popover()
        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.popover.set_child(self.box)
        self.popover.set_has_arrow(False)
        self.popover.set_can_focus(False)
        self.popover.add_css_class('context-menu')

    def create_button(self, label, shortcut=None, popdown=True):
        button = Gtk.Button()
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button.set_child(button_box)

        button_box.append(Gtk.Label.new(label))

        if shortcut != None:
            shortcut_label = Gtk.Label.new(shortcut)
            shortcut_label.add_css_class('shortcut')
            shortcut_label.set_xalign(Gtk.Align.END)
            shortcut_label.set_hexpand(True)
            button_box.append(shortcut_label)

        if popdown:
            button.connect('clicked', self.on_button_click)

        return button

    def popup_at_cursor(self, x, y):
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = 1
        rect.height = 1
        self.popover.set_pointing_to(rect)
        self.popover.popup()

    def on_button_click(self, button):
        self.popover.popdown()


