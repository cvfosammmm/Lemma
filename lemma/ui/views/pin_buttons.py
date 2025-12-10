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
from gi.repository import Gtk
from gi.repository import Adw

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


