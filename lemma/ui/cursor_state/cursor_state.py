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

from lemma.helpers.observable import Observable


class CursorState(Observable):

    def __init__(self, workspace, main_window):
        Observable.__init__(self)
        self.toolbar = main_window.toolbar

        self.tags_at_cursor = set()

        self.workspace = workspace
        self.document = None

        self.set_document(workspace.get_active_document())
        self.workspace.connect('new_active_document', self.on_new_active_document)

    def on_new_active_document(self, workspace, document=None):
        self.set_document(document)
        self.update()

    def set_document(self, document):
        if self.document != None:
            self.document.disconnect('changed', self.on_change)

        self.document = document
        self.update()

        if document != None:
            self.document.connect('changed', self.on_change)

    def on_change(self, document):
        self.update()

    def update(self):
        self.update_tags_at_cursor()
        self.update_paragraph_style_at_cursor()

    def update_tags_at_cursor(self):
        if self.document == None:
            self.set_tags_at_cursor(set())
        else:
            node = self.document.ast.get_node_at_position(self.document.cursor.get_first_cursor_pos())
            node = node.prev_in_parent()
            if node == None:
                self.set_tags_at_cursor(set())
            else:
                self.set_tags_at_cursor(node.tags.copy())

    def set_tags_at_cursor(self, tags):
        self.tags_at_cursor = tags
        self.update_tag_toggle(self.toolbar.toolbar_main.bold_button, 'bold')
        self.update_tag_toggle(self.toolbar.toolbar_main.italic_button, 'italic')

    def update_tag_toggle(self, button, tagname):
        document = self.workspace.active_document
        if self.workspace.mode != 'documents' or document == None: return

        char_nodes = [node for node in document.ast.get_subtree(*document.cursor.get_state()) if node.is_char()]
        all_tagged = True
        for node in char_nodes:
            if tagname not in node.tags: all_tagged = False

        if len(char_nodes) > 0:
            if all_tagged:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')
        else:
            if tagname in self.tags_at_cursor:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')

    def update_paragraph_style_at_cursor(self):
        document = self.workspace.active_document
        if self.workspace.mode != 'documents' or document == None: return

        current_node = document.ast.get_node_at_position(document.cursor.get_first_cursor_pos())
        paragraph_style_at_cursor = current_node.paragraph_style

        labels_dict = {'p': _('Paragraph'), 'h1': _('Heading 2'), 'h2': _('Heading 2'), 'h3': _('Heading 3'), 'h4': _('Heading 4'), 'h5': _('Heading 5'), 'h6': _('Heading 6')}
        self.toolbar.toolbar_main.paragraph_style_menu_button_label.set_text(labels_dict[paragraph_style_at_cursor])


