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
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk
from gi.repository import Adw

from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.use_cases.use_cases import UseCases


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)
        self.add_css_class('bookmarks')

        self.set_width(306)

        self.edit_mode = False
        self.bookmark_drag_handles = []
        self.bookmark_drag_handle_revealers = []
        self.bookmark_buttons = []
        self.bookmark_button_labels = []
        self.bookmark_remove_buttons = []
        self.bookmark_remove_button_revealers = []
        self.bookmark_button_boxes = []
        self.bookmark_revealers = []

        self.headline = Gtk.Label.new('Bookmarks')
        self.headline.add_css_class('title-2')
        self.headline.set_xalign(0)
        self.headline.set_margin_bottom(2)

        self.edit_bookmarks_button = Gtk.Button.new_from_icon_name('edit-symbolic')
        self.edit_bookmarks_button.add_css_class('flat')
        self.edit_bookmarks_button.set_can_focus(False)
        self.done_editing_button = MenuBuilder.create_button(_('Done'))
        edit_button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        edit_button_box.set_margin_top(4)
        edit_button_box.append(self.edit_bookmarks_button)
        edit_button_box.append(self.done_editing_button)

        self.header_box = Gtk.CenterBox()
        self.header_box.add_css_class('header-box')
        self.header_box.set_start_widget(self.headline)
        self.header_box.set_end_widget(edit_button_box)
        self.add_widget(self.header_box)

        for i in range(9):
            title_label = Gtk.Label()

            drag_handle = Gtk.Image.new_from_icon_name('drag-handle-symbolic')
            drag_handle.add_css_class('drag-handle')
            drag_handle.set_cursor_from_name('grab')

            drag_handle_revealer = Gtk.Revealer()
            drag_handle_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
            drag_handle_revealer.set_child(drag_handle)

            shortcut_label = Gtk.Label.new(_('Alt') + '+' + str(i + 1))
            shortcut_label.add_css_class('shortcut')
            shortcut_label.set_xalign(1)
            shortcut_label.set_hexpand(True)

            button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            button_box.append(title_label)
            button_box.append(shortcut_label)

            button = Gtk.Button()
            button.set_child(button_box)
            button.add_css_class('action')
            button.set_can_focus(False)
            button.add_css_class('flat')
            self.register_button_for_keyboard_navigation(button)

            label = Gtk.Label()
            label.set_xalign(0)
            label.set_hexpand(True)

            close_button = Gtk.Button.new_from_icon_name('cross-small-symbolic')
            close_button.add_css_class('flat')
            close_button.set_can_focus(False)

            close_button_revealer = Gtk.Revealer()
            close_button_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
            close_button_revealer.set_child(close_button)

            button_box_outer = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            button_box_outer.append(drag_handle_revealer)
            button_box_outer.append(button)
            button_box_outer.append(close_button_revealer)

            revealer = Gtk.Revealer()
            revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
            revealer.set_child(button_box_outer)

            self.add_widget(revealer)

            self.bookmark_drag_handles.append(drag_handle)
            self.bookmark_drag_handle_revealers.append(drag_handle_revealer)
            self.bookmark_buttons.append(button)
            self.bookmark_button_labels.append(title_label)
            self.bookmark_remove_buttons.append(close_button)
            self.bookmark_remove_button_revealers.append(close_button_revealer)
            self.bookmark_button_boxes.append(button_box_outer)
            self.bookmark_revealers.append(revealer)

        self.empty_state = Adw.StatusPage()
        self.empty_state.set_icon_name('library-symbolic')
        self.empty_state.set_title('No Bookmarks')
        self.empty_state.set_description(_('Bookmarked documents will appear here for quick access.'))
        self.empty_state.add_css_class('compact')
        self.empty_state.add_css_class('dimmed')
        self.add_widget(self.empty_state)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.bookmark_document_button = MenuBuilder.create_button(_('Bookmark Current Document'))
        self.register_button_for_keyboard_navigation(self.bookmark_document_button)
        self.add_widget(self.bookmark_document_button)

        self.unbookmark_document_button = MenuBuilder.create_button(_('Remove Current Document'))
        self.register_button_for_keyboard_navigation(self.unbookmark_document_button)
        self.add_widget(self.unbookmark_document_button)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('0'):
            if state & modifiers == Gdk.ModifierType.ALT_MASK:
                UseCases.hide_popovers()

                return True

        return super().on_keypress(controller, keyval, keycode, state)

    def on_popup(self):
        self.edit_mode = False

    def on_popdown(self):
        self.edit_mode = False


