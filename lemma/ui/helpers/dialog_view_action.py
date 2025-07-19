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

import lemma.ui.helpers.filechooser_button_save as filechooser_button_save
from lemma.ui.shortcuts import ShortcutController


class DialogViewAction(Gtk.Window):

    def __init__(self, main_window, name, default_width, css_class, action_label):
        Gtk.Window.__init__(self)
        self.add_css_class(css_class)
        self.add_css_class('action-dialog')
        self.set_default_size(default_width, -1)

        self.set_modal(True)
        self.set_transient_for(main_window)
        self.set_destroy_with_parent(True)
        self.set_can_focus(False)

        header_label = Gtk.Label.new(name)
        header_label.add_css_class('title')

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_title_buttons(True)
        self.headerbar.set_title_widget(Gtk.Label.new(''))
        self.headerbar.pack_start(header_label)

        self.set_titlebar(self.headerbar)

        self.topbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.topbox.set_size_request(default_width, -1)
        self.set_child(self.topbox)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.topbox.append(self.content)

        self.shortcuts_controller = ShortcutController()
        self.shortcuts_controller.add_with_callback('Escape', self.close)
        self.add_controller(self.shortcuts_controller)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)

        self.submit_button = Gtk.Button.new_with_mnemonic(action_label)
        self.submit_button.set_can_focus(False)
        self.submit_button.add_css_class('suggested-action')

        self.action_bar = Gtk.ActionBar()
        self.action_bar.pack_start(self.cancel_button)
        self.action_bar.pack_end(self.submit_button)
        self.topbox.append(self.action_bar)

    def add_header_label(self, markup):
        label = Gtk.Label()
        label.set_markup(markup)
        label.set_xalign(0)
        label.add_css_class('header')
        self.content.append(label)
        return label

    def add_explainer_label(self, markup):
        label = Gtk.Label()
        label.set_markup(markup)
        label.set_xalign(0)
        label.set_wrap(True)
        label.add_css_class('explainer')
        self.content.append(label)
        return label

    def add_radio_group(self, choices):
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_dict = {}

        first_button = None
        for value, name in choices.items():
            button = Gtk.CheckButton.new_with_label(name)
            button.add_css_class('radio-group')
            hbox.append(button)
            button_dict[value] = button

            if first_button == None:
                first_button = button
            else:
                button.set_group(first_button)

        self.content.append(hbox)
        return button_dict

    def add_file_chooser_button_save(self):
        file_chooser_button = filechooser_button_save.FilechooserButton(self)

        self.content.append(file_chooser_button.view)
        return file_chooser_button


