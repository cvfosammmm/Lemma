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

from lemma.dialogs.dialog_locator import DialogLocator
from lemma.popovers.helpers.popover_menu_builder import MenuBuilder
from lemma.popovers.hamburger_menu.hamburger_menu_viewgtk import HamburgerMenuView


class HamburgerMenu(object):

    def __init__(self, popover_manager):
        self.popover_manager = popover_manager
        self.view = HamburgerMenuView(popover_manager)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.view.add_controller(self.key_controller)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('F10'):
            if state & modifiers == 0:
                self.popover_manager.popdown()
                return True

        return False


