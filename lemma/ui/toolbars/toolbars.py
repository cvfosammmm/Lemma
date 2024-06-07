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

    def __init__(self, workspace, main_window, application):
        self.workspace = workspace
        self.main_window = main_window
        self.application = application
        self.toolbar = main_window.toolbar

        self.toolbar.tools_sidebar_toggle.set_active(ServiceLocator.get_settings().get_value('window_state', 'show_tools_sidebar'))
        self.toolbar.tools_sidebar_toggle.connect('toggled', self.on_tools_sidebar_toggle_toggled)
        self.update()

    def update(self):
        self.update_tag_toggle(self.toolbar.bold_button, 'bold')
        self.update_tag_toggle(self.toolbar.italic_button, 'italic')

    def update_tag_toggle(self, button, tagname):
        document = self.workspace.active_document
        if self.workspace.mode != 'documents' or document == None: return

        char_nodes = [node for node in document.ast.get_subtree(*document.ast.get_cursor_state()) if node.is_char()]
        all_tagged = True
        for node in char_nodes:
            if tagname not in node.tags: all_tagged = False

        if len(char_nodes) > 0:
            if all_tagged:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')
        else:
            if tagname in self.application.tags_at_cursor:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')

    def on_tools_sidebar_toggle_toggled(self, toggle_button, parameter=None):
        self.main_window.document_view_paned.set_show_widget(toggle_button.get_active())
        self.main_window.document_view_paned.animate(True)


