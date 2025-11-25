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


class WelcomeView(Gtk.CenterBox):
        
    def __init__(self):
        Gtk.CenterBox.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('welcome')

        self.icon = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.icon.set_halign(Gtk.Align.CENTER)
        self.icon.add_css_class('icon')

        self.header = Gtk.Label.new('Welcome to Lemma')
        self.header.add_css_class('header')
        self.header.add_css_class('title-3')

        self.explainer = Gtk.Label.new('To create a new document, click the button below.')
        self.explainer.add_css_class('explainer')

        self.button = Gtk.Button.new_with_label('New Document')
        self.button.set_can_focus(False)
        self.button.set_halign(Gtk.Align.CENTER)
        self.button.set_action_name('win.add-document')
        self.button.set_tooltip_text('Add new document (Ctrl+N)')
        self.button.add_css_class('suggested-action')
        self.button.grab_focus()

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.append(self.icon)
        self.box.append(self.header)
        self.box.append(self.explainer)
        self.box.append(self.button)

        self.center_box = Gtk.CenterBox()
        self.center_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_box.set_center_widget(self.box)

        self.set_center_widget(self.center_box)


