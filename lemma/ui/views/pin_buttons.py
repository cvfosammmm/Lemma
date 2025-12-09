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

from lemma.ui.views.context_menu import ContextMenu


class PinButtons(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.add_css_class('linked')
        self.add_css_class('buttonbox')

        self.pin_buttons = []
        for i in range(9):
            button = Gtk.Button.new_from_icon_name(str(i + 1) + '-symbolic')
            button.set_can_focus(False)
            button.add_css_class('flat')
            button.set_tooltip_text('Activate Pinned Document 1 (Alt+' + str(i + 1) + ')')
            self.pin_buttons.append(button)
            self.append(button)

        self.context_menu = PinButtonsContextMenu(self)


class PinButtonsContextMenu(ContextMenu):

    def __init__(self, parent):
        ContextMenu.__init__(self)

        self.popover.set_parent(parent)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)

        self.unpin_button_label = Gtk.Label.new('')
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_box.append(self.unpin_button_label)

        self.unpin_button = Gtk.Button()
        self.unpin_button.set_child(button_box)
        self.box.append(self.unpin_button)


