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

from lemma.infrastructure.service_locator import ServiceLocator


class Panels(object):

    def __init__(self, workspace, main_window, app):
        self.workspace = workspace
        self.main_window = main_window
        self.app = app
        self.settings = ServiceLocator.get_settings()

        self.app.actions.actions['quit'].connect('activate', self.on_quit_action)
        self.main_window.connect('close-request', self.on_window_close)
        self.main_window.toolbar.symbols_sidebar_toggle.set_active(ServiceLocator.get_settings().get_value('window_state', 'show_tools_sidebar'))
        self.main_window.toolbar.symbols_sidebar_toggle.connect('toggled', self.on_tools_sidebar_toggle_toggled)

        self.restore_window_state()

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('mode_set', self.on_mode_set)
        self.update()

    def on_new_active_document(self, workspace, document=None): self.update()
    def on_mode_set(self, workspace): self.update()

    def update(self):
        if self.workspace.mode == 'documents' and self.workspace.active_document != None:
            self.main_window.content_stack.set_visible_child_name('document_view')
        elif self.workspace.mode == 'draft':
            self.main_window.content_stack.set_visible_child_name('draft_view')
        else:
            self.main_window.content_stack.set_visible_child_name('welcome')

    def on_tools_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.main_window.document_view_paned.set_show_widget(toggle_button.get_active())
        self.main_window.document_view_paned.animate(True)

    def on_window_close(self, window=None, parameter=None):
        self.save_quit()
        return True

    def on_quit_action(self, action=None, parameter=None):
        self.save_quit()

    def save_quit(self):
        self.save_window_state()
        self.app.quit()

    def restore_window_state(self):
        if self.settings.get_value('window_state', 'is_maximized'): self.main_window.maximize()
        else: self.main_window.unmaximize()
        window_width = self.settings.get_value('window_state', 'width')
        window_height = self.settings.get_value('window_state', 'height')
        self.main_window.set_default_size(window_width, window_height)
        self.main_window.headerbar.set_position(self.settings.get_value('window_state', 'sidebar_position'))
        self.main_window.present()

        show_tools_sidebar = self.settings.get_value('window_state', 'show_tools_sidebar')
        tools_sidebar_position = self.settings.get_value('window_state', 'tools_sidebar_position')

        if tools_sidebar_position in [None, -1]: self.main_window.document_view_paned.set_end_on_first_show()

        self.main_window.document_view_paned.first_set_show_widget(show_tools_sidebar)
        self.main_window.document_view_paned.set_target_position(tools_sidebar_position)

    def save_window_state(self):
        self.settings.set_value('window_state', 'width', self.main_window.get_property('default-width'))
        self.settings.set_value('window_state', 'height', self.main_window.get_property('default-height'))
        self.settings.set_value('window_state', 'is_maximized', self.main_window.get_property('maximized'))
        self.settings.set_value('window_state', 'sidebar_position', self.main_window.headerbar.get_property('position'))
        self.settings.set_value('window_state', 'show_tools_sidebar', self.main_window.document_view_paned.show_widget)
        self.settings.set_value('window_state', 'tools_sidebar_position', self.main_window.document_view_paned.target_position)
        self.settings.pickle()


