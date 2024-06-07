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
from gi.repository import Gtk, Gdk

from lemma.ui.document_view.document_view_controller import DocumentViewController
from lemma.ui.document_view.document_view_presenter import DocumentViewPresenter
from lemma.ui.title_widget.title_widget import TitleWidget
from lemma.ui.context_menus.document_view import ContextMenuDocumentView
from lemma.helpers.observable import Observable


class DocumentView(Observable):

    def __init__(self, workspace, main_window):
        Observable.__init__(self)
        self.main_window = main_window
        self.view = main_window.document_view

        self.controller = DocumentViewController(self)
        self.presenter = DocumentViewPresenter(self)

        self.title_widget = TitleWidget(self)
        self.title_widget.view.title_entry.connect('activate', self.on_entry_activate)
        self.title_widget.view.submit_button.connect('clicked', self.on_submit_button_clicked)
        self.title_widget.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.key_controller_window = Gtk.EventControllerKey()
        self.key_controller_window.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_window.connect('key-pressed', self.on_entry_keypress)
        self.title_widget.view.title_entry.add_controller(self.key_controller_window)
        self.view.add_overlay(self.title_widget.view)

        self.context_menu = ContextMenuDocumentView(self)

        self.workspace = workspace
        self.document = None
        self.set_document(workspace.get_active_document())
        self.add_change_code('changed')

        self.selected_link_target = None
        self.link_target_at_cursor = None
        self.tags_at_cursor = set()

        self.workspace.connect('new_active_document', self.on_new_active_document)

    def on_new_active_document(self, workspace, document=None):
        self.set_document(document)
        self.add_change_code('changed')

    def set_document(self, document):
        if self.document != None:
            self.document.disconnect('changed', self.on_change)

        self.document = document
        self.update_tags_at_cursor()
        self.update_link_at_cursor()
        self.view.content.queue_draw()
        self.stop_renaming()
        self.title_widget.set_document(document)
        self.view.content.grab_focus()

        if document != None:
            self.document.connect('changed', self.on_change)

    def on_change(self, document):
        self.update_tags_at_cursor()
        self.update_link_at_cursor()
        self.add_change_code('changed')

    def init_renaming(self):
        if self.document != None:
            self.title_widget.activate()
            self.view.scrolling_widget.scroll_to_position([0, 0])
            self.title_widget.view.set_visible(True)
            self.view.title_buttons_height = 50
            self.view.content.queue_draw()
            self.title_widget.grab_focus()

    def stop_renaming(self):
        self.title_widget.deactivate()
        self.title_widget.view.set_visible(False)
        self.view.title_buttons_height = 0
        self.view.content.grab_focus()

    def on_entry_activate(self, entry=None):
        if self.title_widget.validation_state:
            self.submit()

    def on_submit_button_clicked(self, widget=None):
        if self.title_widget.validation_state:
            self.submit()

    def submit(self):
        self.workspace.update_document_title(self.document.title, self.title_widget.title)
        self.document.set_title(self.title_widget.title)
        self.stop_renaming()

    def on_entry_keypress(self, controller, keyval, keycode, state):
        if keyval == Gdk.keyval_from_name('Escape'):
            if state & Gtk.accelerator_get_default_mod_mask() == 0:
                self.cancel()
                return True
        return False

    def on_cancel_button_clicked(self, widget=None):
        self.cancel()

    def cancel(self):
        self.title_widget.reset_title()
        self.stop_renaming()

    def update_link_at_cursor(self):
        if self.document == None:
            self.link_target_at_cursor = None
        else:
            current_node = self.document.ast.get_node_at_position(self.document.ast.get_first_cursor_pos())
            prev_node = current_node.prev_in_parent()
            if prev_node != None and prev_node.link != None and current_node.link != None and current_node.link.target == prev_node.link.target:
                self.link_target_at_cursor = current_node.link.target
            else:
                self.link_target_at_cursor = None

    def update_tags_at_cursor(self):
        if self.document == None:
            self.set_tags_at_cursor(set())
        else:
            node = self.document.ast.get_node_at_position(self.document.ast.get_first_cursor_pos())
            node = node.prev_in_parent()
            if node == None:
                self.set_tags_at_cursor(set())
            else:
                self.set_tags_at_cursor(node.tags.copy())

    def set_tags_at_cursor(self, tags):
        self.tags_at_cursor = tags
        self.update_tag_toggle(self.main_window.toolbar.bold_button, 'bold')
        self.update_tag_toggle(self.main_window.toolbar.italic_button, 'italic')

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
            if tagname in self.tags_at_cursor:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')


