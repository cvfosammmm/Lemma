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
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
from lemma.application_state.application_state import ApplicationState
from lemma.services.layout_info import LayoutInfo
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class DocumentView():

    def __init__(self, main_window, application):
        self.main_window = main_window
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
        self.last_cache_reset = time.time()

        self.view = main_window.document_view
        self.controller = DocumentViewController(self)
        self.presenter = DocumentViewPresenter(self)

    @timer.timer
    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        new_active_document = document != self.document
        if new_active_document:
            self.document = document
            if document != None:
                self.view.content.grab_focus()

        if self.document == None:
            self.scrolling_position_x, self.scrolling_position_y = -1, -1
            return True

        document_changed = max(document.last_cursor_movement, document.last_modified) > self.last_cache_reset
        do_draw = False

        if self.document != None:
            if new_active_document or document_changed:
                self.presenter.render_cache = dict()
                self.last_cache_reset = time.time()
                self.reset_cursor_blink()

                self.update_link_at_cursor()

                do_draw = True

        scrolling_position_x, scrolling_position_y = self.document.get_current_scrolling_offsets()

        time_since_blink_start = time.time() - self.cursor_blink_reset
        time_in_cycle = (time_since_blink_start % self.cursor_blink_time) / self.cursor_blink_time

        cursor_visible = True
        if time_since_blink_start <= 10 and time_in_cycle > 0.6:
            cursor_visible = False
        if ApplicationState.get_value('document_view_hide_cursor_on_unfocus') and not self.view.content.has_focus():
            cursor_visible = False
        if self.document.cursor.has_selection():
            cursor_visible = False

        if time_since_blink_start <= self.cursor_blink_timeout and cursor_visible != self.cursor_visible:
            self.cursor_visible = cursor_visible
            do_draw = True

        if scrolling_position_x != self.scrolling_position_x or scrolling_position_y != self.scrolling_position_y:
            self.scrolling_position_x = scrolling_position_x
            self.scrolling_position_y = scrolling_position_y
            do_draw = True

        if do_draw:
            self.update_pointer()
            self.view.content.queue_draw()

    def reset_cursor_blink(self):
        self.cursor_blink_reset = time.time()

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.last_cursor_or_scrolling_change = time.time()

            document = WorkspaceRepo.get_workspace().get_active_document()
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
            self.update_pointer()

    def set_ctrl_pressed(self, is_pressed):
        if is_pressed != self.ctrl_pressed:
            self.ctrl_pressed = is_pressed
            self.last_cursor_or_scrolling_change = time.time()
            self.update_pointer()

    def update_pointer(self):
        if self.document == None: return

        document = self.document
        if document == None:
            self.view.content.set_cursor_from_name('default')
            return

        x = self.scrolling_position_x + (self.cursor_x if self.cursor_x != None else 0)
        y = self.scrolling_position_y + (self.cursor_y if self.cursor_y != None else 0)
        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()
        y -= ApplicationState.get_value('title_buttons_height')

        if y > 0:
            leaf_box = document.get_leaf_at_xy(x, y)
            if leaf_box != None:
                node = leaf_box['node']
                if node != None:
                    if node.link != None and not self.ctrl_pressed:
                        self.view.content.set_cursor_from_name('pointer')
                    elif node.type == 'widget':
                        self.view.content.set_cursor_from_name(node.value.get_cursor_name())
                    elif node.type == 'placeholder':
                        self.view.content.set_cursor_from_name('default')
                    else:
                        self.view.content.set_cursor_from_name('text')
                else:
                    self.view.content.set_cursor_from_name('text')
            else:
                self.view.content.set_cursor_from_name('text')
        else:
            self.view.content.set_cursor_from_name('default')

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


