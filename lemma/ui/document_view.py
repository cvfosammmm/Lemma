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

from lemma.services.settings import Settings
from lemma.ui.document_view_controller import DocumentViewController
from lemma.ui.document_view_presenter import DocumentViewPresenter
from lemma.document_repo.document_repo import DocumentRepo
from lemma.history.history import History
from lemma.use_cases.use_cases import UseCases
from lemma.ui.title_widget import TitleWidget
from lemma.application_state.application_state import ApplicationState
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class DocumentView():

    def __init__(self, main_window, model_state):
        self.main_window = main_window
        self.view = main_window.document_view
        self.model_state = model_state

        self.cursor_x, self.cursor_y = None, None
        self.ctrl_pressed = False
        self.scrolling_multiplier = 2.5
        self.selected_link_target = None
        self.link_target_at_cursor = None
        self.link_target_at_pointer = None
        self.last_cursor_or_scrolling_change = time.time()

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

        self.set_document(History.get_active_document())
        self.presenter.update()

    @timer.timer
    def update(self):
        self.set_document(History.get_active_document())

        self.view.context_menu.open_link_button.set_visible(self.model_state.open_link_active)
        self.view.context_menu.open_link_separator.set_visible(self.model_state.open_link_active)
        self.view.context_menu.copy_link_button.set_visible(self.model_state.copy_link_active)
        self.view.context_menu.remove_link_button.set_visible(self.model_state.remove_link_active)
        self.view.context_menu.edit_link_button.set_visible(self.model_state.edit_link_active)
        self.view.context_menu.link_buttons_separator.set_visible(self.model_state.remove_link_active or self.model_state.edit_link_active)
        hide_back_and_forward = self.model_state.remove_link_active or self.model_state.edit_link_active or self.model_state.open_link_active
        self.view.context_menu.back_button.set_visible(not hide_back_and_forward)
        self.view.context_menu.forward_button.set_visible(not hide_back_and_forward)
        self.view.context_menu.back_forward_separator.set_visible(not hide_back_and_forward)

        self.update_link_at_cursor()
        self.presenter.update()

    def set_size(self, width, height):
        UseCases.app_state_set_values({'document_view_width': width, 'document_view_height': height})
        offset_x = self.view.adjustment_x.get_value()
        offset_y = self.view.adjustment_y.get_value()
        UseCases.scroll_to_xy(offset_x, offset_y)
        self.presenter.update()

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.last_cursor_or_scrolling_change = time.time()

            document = History.get_active_document()
            if document == None: return

            x = document.clipping.offset_x + (self.cursor_x if self.cursor_x != None else 0)
            y = document.clipping.offset_y + (self.cursor_y if self.cursor_y != None else 0)
            x -= ApplicationState.get_value('document_padding_left')
            y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')
            link = None

            if y > 0:
                leaf_box = document.get_leaf_at_xy(x, y)
                if leaf_box != None and leaf_box['node'] != None and leaf_box['node'].link != None:
                    link = leaf_box['node'].link

            self.set_link_target_at_pointer(link)
            self.presenter.update_pointer()

    def set_ctrl_pressed(self, is_pressed):
        if is_pressed != self.ctrl_pressed:
            self.ctrl_pressed = is_pressed
            self.last_cursor_or_scrolling_change = time.time()
            self.presenter.update()

    def set_document(self, document):
        if document != self.document:
            self.document = document
            self.view.content.queue_draw()
            self.stop_renaming()
            self.title_widget.set_document(document)
            self.view.content.grab_focus()

    def init_renaming(self):
        if self.document != None:
            self.title_widget.activate()
            self.presenter.scroll_to_position([0, 0])
            self.title_widget.view.set_visible(True)
            UseCases.app_state_set_value('title_buttons_height', 50)
            self.view.content.queue_draw()
            self.title_widget.grab_focus()

    def stop_renaming(self):
        self.title_widget.deactivate()
        self.title_widget.view.set_visible(False)
        UseCases.app_state_set_value('title_buttons_height', 0)
        self.view.content.grab_focus()

    def on_entry_activate(self, entry=None):
        if self.title_widget.validation_state:
            self.submit()

    def on_submit_button_clicked(self, widget=None):
        if self.title_widget.validation_state:
            self.submit()

    def submit(self):
        document = History.get_active_document()
        prev_title = document.title

        UseCases.set_title(self.title_widget.title)

        if Settings.get_value('update_backlinks'):
            backlinks = DocumentRepo.list_by_link_target(prev_title)
            for document_id in reversed(backlinks):
                linking_doc = DocumentRepo.get_by_id(document_id)
                links = linking_doc.ast.get_link_bounds_and_targets()
                for link in links:
                    bounds, target = link
                    if target == prev_title:
                        pos_1, pos_2 = bounds[0].get_position(), bounds[1].get_position()
                        char_nodes = [node.value for node in linking_doc.ast.get_subtree(pos_1, pos_2) if node.type == 'char']
                        if ''.join(char_nodes) == target:
                            xml = '<char link_target="' + xml_helpers.escape(self.title_widget.title) + '">' + xml_helpers.escape(self.title_widget.title) + '</char>'
                            UseCases.replace_section(linking_doc, bounds[0], bounds[1], xml)
                        else:
                            UseCases.set_link(linking_doc, bounds, self.title_widget.title)

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
        self.link_target_at_cursor = None
        if self.document != None and not self.document.cursor.has_selection():
            current_node = self.document.cursor.get_insert_node()
            prev_node = current_node.prev_in_parent()
            if prev_node != None and current_node.link == prev_node.link:
                self.link_target_at_cursor = current_node.link

        self.update_link_overlay_text()

    def set_link_target_at_pointer(self, link):
        self.link_target_at_pointer = link
        self.update_link_overlay_text()

    def update_link_overlay_text(self):
        if self.link_target_at_pointer != None:
            text = self.link_target_at_pointer
        else:
            text = self.link_target_at_cursor

        if text != None:
            if not urlparse(text).scheme in ['http', 'https']:
                target_document = DocumentRepo.get_by_title(text)
                if target_document == None:
                    text = 'Create "' + text + '"'

            self.view.link_overlay.set_text(text)
            self.view.link_overlay.set_visible(True)
        else:
            self.view.link_overlay.set_visible(False)


