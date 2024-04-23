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

from lemma.popovers.popover_manager import PopoverManager


class ToolBar(Gtk.ActionBar):

    def __init__(self):
        Gtk.ActionBar.__init__(self)

        self.add_math_button = Gtk.Button.new_from_icon_name('insert-math-symbolic')
        self.add_math_button.set_action_name('win.insert-matharea')
        self.add_math_button.set_can_focus(False)
        self.add_math_button.set_tooltip_text(_('Insert Math') + ' (Ctrl+M)')
        self.pack_start(self.add_math_button)

        self.document_menu_button = PopoverManager.create_popover_button('document_menu')
        self.document_menu_button.set_child(Gtk.Image.new_from_icon_name('view-more-symbolic'))
        self.document_menu_button.set_can_focus(False)
        self.document_menu_button.set_tooltip_text(_('Document Menu') + ' (F12)')
        self.document_menu_button.get_style_context().add_class('flat')
        self.document_menu_button.set_action_name('win.show-document-menu')
        self.pack_end(self.document_menu_button)

        self.edit_menu_button = PopoverManager.create_popover_button('edit_menu')
        self.edit_menu_button.set_child(Gtk.Image.new_from_icon_name('document-edit-symbolic'))
        self.edit_menu_button.set_can_focus(False)
        self.edit_menu_button.set_tooltip_text(_('Edit Menu'))
        self.edit_menu_button.get_style_context().add_class('flat')
        self.edit_menu_button.set_action_name('win.show-edit-menu')
        self.pack_end(self.edit_menu_button)

        self.redo_button = Gtk.Button.new_from_icon_name('edit-redo-symbolic')
        self.redo_button.set_action_name('win.redo')
        self.redo_button.set_can_focus(False)
        self.redo_button.set_tooltip_text(_('Redo') + ' (Shift+Ctrl+Z)')
        self.pack_end(self.redo_button)

        self.undo_button = Gtk.Button.new_from_icon_name('edit-undo-symbolic')
        self.undo_button.set_action_name('win.undo')
        self.undo_button.set_can_focus(False)
        self.undo_button.set_tooltip_text(_('Undo') + ' (Ctrl+Z)')
        self.pack_end(self.undo_button)


