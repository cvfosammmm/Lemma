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

from lemma.context_menus.context_menu import ContextMenu


class ContextMenuDocumentView(ContextMenu):
    
    def __init__(self, document_view):
        ContextMenu.__init__(self)
        self.parent = document_view.view.scrolling_widget

        self.popup_offset_x, self.popup_offset_y = 0, 0

        self.popover.set_parent(self.parent.content)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)
        self.popover.connect('closed', self.on_popover_close)

        self.undo_button = self.create_button('Undo', _('Ctrl') + '+Z')
        self.undo_button.set_action_name('win.undo')
        self.undo_button.connect('clicked', self.on_button_click)
        self.box.append(self.undo_button)
        self.redo_button = self.create_button('Redo', _('Shift') + '+' + _('Ctrl') + '+Z')
        self.redo_button.set_action_name('win.redo')
        self.redo_button.connect('clicked', self.on_button_click)
        self.box.append(self.redo_button)

        self.box.append(Gtk.Separator())

        self.select_all_button = self.create_button('Select All', _('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.select_all_button.connect('clicked', self.on_button_click)
        self.box.append(self.select_all_button)

        self.parent.connect('secondary_button_press', self.on_secondary_button_press)

    def on_secondary_button_press(self, content, data):
        x_offset, y_offset, state = data
        self.popup_offset_x, self.popup_offset_y = x_offset, y_offset
        self.popup_at_cursor(x_offset - content.scrolling_offset_x, y_offset - content.scrolling_offset_y)
        return True

    def on_button_click(self, button):
        self.popover.popdown()

    def on_popover_close(self, popover):
        pass


