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

from lemma.settings.settings import Settings


class PageAutocomplete(object):

    def __init__(self, settings, main_window, use_cases):
        self.view = PageAutocompleteView()
        self.settings = settings
        self.main_window = main_window
        self.use_cases = use_cases

    def init(self):
        self.view.checkbox_stylized_latex.set_active(Settings.get_value('stylized_latex_autocomplete'))
        self.view.checkbox_stylized_latex.connect('toggled', self.on_checkbutton_toggled, 'stylized_latex_autocomplete')

    def on_checkbutton_toggled(self, button, key):
        self.use_cases.settings_set_value(key, button.get_active())


class PageAutocompleteView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('settings-page')

        self.checkbox_stylized_latex = Gtk.CheckButton.new_with_label(_('Suggest (stylized) LaTeX commands (starting with "\\")'))
        self.checkbox_stylized_latex.add_css_class('single')
        self.checkbox_stylized_latex.set_margin_top(18)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.append(self.checkbox_stylized_latex)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


