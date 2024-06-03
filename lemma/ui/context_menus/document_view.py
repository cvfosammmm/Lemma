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

from lemma.ui.context_menus.context_menu import ContextMenu


class ContextMenuDocumentView(ContextMenu):
    
    def __init__(self, document_view):
        ContextMenu.__init__(self)
        self.parent = document_view.view.scrolling_widget
        self.document_view = document_view

        self.popup_offset_x, self.popup_offset_y = 0, 0

        self.popover.set_parent(self.parent.content)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)
        self.popover.connect('closed', self.on_popover_close)

        self.back_button = self.create_button('Back', _('Alt') + '+Left Arrow')
        self.back_button.set_action_name('win.go-back')
        self.back_button.connect('clicked', self.on_button_click)
        self.box.append(self.back_button)
        self.forward_button = self.create_button('Forward', _('Alt') + '+Right Arrow')
        self.forward_button.set_action_name('win.go-forward')
        self.forward_button.connect('clicked', self.on_button_click)
        self.box.append(self.forward_button)

        self.box.append(Gtk.Separator())

        self.undo_button = self.create_button('Undo', _('Ctrl') + '+Z')
        self.undo_button.set_action_name('win.undo')
        self.undo_button.connect('clicked', self.on_button_click)
        self.box.append(self.undo_button)
        self.redo_button = self.create_button('Redo', _('Shift') + '+' + _('Ctrl') + '+Z')
        self.redo_button.set_action_name('win.redo')
        self.redo_button.connect('clicked', self.on_button_click)
        self.box.append(self.redo_button)

        self.box.append(Gtk.Separator())

        self.cut_button = self.create_button('Cut', _('Ctrl') + '+X')
        self.cut_button.set_action_name('win.cut')
        self.cut_button.connect('clicked', self.on_button_click)
        self.box.append(self.cut_button)

        self.copy_button = self.create_button('Copy', _('Ctrl') + '+C')
        self.copy_button.set_action_name('win.copy')
        self.copy_button.connect('clicked', self.on_button_click)
        self.box.append(self.copy_button)

        self.paste_button = self.create_button('Paste', _('Ctrl') + '+V')
        self.paste_button.set_action_name('win.paste')
        self.paste_button.connect('clicked', self.on_button_click)
        self.box.append(self.paste_button)

        self.delete_button = self.create_button('Delete')
        self.delete_button.set_action_name('win.delete')
        self.delete_button.connect('clicked', self.on_button_click)
        self.box.append(self.delete_button)

        self.box.append(Gtk.Separator())

        self.select_all_button = self.create_button('Select All', _('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.select_all_button.connect('clicked', self.on_button_click)
        self.box.append(self.select_all_button)

        self.link_buttons_separator = Gtk.Separator()
        self.box.append(self.link_buttons_separator)

        self.remove_link_button = self.create_button('Remove Link')
        self.remove_link_button.set_action_name('win.remove-link')
        self.remove_link_button.connect('clicked', self.on_button_click)
        self.box.append(self.remove_link_button)

        self.parent.connect('secondary_button_press', self.on_secondary_button_press)

    def on_secondary_button_press(self, content, data):
        self.update_button_visibility()

        x_offset, y_offset, state = data
        self.popup_offset_x, self.popup_offset_y = x_offset, y_offset
        self.popup_at_cursor(x_offset - content.scrolling_offset_x, y_offset - content.scrolling_offset_y)
        return True

    def update_button_visibility(self):
        document = self.document_view.document

        if document == None: return

        char_nodes = [node for node in document.ast.get_subtree(*document.ast.get_cursor_state()) if node.link != None]
        self.remove_link_button.set_visible(len(char_nodes) > 0)
        self.link_buttons_separator.set_visible(len(char_nodes) > 0)

    def on_button_click(self, button):
        self.popover.popdown()

    def on_popover_close(self, popover):
        pass


