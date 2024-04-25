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


class Toolbars(object):

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.main_window = main_window

        self.main_window.headerbar.hb_right.tools_sidebar_toggle.connect('toggled', self.on_tools_sidebar_toggle_toggled)

        self.update()

    def update(self):
        pass

    def on_tools_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.main_window.document_view_paned.set_show_widget(toggle_button.get_active())
        self.main_window.document_view_paned.animate(True)


