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
from lemma.document_repo.document_repo import DocumentRepo
from lemma.history.history import History
from lemma.message_bus.message_bus import MessageBus
from lemma.ui.title_widget.title_widget import TitleWidget
from lemma.ui.helpers.observable import Observable
import lemma.infrastructure.timer as timer


class DocumentView(Observable):

    def __init__(self, main_window, application):
        Observable.__init__(self)
        self.main_window = main_window
        self.view = main_window.document_view
        self.use_cases = application.use_cases

        self.cursor_x, self.cursor_y = None, None
        self.keyboard_modifiers_state = 0
        self.scrolling_multiplier = 2.5
        self.selected_link_target = None
        self.link_target_at_cursor = None
        self.link_target_at_pointer = None
        self.last_cursor_or_scrolling_change = time.time()

        self.document = None

        self.controller = DocumentViewController(self, self.use_cases)
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
        MessageBus.connect('history_changed', self.on_history_changed)
        MessageBus.connect('document_changed', self.on_document_change)
        MessageBus.connect('mode_set', self.on_mode_set)

        self.add_change_code('changed')

    def on_history_changed(self):
        self.set_document(History.get_active_document())
        self.update()

    def on_document_change(self):
        self.update_link_at_cursor()
        self.update()

    def on_mode_set(self):
        self.update()

    @timer.timer
    def update(self):
        active_document = History.get_active_document()
        has_active_doc = active_document != None
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
        self.last_cursor_or_scrolling_change = time.time()
        self.use_cases.app_state_set_value('document_view_width', width)
        self.use_cases.app_state_set_value('document_view_height', height)
        offset_x = self.view.adjustment_x.get_value()
        offset_y = self.view.adjustment_y.get_value()
        self.use_cases.scroll_to_xy(offset_x, offset_y)
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
        self.document = document
        self.update_link_at_cursor()
        self.view.content.queue_draw()
        self.stop_renaming()
        self.title_widget.set_document(document)
        self.view.content.grab_focus()

    def init_renaming(self):
        if self.document != None:
            self.title_widget.activate()
            self.presenter.scroll_to_position([0, 0])
            self.title_widget.view.set_visible(True)
            self.use_cases.app_state_set_value('title_buttons_height', 50)
            self.view.content.queue_draw()
            self.title_widget.grab_focus()

    def stop_renaming(self):
        self.title_widget.deactivate()
        self.title_widget.view.set_visible(False)
        self.use_cases.app_state_set_value('title_buttons_height', 0)
        self.view.content.grab_focus()

    def on_entry_activate(self, entry=None):
        if self.title_widget.validation_state:
            self.submit()

    def on_submit_button_clicked(self, widget=None):
        if self.title_widget.validation_state:
            self.submit()

    def submit(self):
        self.use_cases.set_title(self.title_widget.title)
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
            if prev_node != None and prev_node.link != None and current_node.link != None and current_node.link.target == prev_node.link.target:
                self.link_target_at_cursor = current_node.link.target

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


