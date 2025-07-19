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

from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView


class Popover(object):

    def __init__(self, use_cases):
        self.use_cases = use_cases
        self.view = View(use_cases)

    def on_popup(self):
        pass

    def on_popdown(self):
        pass


class View(PopoverView):

    def __init__(self, use_cases):
        PopoverView.__init__(self, use_cases)

        self.set_width(306)

        self.open_link_button = MenuBuilder.create_button(_('Open Link'))
        self.open_link_button.set_action_name('win.open-link')
        self.add_closing_button(self.open_link_button)

        self.open_link_separator = Gtk.Separator()
        self.add_widget(self.open_link_separator)

        self.copy_link_button = MenuBuilder.create_button(_('Copy Link Target'))
        self.copy_link_button.set_action_name('win.copy-link')
        self.add_closing_button(self.copy_link_button)

        self.remove_link_button = MenuBuilder.create_button(_('Remove Link'))
        self.remove_link_button.set_action_name('win.remove-link')
        self.add_closing_button(self.remove_link_button)

        self.edit_link_button = MenuBuilder.create_button(_('Edit Link'))
        self.edit_link_button.set_action_name('win.edit-link')
        self.add_closing_button(self.edit_link_button)

        self.link_buttons_separator = Gtk.Separator()
        self.add_widget(self.link_buttons_separator)

        self.cut_button = MenuBuilder.create_button(_('Cut'), shortcut=_('Ctrl') + '+X')
        self.cut_button.set_action_name('win.cut')
        self.add_closing_button(self.cut_button)
        self.copy_button = MenuBuilder.create_button(_('Copy'), shortcut=_('Ctrl') + '+C')
        self.copy_button.set_action_name('win.copy')
        self.add_closing_button(self.copy_button)
        self.paste_button = MenuBuilder.create_button(_('Paste'), shortcut=_('Ctrl') + '+V')
        self.paste_button.set_action_name('win.paste')
        self.add_closing_button(self.paste_button)
        self.delete_button = MenuBuilder.create_button(_('Delete'))
        self.delete_button.set_action_name('win.delete')
        self.add_closing_button(self.delete_button)

        self.add_widget(Gtk.Separator())

        self.select_all_button = MenuBuilder.create_button(_('Select All'), shortcut=_('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.add_closing_button(self.select_all_button)


