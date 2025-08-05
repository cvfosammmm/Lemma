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

import lemma.ui.dialogs.settings.settings_viewgtk as view
import lemma.ui.dialogs.settings.page_colors as page_colors
import lemma.ui.dialogs.settings.page_workspace as page_workspace
import lemma.ui.dialogs.settings.page_autocomplete as page_autocomplete
from lemma.use_cases.use_cases import UseCases


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.present()

    def setup(self):
        self.view = view.Settings(self.main_window)

        self.page_colors = page_colors.PageColors(self, self.main_window)
        self.page_workspace = page_workspace.PageWorkspace(self, self.main_window)
        self.page_autocomplete = page_autocomplete.PageAutocomplete(self, self.main_window)

        self.view.notebook.append_page(self.page_colors.view, Gtk.Label.new(_('Colors')))
        self.view.notebook.append_page(self.page_workspace.view, Gtk.Label.new(_('Workspace')))
        self.view.notebook.append_page(self.page_autocomplete.view, Gtk.Label.new(_('Autocomplete')))

        self.page_colors.init()
        self.page_workspace.init()
        self.page_autocomplete.init()

    def on_check_button_toggle(self, button, setting_name):
        UseCases.settings_set_value(setting_name, button.get_active())
        
    def on_radio_button_toggle(self, button, setting_name, value):
        UseCases.settings_set_value(setting_name, value)

    def spin_button_changed(self, button, setting_name):
        UseCases.settings_set_value(setting_name, button.get_value_as_int())

    def text_deleted(self, buffer, position, n_chars, setting_name):
        UseCases.settings_set_value(setting_name, buffer.get_text())

    def text_inserted(self, buffer, position, chars, n_chars, setting_name):
        UseCases.settings_set_value(setting_name, buffer.get_text())

    def on_interpreter_changed(self, button, setting_name, value):
        UseCases.settings_set_value(setting_name, value)


