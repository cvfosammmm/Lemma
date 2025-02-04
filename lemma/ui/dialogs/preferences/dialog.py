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

import lemma.ui.dialogs.preferences.preferences_viewgtk as view
import lemma.ui.dialogs.preferences.page_colors as page_colors
import lemma.ui.dialogs.preferences.page_workspace as page_workspace
from lemma.infrastructure.service_locator import ServiceLocator


class Dialog(object):

    def __init__(self, main_window, use_cases):
        self.main_window = main_window
        self.use_cases = use_cases
        self.settings = ServiceLocator.get_settings()

    def run(self):
        self.setup()
        self.view.present()

    def setup(self):
        self.view = view.Preferences(self.main_window)

        self.page_colors = page_colors.PageColors(self, self.settings, self.main_window, self.use_cases)
        self.page_workspace = page_workspace.PageWorkspace(self, self.settings, self.main_window, self.use_cases)

        self.view.notebook.append_page(self.page_colors.view, Gtk.Label.new(_('Colors')))
        self.view.notebook.append_page(self.page_workspace.view, Gtk.Label.new(_('Workspace')))

        self.page_colors.init()
        self.page_workspace.init()

    def on_check_button_toggle(self, button, preference_name):
        self.use_cases.settings_set_value('preferences', preference_name, button.get_active())
        
    def on_radio_button_toggle(self, button, preference_name, value):
        self.use_cases.settings_set_value('preferences', preference_name, value)

    def spin_button_changed(self, button, preference_name):
        self.use_cases.settings_set_value('preferences', preference_name, button.get_value_as_int())

    def text_deleted(self, buffer, position, n_chars, preference_name):
        self.use_cases.settings_set_value('preferences', preference_name, buffer.get_text())

    def text_inserted(self, buffer, position, chars, n_chars, preference_name):
        self.use_cases.settings_set_value('preferences', preference_name, buffer.get_text())

    def on_interpreter_changed(self, button, preference_name, value):
        self.use_cases.settings_set_value('preferences', preference_name, value)


