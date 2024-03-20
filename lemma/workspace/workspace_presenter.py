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

from lemma.app.service_locator import ServiceLocator


class WorkspacePresenter():

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.main_window = main_window

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('mode_set', self.on_mode_set)
        self.workspace.connect('theme_change', self.on_theme_change)

        self.update_colors()
        self.update_mode_stack()
        self.setup_paneds()

    def on_new_active_document(self, workspace, document=None):
        self.update_mode_stack()

    def on_mode_set(self, workspace):
        self.update_mode_stack()

    def on_theme_change(self, workspace):
        self.update_colors()

    def update_mode_stack(self):
        if self.workspace.mode == 'documents' and self.workspace.active_document != None:
            self.main_window.content_stack.set_visible_child_name('document_view')
        elif self.workspace.mode == 'draft':
            self.main_window.content_stack.set_visible_child_name('draft_view')
        else:
            self.main_window.content_stack.set_visible_child_name('welcome')

    def update_colors(self):
        path = os.path.join(ServiceLocator.get_resources_path(), 'themes', self.workspace.theme + '.css')
        self.main_window.css_provider_colors.load_from_path(path)

    def setup_paneds(self):
        show_tools_sidebar = self.workspace.settings.get_value('window_state', 'show_tools_sidebar')
        tools_sidebar_position = self.workspace.settings.get_value('window_state', 'tools_sidebar_position')

        if tools_sidebar_position in [None, -1]: self.main_window.document_view_paned.set_end_on_first_show()

        self.main_window.document_view_paned.first_set_show_widget(show_tools_sidebar)
        self.main_window.document_view_paned.set_target_position(tools_sidebar_position)
        self.main_window.headerbar.hb_right.tools_sidebar_toggle.set_active(show_tools_sidebar)


