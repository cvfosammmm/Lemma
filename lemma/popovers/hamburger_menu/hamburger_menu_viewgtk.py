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

from lemma.popovers.helpers.popover_menu_builder import MenuBuilder
from lemma.popovers.helpers.popover import Popover


class HamburgerMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(306)

        self.button_add_document = MenuBuilder.create_button(_('New Document'), shortcut=_('Ctrl') + '+N')
        self.button_add_document.set_action_name('win.add-document')
        self.add_closing_button(self.button_add_document)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_shortcuts = MenuBuilder.create_button(_('Keyboard Shortcuts'), shortcut=_('Ctrl') + '+?')
        self.button_shortcuts.set_action_name('win.show-shortcuts-dialog')
        self.add_closing_button(self.button_shortcuts)

        self.button_about = MenuBuilder.create_button(_('About'))
        self.button_about.set_action_name('win.show-about-dialog')
        self.add_closing_button(self.button_about)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_quit = MenuBuilder.create_button(_('Quit'), shortcut=_('Ctrl') + '+Q')
        self.button_quit.set_action_name('win.quit')
        self.add_closing_button(self.button_quit)


