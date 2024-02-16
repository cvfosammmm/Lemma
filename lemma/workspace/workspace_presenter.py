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
        self.init()

    def on_new_active_document(self, workspace, document=None):
        self.init()

    def on_mode_set(self, workspace):
        self.init()

    def on_theme_change(self, workspace):
        self.update_colors()

    def init(self):
        if self.workspace.mode == 'documents' and self.workspace.active_document != None:
            self.init_document_mode()
        elif self.workspace.mode == 'draft':
            self.init_draft_mode()
        else:
            self.init_welcome_mode()

    def init_document_mode(self):
        self.workspace.document_view.set_document(self.workspace.active_document)
        self.main_window.content_stack.set_visible_child_name('document_view')

    def init_welcome_mode(self):
        self.main_window.content_stack.set_visible_child_name('welcome')
        self.main_window.welcome.button.grab_focus()

    def init_draft_mode(self):
        self.main_window.content_stack.set_visible_child_name('draft_view')
        self.workspace.document_draft_view.init()

    def update_colors(self):
        path = os.path.join(ServiceLocator.get_resources_path(), 'themes', self.workspace.theme + '.css')
        self.main_window.css_provider_colors.load_from_path(path)


