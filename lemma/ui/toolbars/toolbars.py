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

from lemma.infrastructure.service_locator import ServiceLocator


class Toolbars(object):

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.main_window = main_window
        self.toolbar = main_window.toolbar

        self.toolbar.tools_sidebar_toggle.set_active(ServiceLocator.get_settings().get_value('window_state', 'show_tools_sidebar'))
        self.toolbar.tools_sidebar_toggle.connect('toggled', self.on_tools_sidebar_toggle_toggled)
        self.toolbar.bold_button.connect('clicked', self.on_tag_button_clicked, 'bold')
        self.toolbar.italic_button.connect('clicked', self.on_tag_button_clicked, 'italic')

        self.update()

    def update(self):
        document = self.workspace.active_document
        if self.workspace.mode != 'documents' or document == None: return

        char_nodes = [node for node in document.ast.get_subtree(*document.ast.get_cursor_state()) if node.is_char()]
        self.toolbar.bold_button.set_sensitive(len(char_nodes) > 0)
        self.toolbar.italic_button.set_sensitive(len(char_nodes) > 0)

        all_bold = True
        all_italic = True
        for node in char_nodes:
            if 'bold' not in node.tags: all_bold = False
            if 'italic' not in node.tags: all_italic = False
        self.toolbar.bold_button.set_active(len(char_nodes) > 0 and all_bold)
        self.toolbar.italic_button.set_active(len(char_nodes) > 0 and all_italic)

    def on_tag_button_clicked(self, button, parameter):
        document = self.workspace.active_document
        if button.get_active():
            document.add_command('add_tag', parameter)
        else:
            document.add_command('remove_tag', parameter)

    def on_tools_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.main_window.document_view_paned.set_show_widget(toggle_button.get_active())
        self.main_window.document_view_paned.animate(True)


