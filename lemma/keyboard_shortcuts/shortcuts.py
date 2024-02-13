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

from lemma.app.service_locator import ServiceLocator
from lemma.popovers.popover_manager import PopoverManager
from lemma.keyboard_shortcuts.shortcut_controller_app import ShortcutControllerApp


class Shortcuts(object):

    def __init__(self):
        self.main_window = ServiceLocator.get_main_window()

        self.shortcut_controller_app = ShortcutControllerApp()
        self.main_window.add_controller(self.shortcut_controller_app)

        PopoverManager.connect('popup', self.on_popover_popup)
        PopoverManager.connect('popdown', self.on_popover_popdown)

    def on_popover_popup(self, name):
        self.main_window.remove_controller(self.shortcut_controller_app)

    def on_popover_popdown(self, name):
        self.main_window.add_controller(self.shortcut_controller_app)


