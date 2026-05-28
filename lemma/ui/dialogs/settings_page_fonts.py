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


class PageFonts(object):

    def __init__(self, settings, main_window):
        self.view = PageFontsView()
        self.settings = settings
        self.main_window = main_window

        self.theme_choices = dict()

    def init(self):
        for name in ['default', 'Sans-serif']:
            self.add_theme_choice(name)

    def add_theme_choice(self, name):
        button = Gtk.CheckButton.new_with_label(name)
        if 'default' in self.theme_choices:
            button.set_group(self.theme_choices['default'])
        button.set_active(Settings.get_value('font_theme') == name)
        button.add_css_class('single')
        button.connect('toggled', self.on_theme_choice_toggled, name)
        self.theme_choices[name] = button
        self.view.radio_buttons.append(button)

    def on_theme_choice_toggled(self, button, name):
        if button.get_active():
            UseCases.settings_set_value('font_theme', name)
            UseCases.invalidate_document_layout()


class PageFontsView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('settings-page')
        self.add_css_class('settings-page-fonts')

        self.radio_buttons = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.radio_buttons.set_margin_top(18)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.append(self.radio_buttons)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


