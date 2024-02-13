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


class MenuBuilder():

    def create_menu():
        menu = Gtk.Popover()
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        menu.set_child(box)

        return menu

    def create_button(label, shortcut=None):
        button = Gtk.Button()
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button.set_child(button_box)

        button_box.append(Gtk.Label.new(label))

        if shortcut != None:
            shortcut_label = Gtk.Label.new(shortcut)
            shortcut_label.get_style_context().add_class('shortcut')
            button_box.append(shortcut_label)

        return button

    def add_button(menu, button):
        box = menu.get_child()
        box.append(button)

    def add_separator(menu):
        box = menu.get_child()
        box.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))


