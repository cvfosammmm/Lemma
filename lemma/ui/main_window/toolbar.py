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
from gi.repository import Gtk, GLib

from lemma.ui.popovers.popover_manager import PopoverManager


class ToolBarView(Gtk.ActionBar):

    def __init__(self):
        Gtk.ActionBar.__init__(self)
        self.add_css_class('toolbar')

        self.paragraph_style_menu_button_label = Gtk.Label()
        self.paragraph_style_menu_button_label.set_xalign(Gtk.Align.FILL)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        box.append(self.paragraph_style_menu_button_label)
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))

        self.paragraph_style_menu_button = PopoverManager.create_popover_button('paragraph_style')
        self.paragraph_style_menu_button.set_child(box)
        self.paragraph_style_menu_button.set_can_focus(False)
        self.paragraph_style_menu_button.set_tooltip_text(_('Paragraph Style'))
        self.paragraph_style_menu_button.add_css_class('flat')
        self.paragraph_style_menu_button.set_action_name('win.show-paragraph-style-menu')
        self.pack_start(self.paragraph_style_menu_button)
        self.pack_start(Gtk.Separator())

        self.bold_button = Gtk.Button.new_from_icon_name('bold-text-symbolic')
        self.bold_button.set_action_name('win.toggle-bold')
        self.bold_button.set_can_focus(False)
        self.bold_button.set_tooltip_text(_('Bold') + ' (Ctrl+B)')

        self.italic_button = Gtk.Button.new_from_icon_name('italic-text-symbolic')
        self.italic_button.set_action_name('win.toggle-italic')
        self.italic_button.set_can_focus(False)
        self.italic_button.set_tooltip_text(_('Italic') + ' (Ctrl+I)')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.bold_button)
        box.append(self.italic_button)
        self.pack_start(box)
        self.pack_start(Gtk.Separator())

        self.insert_link_button = Gtk.ToggleButton()
        self.insert_link_button.set_child(Gtk.Image.new_from_icon_name('link-symbolic'))
        self.insert_link_button.set_can_focus(False)
        self.insert_link_button.add_css_class('flat')
        self.insert_link_button.set_tooltip_text(_('Insert Link') + ' (Ctrl+L)')
        self.insert_link_button.set_action_name('win.insert-link')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.insert_link_button)
        self.pack_start(box)

        self.math_sidebar_toggle = Gtk.ToggleButton()
        self.math_sidebar_toggle.set_tooltip_text(_('Math Toolbar') + ' (Ctrl+M)')
        self.math_sidebar_toggle.set_icon_name('insert-symbols-symbolic')
        self.math_sidebar_toggle.set_can_focus(False)
        self.math_sidebar_toggle.add_css_class('flat')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.math_sidebar_toggle)
        self.pack_end(box)
        self.pack_end(Gtk.Separator())

        self.edit_menu_button = PopoverManager.create_popover_button('edit_menu')
        self.edit_menu_button.set_child(Gtk.Image.new_from_icon_name('document-edit-symbolic'))
        self.edit_menu_button.set_can_focus(False)
        self.edit_menu_button.set_tooltip_text(_('Edit Menu'))
        self.edit_menu_button.add_css_class('flat')
        self.edit_menu_button.set_action_name('win.show-edit-menu')

        self.redo_button = Gtk.Button.new_from_icon_name('edit-redo-symbolic')
        self.redo_button.set_action_name('win.redo')
        self.redo_button.set_can_focus(False)
        self.redo_button.set_tooltip_text(_('Redo') + ' (Shift+Ctrl+Z)')

        self.undo_button = Gtk.Button.new_from_icon_name('edit-undo-symbolic')
        self.undo_button.set_action_name('win.undo')
        self.undo_button.set_can_focus(False)
        self.undo_button.set_tooltip_text(_('Undo') + ' (Ctrl+Z)')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.edit_menu_button)
        box.append(self.redo_button)
        box.append(self.undo_button)
        self.pack_end(box)


