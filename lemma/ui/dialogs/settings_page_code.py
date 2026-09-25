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

from lemma.services.settings import Settings
from lemma.use_cases.use_cases import UseCases


class PageCode(object):

    def __init__(self, settings, main_window):
        self.view = PageCodeView()
        self.settings = settings
        self.main_window = main_window

    def init(self):
        self.view.checkbox_spaces.set_active(Settings.get_value('indent_code_with_spaces'))
        self.view.checkbox_spaces.connect('toggled', self.on_checkbutton_toggled, 'indent_code_with_spaces')

        self.view.tab_width_spinner.set_value(Settings.get_value('code_tab_width'))
        self.view.tab_width_spinner.connect('value-changed', self.on_tab_width_changed)

    def on_checkbutton_toggled(self, button, key):
        UseCases.settings_set_value(key, button.get_active())

    def on_tab_width_changed(self, spin_button):
        UseCases.settings_set_value('code_tab_width', spin_button.get_value_as_int())


class PageCodeView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('settings-page')

        self.tabs_header = Gtk.Label.new(_('Tab Stops'))
        self.tabs_header.add_css_class('settings-header')
        self.tabs_header.set_xalign(0)
        self.tabs_header.set_margin_top(21)

        self.checkbox_spaces = Gtk.CheckButton.new_with_label(_('Insert spaces instead of tabs in code cells'))
        self.checkbox_spaces.add_css_class('single')
        self.checkbox_spaces.set_margin_top(18)

        self.tab_width_header = Gtk.Label.new(_('Set Tab Width:'))
        self.tab_width_header.add_css_class('settings-subheader')
        self.tab_width_header.set_xalign(0)
        self.tab_width_header.set_margin_top(21)

        self.tab_width_spinner = Gtk.SpinButton.new_with_range(0, 8, 1)
        self.tab_width_spinner_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.tab_width_spinner_box.add_css_class('settings-margin-box')
        self.tab_width_spinner_box.append(self.tab_width_spinner)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.append(self.tabs_header)
        self.vbox.append(self.checkbox_spaces)
        self.vbox.append(self.tab_width_header)
        self.vbox.append(self.tab_width_spinner_box)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


