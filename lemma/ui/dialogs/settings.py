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

import lemma.ui.dialogs.settings_view as view
import lemma.ui.dialogs.settings_page_colors as page_colors
import lemma.ui.dialogs.settings_page_workspace as page_workspace
import lemma.ui.dialogs.settings_page_toolbars as page_toolbars
import lemma.ui.dialogs.settings_page_autocomplete as page_autocomplete
import lemma.ui.dialogs.settings_page_storage as page_storage
from lemma.use_cases.use_cases import UseCases


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.present()

    def setup(self, visible_page_name='Colors'):
        self.view = view.Settings(self.main_window)

        self.pages = []
        self.pages.append(['Colors', 'preferences-color-symbolic', page_colors.PageColors(self, self.main_window)])
        self.pages.append(['Workspace', 'overlapping-windows-symbolic', page_workspace.PageWorkspace(self, self.main_window)])
        self.pages.append(['Toolbars', 'preferences-system-symbolic', page_toolbars.PageToolbars(self, self.main_window)])
        self.pages.append(['Autocomplete', 'completion-snippet-symbolic', page_autocomplete.PageAutocomplete(self, self.main_window)])
        self.pages.append(['Storage', 'drawer-symbolic', page_storage.PageStorage(self, self.main_window)])

        for title, icon_name, page in self.pages:
            self.view.add_page(title, icon_name, page.view)
            page.init()

        self.view.set_visible_page(visible_page_name)


