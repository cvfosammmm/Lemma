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

from lemma.view.popovers.popover_menu_builder import MenuBuilder
from lemma.view.popovers.popover_templates import PopoverTop


class Popover(object):

    def __init__(self, popover_manager):
        self.popover_manager = popover_manager
        self.view = View(popover_manager)
        self.workspace = popover_manager.workspace

        self.popover_manager.connect('popup', self.on_popover_popup)

    def on_popover_popup(self, name):
        if name != 'edit_menu': return

        document = self.workspace.get_active_document()
        if document == None: return

        char_nodes = [node for node in document.ast.get_subtree(*document.ast.get_cursor_state()) if node.link != None]
        self.view.remove_link_button.set_visible(len(char_nodes) > 0)
        self.view.link_buttons_separator.set_visible(len(char_nodes) > 0)

class View(PopoverTop):

    def __init__(self, popover_manager):
        PopoverTop.__init__(self, popover_manager)

        self.set_width(306)

        self.select_all_button = MenuBuilder.create_button(_('Select All'), shortcut=_('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.add_closing_button(self.select_all_button)

        self.link_buttons_separator = Gtk.Separator()
        self.add_widget(self.link_buttons_separator)

        self.remove_link_button = MenuBuilder.create_button(_('Remove Link'))
        self.remove_link_button.set_action_name('win.remove-link')
        self.add_closing_button(self.remove_link_button)


