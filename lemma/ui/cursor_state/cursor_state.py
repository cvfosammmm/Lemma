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

from lemma.history.history import History
from lemma.application_state.application_state import ApplicationState
from lemma.message_bus.message_bus import MessageBus
import lemma.infrastructure.timer as timer


class CursorState():

    def __init__(self, main_window, application):
        self.toolbar = main_window.toolbar
        self.use_cases = application.use_cases

        MessageBus.connect('history_changed', self.on_history_changed)
        MessageBus.connect('document_changed', self.on_document_change)
        MessageBus.connect('app_state_changed', self.on_app_state_changed)

    def on_history_changed(self): self.update()
    def on_document_change(self): self.update()
    def on_app_state_changed(self):
        self.update_tag_toggle(self.toolbar.toolbar_main.bold_button, 'bold')
        self.update_tag_toggle(self.toolbar.toolbar_main.italic_button, 'italic')

    def update(self):
        self.update_tags_at_cursor()
        self.update_paragraph_style_at_cursor()
        self.update_tag_toggle(self.toolbar.toolbar_main.bold_button, 'bold')
        self.update_tag_toggle(self.toolbar.toolbar_main.italic_button, 'italic')

    def update_tags_at_cursor(self):
        document = History.get_active_document()

        if document == None:
            self.use_cases.app_state_set_value('tags_at_cursor', set())
        else:
            node = document.cursor.get_first_node()
            node = node.prev_in_parent()
            if node == None:
                self.use_cases.app_state_set_value('tags_at_cursor', set())
            else:
                self.use_cases.app_state_set_value('tags_at_cursor', node.tags.copy())

    def update_tag_toggle(self, button, tagname):
        document = History.get_active_document()
        if document == None: return

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
            if tagname in ApplicationState.get_value('tags_at_cursor'):
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')

    def update_paragraph_style_at_cursor(self):
        document = History.get_active_document()
        if document == None: return

        current_node = document.cursor.get_first_node()
        paragraph_style_at_cursor = current_node.get_paragraph_style()

        labels_dict = {'p': _('Paragraph'), 'h1': _('Heading 2'), 'h2': _('Heading 2'), 'h3': _('Heading 3'), 'h4': _('Heading 4'), 'h5': _('Heading 5'), 'h6': _('Heading 6')}
        self.toolbar.toolbar_main.paragraph_style_menu_button_label.set_text(labels_dict[paragraph_style_at_cursor])


