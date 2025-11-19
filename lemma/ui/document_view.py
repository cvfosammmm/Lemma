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

import time, math
from urllib.parse import urlparse

from lemma.services.settings import Settings
from lemma.ui.document_view_controller import DocumentViewController
from lemma.ui.document_view_presenter import DocumentViewPresenter
from lemma.ui.document_view_view import DocumentViewDrawingArea
from lemma.ui.document_view_view import TitleWidget
from lemma.document_repo.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
from lemma.services.layout_info import LayoutInfo
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class DocumentView():

    def __init__(self, main_window, model_state, application):
        self.main_window = main_window
        self.model_state = model_state
        self.application = application

        self.cursor_x, self.cursor_y = None, None
        self.scrolling_position_x, self.scrolling_position_y = -1, -1
        self.ctrl_pressed = False
        self.scrolling_multiplier = 2.5
        self.selected_link_target = None
        self.link_target_at_cursor = None
        self.link_target_at_pointer = None
        self.last_cursor_or_scrolling_change = time.time()

        self.cursor_blink_time = Gtk.Settings.get_default().get_property('gtk_cursor_blink_time') / 1000
        self.cursor_blink_timeout = Gtk.Settings.get_default().get_property('gtk_cursor_blink_timeout')
        self.cursor_blink_reset = time.time()
        self.cursor_visible = True

        self.document = None

        self.view = main_window.document_view
        self.view.content = DocumentViewDrawingArea(self)
        self.view.set_child(self.view.content)
        self.controller = DocumentViewController(self)
        self.presenter = DocumentViewPresenter(self)

        self.title_widget_is_active = False
        self.title_widget = TitleWidget()
        self.title_widget.title_entry.connect('activate', self.on_entry_activate)
        self.title_widget.submit_button.connect('clicked', self.on_submit_button_clicked)
        self.title_widget.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.key_controller_window = Gtk.EventControllerKey()
        self.key_controller_window.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_window.connect('key-pressed', self.on_entry_keypress)
        self.title_widget.title_entry.add_controller(self.key_controller_window)
        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_title_entry_focus_in)
        self.title_widget.title_entry.add_controller(self.focus_controller)
        self.title_widget.title_entry.connect('changed', self.on_title_entry_changed)
        self.view.add_overlay(self.title_widget)

        self.set_document(DocumentRepo.get_active_document())
        self.presenter.update()

    @timer.timer
    def update(self):
        self.set_document(DocumentRepo.get_active_document())

        self.update_link_at_cursor()
        self.presenter.update()

        if self.document == None: return

        new_active_document = self.document != self.view.content.last_rendered_document
        document_changed = max(self.document.last_cursor_movement, self.document.last_modified) > self.view.content.last_cache_reset
        if new_active_document or document_changed:
            self.view.content.render_cache = dict()
            self.view.content.do_render_title = True
            self.view.content.last_rendered_document = self.document
            self.view.content.last_cache_reset = time.time()
            self.reset_cursor_blink()
        self.view.content.queue_draw()

    def animate(self):
        if self.document == None:
            self.scrolling_position_x, self.scrolling_position_y = -1, -1
            return True

        scrolling_position_x, scrolling_position_y = self.document.get_current_scrolling_offsets()

        time_since_blink_start = time.time() - self.cursor_blink_reset
        time_in_cycle = (time_since_blink_start % self.cursor_blink_time) / self.cursor_blink_time

        if time_since_blink_start <= 10 and time_in_cycle > 0.6:
            cursor_visible = False
        else:
            cursor_visible = True

        do_draw = False

        if time_since_blink_start <= self.cursor_blink_timeout and cursor_visible != self.cursor_visible:
            self.cursor_visible = cursor_visible
            do_draw = True

        if scrolling_position_x != self.scrolling_position_x or scrolling_position_y != self.scrolling_position_y:
            self.scrolling_position_x = scrolling_position_x
            self.scrolling_position_y = scrolling_position_y
            do_draw = True

        if do_draw:
            self.view.content.queue_draw()

    def reset_cursor_blink(self):
        self.cursor_blink_reset = time.time()

    def set_size(self, width, height):
        UseCases.app_state_set_values({'document_view_width': width, 'document_view_height': height})
        self.presenter.update()

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.last_cursor_or_scrolling_change = time.time()

            document = DocumentRepo.get_active_document()
            if document == None: return

            x = self.scrolling_position_x + (self.cursor_x if self.cursor_x != None else 0)
            y = self.scrolling_position_y + (self.cursor_y if self.cursor_y != None else 0)
            x -= LayoutInfo.get_document_padding_left()
            y -= LayoutInfo.get_normal_document_offset()
            link = None

            if y > 0:
                leaf_box = document.get_leaf_at_xy(x, y)
                if leaf_box != None and leaf_box['node'] != None and leaf_box['node'].link != None:
                    link = leaf_box['node'].link

            self.set_link_target_at_pointer(link)
            self.presenter.update()

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
            self.reset_title()
            self.view.content.grab_focus()

    def on_title_entry_focus_in(self, controller):
        if not self.title_widget_is_active:
            self.title_widget_is_active = True
            self.reset_title()
            self.validate_title()
            self.title_widget.button_revealer.set_reveal_child(True)

    def on_title_entry_changed(self, entry):
        if self.title_widget_is_active:
            self.validate_title()

    def on_entry_activate(self, entry=None):
        self.submit()

    def on_submit_button_clicked(self, widget=None):
        self.submit()

    def on_entry_keypress(self, controller, keyval, keycode, state):
        if keyval == Gdk.keyval_from_name('Escape'):
            if state & Gtk.accelerator_get_default_mod_mask() == 0:
                self.cancel()
                return True
        return False

    def on_cancel_button_clicked(self, widget=None):
        self.cancel()

    def init_renaming(self):
        if self.document != None:
            self.title_widget.set_visible(True)
            UseCases.app_state_set_value('title_buttons_height', 50)
            UseCases.scroll_to_xy(0, 0, animation_type=None)
            self.view.content.queue_draw()
            self.title_widget.title_entry.grab_focus()
            self.title_widget.title_entry.set_position(self.title_widget.title_entry.get_text_length())

    def validate_title(self):
        if self.document == None: return

        title = self.title_widget.title_entry.get_text()

        validation_state = True
        if title == '':
            validation_state = False
        elif title != self.document.title and len(DocumentRepo.list_by_title(title)) > 0:
            validation_state = False
        self.title_widget.submit_button.set_sensitive(validation_state)

        if title != self.document.title and title == '':
            self.title_widget.subtext.set_text('Name cannot be empty.')
            self.title_widget.subtext.add_css_class('error')
            self.title_widget.title_entry.add_css_class('error')
        elif title != self.document.title and len(DocumentRepo.list_by_title(title)) > 0:
            self.title_widget.subtext.set_text('A document with this name already exists.')
            self.title_widget.subtext.add_css_class('error')
            self.title_widget.title_entry.add_css_class('error')
        else:
            self.title_widget.subtext.set_text('Please enter a name for this document.')
            self.title_widget.subtext.remove_css_class('error')
            self.title_widget.title_entry.remove_css_class('error')

    def submit(self):
        if not self.title_widget.submit_button.get_sensitive(): return

        document = DocumentRepo.get_active_document()
        prev_title = document.title
        title = self.title_widget.title_entry.get_text()

        UseCases.set_title(title)

        if Settings.get_value('update_backlinks'):
            backlinks = DocumentRepo.list_by_link_target(prev_title)
            for document_stub in reversed(backlinks):
                linking_doc = DocumentRepo.get_by_id(document_stub['id'])
                links = linking_doc.ast.get_link_bounds_and_targets()
                for link in links:
                    bounds, target = link
                    if target == prev_title:
                        pos_1, pos_2 = bounds[0].get_position(), bounds[1].get_position()
                        char_nodes = [node.value for node in linking_doc.ast.get_subtree(pos_1, pos_2) if node.type == 'char']
                        if ''.join(char_nodes) == target:
                            xml = '<a href="' + xml_helpers.escape(title) + '">' + xml_helpers.escape(title) + '</a>'
                            UseCases.replace_section(linking_doc, bounds[0], bounds[1], xml)
                        else:
                            UseCases.set_link(linking_doc, bounds, title)

        self.stop_renaming()

    def cancel(self):
        self.reset_title()
        self.stop_renaming()

    def reset_title(self):
        if self.document == None:
            self.title_widget.title_entry.set_enable_undo(False)
            self.title_widget.title_entry.set_text('')
            self.title_widget.title_entry.set_enable_undo(True)
        else:
            self.title_widget.title_entry.set_enable_undo(False)
            self.title_widget.title_entry.set_text(self.document.title)
            self.title_widget.title_entry.set_enable_undo(True)

    def stop_renaming(self):
        self.title_widget_is_active = False
        self.title_widget.button_revealer.set_reveal_child(False)
        self.title_widget.set_visible(False)
        UseCases.app_state_set_value('title_buttons_height', 0)
        self.view.content.grab_focus()

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
                if len(DocumentRepo.list_by_title(text)) == 0:
                    text = 'Create "' + text + '"'

            self.view.link_overlay.set_text(text)
            self.view.link_overlay.set_visible(True)
        else:
            self.view.link_overlay.set_visible(False)


