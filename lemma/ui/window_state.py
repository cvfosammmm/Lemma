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

import os.path

from lemma.services.settings import Settings
from lemma.application_state.application_state import ApplicationState
from lemma.document_repo.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases


class WindowState(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.toolbar_right = self.main_window.toolbar.toolbar_right

        self.toolbar_right.symbols_sidebar_toggle.connect('clicked', self.on_tools_sidebar_toggle_clicked, 'math')
        self.toolbar_right.emoji_sidebar_toggle.connect('clicked', self.on_tools_sidebar_toggle_clicked, 'emojis')

        toggle_state = Settings.get_value('show_backlinks')
        self.main_window.navigation_sidebar.backlinks_toggle.set_active(toggle_state)
        self.main_window.navigation_sidebar.backlinks_toggle.connect('toggled', self.on_backlinks_toggle_toggled)

        self.restore_window_state()

    def update(self):
        mode = ApplicationState.get_value('mode')

        if mode == 'documents' and DocumentRepo.get_active_document() != None:
            self.main_window.content_stack.set_visible_child_name('document_view')
        elif mode == 'draft':
            self.main_window.content_stack.set_visible_child_name('draft_view')
        else:
            self.main_window.content_stack.set_visible_child_name('welcome')

        sidebar_visible = Settings.get_value('show_tools_sidebar')
        active_tab = Settings.get_value('tools_sidebar_active_tab')

        self.update_toggle(self.toolbar_right.symbols_sidebar_toggle, sidebar_visible and active_tab == 'math')
        self.update_toggle(self.toolbar_right.emoji_sidebar_toggle, sidebar_visible and active_tab == 'emojis')

        self.main_window.tools_sidebar.set_visible_child_name(active_tab)
        self.main_window.document_view_paned.set_show_widget(sidebar_visible)
        self.main_window.document_view_paned.animate(True)

    def on_tools_sidebar_toggle_clicked(self, button, name):
        UseCases.toggle_tools_sidebar(name)

    def update_toggle(self, button, new_state):
        if new_state == True:
            button.add_css_class('checked')
        else:
            button.remove_css_class('checked')

    def on_backlinks_toggle_toggled(self, button, parameter=None):
        self.main_window.navigation_sidebar.paned.set_show_widget(button.get_active())
        self.main_window.navigation_sidebar.paned.animate(True)

    def restore_window_state(self):
        if Settings.get_value('is_maximized'): self.main_window.maximize()
        else: self.main_window.unmaximize()
        window_width = Settings.get_value('width')
        window_height = Settings.get_value('height')
        self.main_window.set_default_size(window_width, window_height)
        self.main_window.headerbar.set_position(Settings.get_value('sidebar_position'))
        self.main_window.present()

        show_tools_sidebar = Settings.get_value('show_tools_sidebar')
        tools_sidebar_position = Settings.get_value('tools_sidebar_position')

        if tools_sidebar_position in [None, -1]: self.main_window.document_view_paned.set_end_on_first_show()

        self.main_window.document_view_paned.first_set_show_widget(show_tools_sidebar)
        self.main_window.document_view_paned.set_target_position(tools_sidebar_position)

        show_backlinks = Settings.get_value('show_backlinks')
        navbar_paned_position = Settings.get_value('navbar_paned_position')

        if navbar_paned_position in [None, -1]: self.main_window.navigation_sidebar.paned.set_end_on_first_show()

        self.main_window.navigation_sidebar.paned.first_set_show_widget(show_backlinks)
        self.main_window.navigation_sidebar.paned.set_target_position(navbar_paned_position)

    def save_window_state(self):
        UseCases.settings_set_value('width', self.main_window.get_property('default-width'))
        UseCases.settings_set_value('height', self.main_window.get_property('default-height'))
        UseCases.settings_set_value('is_maximized', self.main_window.get_property('maximized'))
        UseCases.settings_set_value('sidebar_position', self.main_window.headerbar.get_property('position'))
        UseCases.settings_set_value('tools_sidebar_position', self.main_window.document_view_paned.target_position)
        UseCases.settings_set_value('show_backlinks', self.main_window.navigation_sidebar.paned.show_widget)
        UseCases.settings_set_value('navbar_paned_position', self.main_window.navigation_sidebar.paned.target_position)


