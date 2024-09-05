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

import time
from urllib.parse import urlparse

from lemma.ui.document_view.document_view_controller import DocumentViewController
from lemma.ui.document_view.document_view_presenter import DocumentViewPresenter
from lemma.ui.title_widget.title_widget import TitleWidget
from lemma.helpers.observable import Observable


class DocumentView(Observable):

    def __init__(self, workspace, main_window):
        Observable.__init__(self)
        self.main_window = main_window
        self.view = main_window.document_view

        self.width, self.height = 0, 0
        self.cursor_x, self.cursor_y = None, None
        self.keyboard_modifiers_state = 0
        self.scrolling_multiplier = 2.5
        self.selected_link_target = None
        self.link_target_at_cursor = None
        self.link_target_at_pointer = None
        self.tags_at_cursor = set()
        self.paragraph_style_at_cursor = 'p'
        self.last_cursor_or_scrolling_change = time.time()

        self.workspace = workspace
        self.document = None

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

        self.set_document(workspace.get_active_document())
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('document_changed', self.on_document_change)
        self.workspace.connect('mode_set', self.on_mode_set)

        self.add_change_code('changed')

    def on_new_active_document(self, workspace, document=None):
        self.set_document(document)
        self.update()

    def on_document_change(self, workspace, document): self.update()
    def on_mode_set(self, workspace): self.update()

    def update(self):
        active_document = self.workspace.active_document
        has_active_doc = (self.workspace.mode == 'documents' and active_document != None)
        has_selection = has_active_doc and active_document.cursor.has_selection()
        links_inside_selection = has_active_doc and len([node for node in active_document.ast.get_subtree(*active_document.cursor.get_state()) if node.link != None]) > 0
        cursor_inside_link = has_active_doc and active_document.cursor.get_insert_node().is_inside_link()
        delete_link_visible = has_active_doc and (links_inside_selection or ((not has_selection) and cursor_inside_link))
        edit_link_visible = has_active_doc and ((not has_selection) and cursor_inside_link)

        self.view.context_menu.remove_link_button.set_visible(delete_link_visible)
        self.view.context_menu.edit_link_button.set_visible(edit_link_visible)
        self.view.context_menu.link_buttons_separator.set_visible(delete_link_visible or edit_link_visible)

        self.add_change_code('changed')

    def set_size(self, width, height):
        self.width, self.height = width, height
        self.last_cursor_or_scrolling_change = time.time()
        self.add_change_code('changed')

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.last_cursor_or_scrolling_change = time.time()
            self.add_change_code('changed')

    def set_keyboard_modifiers_state(self, state):
        if state != self.keyboard_modifiers_state:
            self.keyboard_modifiers_state = state
            self.last_cursor_or_scrolling_change = time.time()
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
        self.update_paragraph_style_at_cursor()
        self.add_change_code('changed')

    def init_renaming(self):
        if self.document != None:
            self.title_widget.activate()
            self.presenter.scroll_to_position([0, 0])
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
            current_node = self.document.ast.root.get_node_at_position(self.document.cursor.get_first_cursor_pos())
            prev_node = current_node.prev_in_parent()
            if prev_node != None and prev_node.link != None and current_node.link != None and current_node.link.target == prev_node.link.target:
                self.link_target_at_cursor = current_node.link.target
            else:
                self.link_target_at_cursor = None
        self.update_link_overlay_text()

    def update_tags_at_cursor(self):
        if self.document == None:
            self.set_tags_at_cursor(set())
        else:
            node = self.document.ast.root.get_node_at_position(self.document.cursor.get_first_cursor_pos())
            node = node.prev_in_parent()
            if node == None:
                self.set_tags_at_cursor(set())
            else:
                self.set_tags_at_cursor(node.tags.copy())

    def update_paragraph_style_at_cursor(self):
        if self.document == None:
            self.paragraph_style_at_cursor = 'p'
        else:
            current_node = self.document.ast.root.get_node_at_position(self.document.cursor.get_first_cursor_pos())
            self.paragraph_style_at_cursor = current_node.paragraph_style
        self.update_paragraph_style_button()

    def set_tags_at_cursor(self, tags):
        self.tags_at_cursor = tags
        self.update_tag_toggle(self.main_window.toolbar.bold_button, 'bold')
        self.update_tag_toggle(self.main_window.toolbar.italic_button, 'italic')

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

    def set_link_target_at_pointer(self, link):
        self.link_target_at_pointer = link
        self.update_link_overlay_text()

    def update_paragraph_style_button(self):
        labels_dict = {'p': _('Paragraph'), 'h2': _('Heading 2'), 'h3': _('Heading 3'), 'h4': _('Heading 4'), 'h5': _('Heading 5'), 'h6': _('Heading 6')}

        self.main_window.toolbar.paragraph_style_menu_button_label.set_text(labels_dict[self.paragraph_style_at_cursor])

    def update_link_overlay_text(self):
        if self.link_target_at_pointer != None:
            text = self.link_target_at_pointer
        else:
            text = self.link_target_at_cursor

        if text != None:
            if not urlparse(text).scheme in ['http', 'https']:
                target_document = self.workspace.get_by_title(text)
                if target_document == None:
                    text = 'Create "' + text + '"'

            self.view.link_overlay.set_text(text)
            self.view.link_overlay.set_visible(True)
        else:
            self.view.link_overlay.set_visible(False)


