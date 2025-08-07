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

from lemma.ui.popovers.popover_manager import PopoverManager


class HeaderBar(Gtk.Paned):

    def __init__(self):
        Gtk.Paned.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_wide_handle(True)
        self.add_css_class('header')

        self.hb_left = HeaderBarLeft()
        self.hb_right = HeaderBarRight()

        self.set_resize_start_child(False)
        self.set_shrink_start_child(False)
        self.set_resize_end_child(True)
        self.set_shrink_end_child(False)
        self.set_start_child(self.hb_left)
        self.set_end_child(self.hb_right)


class HeaderBarLeft(Gtk.WindowHandle):

    def __init__(self):
        Gtk.WindowHandle.__init__(self)
        self.add_css_class('left')
        self.set_size_request(250, -1)

        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.set_child(self.box)

        # search
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text(_('Search') + '…')
        self.search_entry.add_css_class('flat')
        self.search_entry.add_css_class('search')
        self.search_entry.set_hexpand(True)
        self.box.append(self.search_entry)

        # workspace menu
        self.hamburger_menu_button = Gtk.Button.new_from_icon_name('open-menu-symbolic')
        self.hamburger_menu_button.set_can_focus(False)
        self.hamburger_menu_button.set_tooltip_text(_('Main Menu') + ' (F10)')
        self.hamburger_menu_button.add_css_class('flat')
        self.hamburger_menu_button.add_css_class('sidebar')
        self.hamburger_menu_button.set_action_name('win.show-hamburger-menu')
        self.box.append(self.hamburger_menu_button)


class HeaderBarRight(Gtk.WindowHandle):

    def __init__(self):
        Gtk.WindowHandle.__init__(self)
        self.add_css_class('right')

        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.set_child(self.box)

        self.back_button = Gtk.Button.new_from_icon_name('go-previous-symbolic')
        self.back_button.set_tooltip_text('Back (Alt+Left Arrow)')
        self.back_button.set_action_name('win.go-back')
        self.back_button.set_can_focus(False)
        self.back_button.add_css_class('flat')

        self.forward_button = Gtk.Button.new_from_icon_name('go-next-symbolic')
        self.forward_button.set_tooltip_text('Forward (Alt+Right Arrow)')
        self.forward_button.set_action_name('win.go-forward')
        self.forward_button.set_can_focus(False)
        self.forward_button.add_css_class('flat')

        self.back_forward_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.back_forward_box.append(self.back_button)
        self.back_forward_box.append(self.forward_button)
        self.back_forward_box.add_css_class('linked')
        self.back_forward_box.add_css_class('buttonbox')
        self.box.append(self.back_forward_box)

        self.history_overlay = Gtk.Overlay()
        self.box.append(self.history_overlay)

        self.add_document_button = Gtk.Button.new_from_icon_name('list-add-symbolic')
        self.add_document_button.set_action_name('win.add-document')
        self.add_document_button.set_can_focus(False)
        self.add_document_button.set_tooltip_text(_('New Document') + ' (' + _('Ctrl') + '+N)')
        self.add_document_button.add_css_class('flat')

        self.document_menu_button = Gtk.Button.new_from_icon_name('view-more-symbolic')
        self.document_menu_button.set_can_focus(False)
        self.document_menu_button.set_tooltip_text(_('Document Menu') + ' (F12)')
        self.document_menu_button.add_css_class('flat')
        self.document_menu_button.set_action_name('win.show-document-menu')

        self.add_docmenu_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add_docmenu_box.append(self.add_document_button)
        self.add_docmenu_box.append(self.document_menu_button)
        self.add_docmenu_box.add_css_class('buttonbox')
        self.box.append(self.add_docmenu_box)

        # window buttons
        self.window_controls = Gtk.WindowControls.new(Gtk.PackType.END)
        self.box.append(self.window_controls)


