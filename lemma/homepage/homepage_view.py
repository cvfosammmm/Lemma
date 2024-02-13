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


class HomepageView(Gtk.CenterBox):
        
    def __init__(self):
        Gtk.CenterBox.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.label = Gtk.Label.new('Welcome.')
        self.label.set_size_request(250, -1)

        self.button = Gtk.Button.new_with_label('+ New Document')
        self.button.set_can_focus(False)
        self.button.set_action_name('win.add-document')
        self.button.set_tooltip_text('Add new document (Ctrl+N)')
        self.button.grab_focus()

        self.box.append(self.label)
        self.box.append(self.button)

        self.set_center_widget(self.box)


