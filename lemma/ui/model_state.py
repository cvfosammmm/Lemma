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
from gi.repository import Gdk

from lemma.application_state.application_state import ApplicationState
from lemma.infrastructure.layout_info import LayoutInfo
from lemma.history.history import History
import lemma.infrastructure.timer as timer


class ModelState(object):

    def __init__(self, main_window):
        self.main_window = main_window

        self.document = None
        self.mode = None
        self.has_active_doc = None
        self.selected_nodes = None
        self.prev_doc = None
        self.next_doc = None
        self.can_undo = None
        self.can_redo = None
        self.insert_in_line = None
        self.has_selection = None
        self.clipboard_formats = None
        self.text_in_clipboard = None
        self.subtree_in_clipboard = None
        self.links_inside_selection = None
        self.widget_selected = None
        self.selected_widget_is_max = None
        self.selected_widget_is_min = None
        self.cursor_inside_link = None
        self.remove_link_active = None
        self.edit_link_active = None

    @timer.timer
    def update(self):
        self.document = History.get_active_document()
        self.mode = ApplicationState.get_value('mode')
        self.has_active_doc = (self.mode == 'documents' and self.document != None)
        self.selected_nodes = self.document.ast.get_subtree(*self.document.cursor.get_state()) if self.has_active_doc else []

        self.prev_doc = History.get_previous_if_any(self.document)
        self.next_doc = History.get_next_if_any(self.document)
        self.can_undo = self.has_active_doc and self.document.can_undo()
        self.can_redo = self.has_active_doc and self.document.can_redo()
        self.insert_in_line = self.has_active_doc and self.document.cursor.get_insert_node().parent.type == 'root'
        self.has_selection = self.has_active_doc and self.document.cursor.has_selection()
        self.clipboard_formats = Gdk.Display.get_default().get_clipboard().get_formats().to_string()
        self.text_in_clipboard = 'text/plain;charset=utf-8' in self.clipboard_formats
        self.subtree_in_clipboard = 'lemma/ast' in self.clipboard_formats
        self.links_inside_selection = self.has_active_doc and len([node for node in self.selected_nodes if node.link != None]) > 0
        self.whole_selection_is_one_link = self.links_inside_selection and (len(set([node.link for node in self.selected_nodes])) == 1)
        self.widget_selected = len(self.selected_nodes) == 1 and self.selected_nodes[0].type == 'widget'
        self.selected_widget_is_max = self.widget_selected and (self.selected_nodes[0].value.get_width() == LayoutInfo.get_layout_width() or not self.selected_nodes[0].value.is_resizable())
        self.selected_widget_is_min = self.widget_selected and (self.selected_nodes[0].value.get_width() == self.selected_nodes[0].value.get_minimum_width() or not self.selected_nodes[0].value.is_resizable())
        self.cursor_inside_link = self.has_active_doc and self.document.cursor.get_insert_node().is_inside_link()

        self.remove_link_active = (self.has_active_doc and (self.links_inside_selection or ((not self.has_selection) and self.cursor_inside_link)))
        self.edit_link_active = (self.has_active_doc and (self.whole_selection_is_one_link or (not self.has_selection) and self.cursor_inside_link))
        self.copy_link_active = self.edit_link_active
        self.open_link_active = (self.has_active_doc and not self.has_selection and self.document.cursor.get_insert_node().is_inside_link())


