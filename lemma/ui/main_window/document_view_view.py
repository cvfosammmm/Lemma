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
from gi.repository import Gtk, Gdk, Pango

from lemma.infrastructure.color_manager import ColorManager
from lemma.ui.main_window.context_menu import ContextMenu


class DocumentViewView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.set_size_request(770, -1)

        self.padding_left = 48
        self.padding_bottom = 120
        self.padding_top = 49
        self.title_height = 54
        self.subtitle_height = 50
        self.title_buttons_height = 0
        self.title_width = 500
        self.insert_height = 25
        self.insert_drawing_offset = 9

        self.layout_title = Pango.Layout(self.get_pango_context())
        self.layout_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_title.set_width(self.title_width * Pango.SCALE)
        self.layout_title.set_font_description(Pango.FontDescription.from_string('NewComputerModernSans10 Regular 36px'))

        self.layout_subtitle = Pango.Layout(self.get_pango_context())
        self.layout_subtitle.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_subtitle.set_width(self.title_width * Pango.SCALE)
        self.layout_subtitle.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.content = Gtk.DrawingArea()
        self.content.set_focusable(True)
        self.content.set_vexpand(True)

        self.set_child(self.content)

        self.scrollbar_x = Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL)
        self.scrollbar_x.set_valign(Gtk.Align.END)
        self.scrollbar_x.add_css_class('bottom')
        self.scrollbar_x.add_css_class('overlay-indicator')
        self.adjustment_x = self.scrollbar_x.get_adjustment()
        self.add_overlay(self.scrollbar_x)

        self.scrollbar_y = Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL)
        self.scrollbar_y.set_halign(Gtk.Align.END)
        self.scrollbar_y.add_css_class('right')
        self.scrollbar_y.add_css_class('overlay-indicator')
        self.adjustment_y = self.scrollbar_y.get_adjustment()
        self.add_overlay(self.scrollbar_y)

        self.link_overlay = Gtk.Label.new('http://url')
        self.link_overlay.set_valign(Gtk.Align.END)
        self.link_overlay.set_halign(Gtk.Align.END)
        self.link_overlay.add_css_class('link-overlay')
        self.add_overlay(self.link_overlay)

        self.context_menu = ContextMenuDocumentView(self.content)


class ContextMenuDocumentView(ContextMenu):
    
    def __init__(self, parent):
        ContextMenu.__init__(self)

        self.popover.set_parent(parent)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)

        self.back_button = self.create_button('Back', _('Alt') + '+Left Arrow')
        self.back_button.set_action_name('win.go-back')
        self.box.append(self.back_button)

        self.forward_button = self.create_button('Forward', _('Alt') + '+Right Arrow')
        self.forward_button.set_action_name('win.go-forward')
        self.box.append(self.forward_button)

        self.box.append(Gtk.Separator())

        self.undo_button = self.create_button('Undo', _('Ctrl') + '+Z')
        self.undo_button.set_action_name('win.undo')
        self.box.append(self.undo_button)

        self.redo_button = self.create_button('Redo', _('Shift') + '+' + _('Ctrl') + '+Z')
        self.redo_button.set_action_name('win.redo')
        self.box.append(self.redo_button)

        self.box.append(Gtk.Separator())

        self.cut_button = self.create_button('Cut', _('Ctrl') + '+X')
        self.cut_button.set_action_name('win.cut')
        self.box.append(self.cut_button)

        self.copy_button = self.create_button('Copy', _('Ctrl') + '+C')
        self.copy_button.set_action_name('win.copy')
        self.box.append(self.copy_button)

        self.paste_button = self.create_button('Paste', _('Ctrl') + '+V')
        self.paste_button.set_action_name('win.paste')
        self.box.append(self.paste_button)

        self.delete_button = self.create_button('Delete')
        self.delete_button.set_action_name('win.delete')
        self.box.append(self.delete_button)

        self.box.append(Gtk.Separator())

        self.select_all_button = self.create_button('Select All', _('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.box.append(self.select_all_button)

        self.link_buttons_separator = Gtk.Separator()
        self.box.append(self.link_buttons_separator)

        self.remove_link_button = self.create_button('Remove Link')
        self.remove_link_button.set_action_name('win.remove-link')
        self.box.append(self.remove_link_button)

        self.edit_link_button = self.create_button('Edit Link')
        self.edit_link_button.set_action_name('win.edit-link')
        self.box.append(self.edit_link_button)


