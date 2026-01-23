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
from gi.repository import Gtk, Adw

from lemma.ui.shortcuts import ShortcutController


class Settings(Adw.Window):

    def __init__(self, main_window):
        Adw.Window.__init__(self)
        self.add_css_class('settings')

        self.set_modal(True)
        self.set_transient_for(main_window)
        self.set_destroy_with_parent(True)
        self.set_can_focus(False)
        self.set_default_size(500, 600)

        self.shortcuts_controller = ShortcutController()
        self.shortcuts_controller.add_with_callback('Escape', self.close)
        self.add_controller(self.shortcuts_controller)

        self.navbar = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.navbar.set_size_request(250, -1)
        self.navbar.add_css_class('navbar')
        self.navbuttons = dict()

        self.title_stack = Gtk.Stack()

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.pack_start(self.title_stack)
        self.headerbar.set_title_widget(Gtk.Label.new(''))

        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.append(self.headerbar)
        self.content.append(self.stack)

        self.topbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.topbox.append(self.navbar)
        self.topbox.append(self.content)

        self.set_content(self.topbox)

    def add_page(self, title, icon_name, widget):
        self.stack.add_named(widget, title)

        title_widget = Gtk.Label.new(_(title))
        title_widget.set_xalign(0)
        self.title_stack.add_named(title_widget, title)

        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        button_box.append(Gtk.Image.new_from_icon_name(icon_name))
        button_box.append(Gtk.Label.new(title))
        navbutton = Gtk.Button()
        navbutton.set_child(button_box)
        navbutton.add_css_class('flat')

        controller = Gtk.GestureClick()
        controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        controller.set_button(1)
        controller.connect('pressed', self.on_navbutton_pressed, title)
        navbutton.add_controller(controller)

        self.navbuttons[title] = navbutton
        self.navbar.append(navbutton)

    def set_visible_page(self, page_name):
        self.stack.set_visible_child_name(page_name)
        self.title_stack.set_visible_child_name(page_name)

        for button in self.navbuttons.values():
            button.remove_css_class('active')
        self.navbuttons[page_name].add_css_class('active')

    def on_navbutton_pressed(self, button, n_press, x, y, page_name):
        self.set_visible_page(page_name)


