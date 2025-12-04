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

from lemma.services.message_bus import MessageBus
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.settings import Settings
from lemma.services.autocomplete_db import AutocompleteDB
from lemma.application_state.application_state import ApplicationState
from lemma.services.layout_info import LayoutInfo
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class Autocomplete():

    def __init__(self, main_window, application):
        self.document_view = main_window.document_view
        self.view = main_window.document_view.autocomplete_view
        self.application = application

        self.scrolling_position_x, self.scrolling_position_y = -1, -1

        self.is_active = False
        self.position_on_screen = False
        self.command_at_cursor = ''
        self.command_at_cursor_first_node = None
        self.session_first_node = None
        self.suggestions = []

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.document_view.content.add_controller(key_controller)
        self.view.listbox.connect('row-activated', self.on_row_activated)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect('enter', self.on_focus_in)
        focus_controller.connect('leave', self.on_focus_out)
        self.document_view.content.add_controller(focus_controller)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'keyboard_input')

    @timer.timer
    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            self.deactivate()
            return

        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages:
            self.on_history_changed()
        if 'document_changed' in messages:
            self.on_document_changed()
        if 'keyboard_input' in messages:
            self.on_keyboard_input()

        scrolling_position_x, scrolling_position_y = document.get_current_scrolling_offsets()
        if scrolling_position_x != self.scrolling_position_x or scrolling_position_y != self.scrolling_position_y:
            self.scrolling_position_x = scrolling_position_x
            self.scrolling_position_y = scrolling_position_y
            self.update()

    def on_keyboard_input(self):
        self.update_command_at_cursor()
        if not self.is_active:
            self.activate_if_possible()
        self.update()

    def on_document_changed(self):
        self.update_command_at_cursor()
        self.update()

    def on_history_changed(self):
        self.update_command_at_cursor()
        self.update()

    def on_keypress(self, controller, keyval, keycode, state):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None:
            self.deactivate()
            return

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval in [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]:
            if state & modifiers == 0:
                if self.is_active:
                    return True
                else:
                    self.update_command_at_cursor()
                    self.activate_if_possible()
                    self.update()
                    if self.is_active:
                        return True

        elif (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Return')):
            if self.is_active:
                self.submit()
                self.update()
                return True

        elif (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Escape')):
            if self.is_active:
                self.deactivate()
                self.update()
                return True

        elif (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Down')):
            if self.is_active:
                self.view.select_next()
                return True

        elif (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Up')):
            if self.is_active:
                self.view.select_prev()
                return True

        return False

    def on_row_activated(self, listbox, row):
        self.submit()
        self.update()

    def on_focus_out(self, controller):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None:
            self.deactivate()
            return

        self.view.focus_hide = True
        self.update()

    def on_focus_in(self, controller):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None:
            self.deactivate()
            return

        self.view.focus_hide = False
        self.update()

    def update(self):
        if self.is_active:
            self.deactivate_if_necessary()
            self.update_suggestions()

        self.view.set_visible(self.is_active)
        self.update_position()
        self.view.set_visible(self.is_active and self.position_on_screen and not self.view.focus_hide)
        self.view.queue_draw()

    def update_position(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.cursor.get_insert_node()
        insert_x, insert_y = document.get_absolute_xy(insert.layout)
        content_offset = LayoutInfo.get_normal_document_offset()
        scrolling_offset_y = document.get_current_scrolling_offsets()[1]
        insert_y += content_offset - scrolling_offset_y
        insert_height = insert.layout['height']
        insert_x += LayoutInfo.get_document_padding_left()
        window_height = ApplicationState.get_value('document_view_height')
        window_width = ApplicationState.get_value('document_view_width')

        self.view.x = min(insert_x, window_width - self.view.width - 18)
        if insert_y + insert_height + self.view.max_height > window_height:
            self.view.y = insert_y - self.view.height
            self.position_on_screen = (self.view.y + self.view.height - self.view.max_height >= 0 and self.view.y + self.view.height + insert_height <= window_height)
        else:
            self.view.y = insert_y + insert_height
            self.position_on_screen = (self.view.y - insert_height >= 0 and self.view.y + self.view.max_height <= window_height)

        self.view.set_margin_top(self.view.y)
        self.view.set_margin_start(self.view.x)

    def update_command_at_cursor(self):
        # Tries to match a backslash followed by letters from the
        # last backslash before the cursor to the cursor.

        document = WorkspaceRepo.get_workspace().get_active_document()
        node = document.cursor.get_insert_node()
        command_at_cursor = ''
        first_command_node = None
        while True:
            node = node.prev_in_parent()
            if node == None:
                break
            elif node.type == 'char' and node.value.isalpha():
                command_at_cursor = node.value + command_at_cursor
            elif node.type == 'char' and node.value == '\\':
                command_at_cursor = node.value + command_at_cursor
                first_command_node = node
                break
            else:
                break

        if first_command_node != None:
            self.command_at_cursor = command_at_cursor
            self.command_at_cursor_first_node = first_command_node
        else:
            self.command_at_cursor = ''
            self.command_at_cursor_first_node = None

    def activate_if_possible(self):
        # No activation if autocomplete is disabled.
        if not Settings.get_value('stylized_latex_autocomplete'): return

        # Triggered on tab, if ac is inactive,
        # also when nodes are inserted in the document ast.

        if len(self.command_at_cursor) >= 2:
            self.is_active = True
            self.session_first_node = self.command_at_cursor_first_node

    def deactivate_if_necessary(self):
        # Deactivates autocomplete if certain invariants don't hold
        # The cursor must be on the same paragraph as the starting point
        # and it must come after it on that paragraph, ...

        if not Settings.get_value('stylized_latex_autocomplete'):
            self.deactivate()

        if self.session_first_node != self.command_at_cursor_first_node:
            self.deactivate()

    def deactivate(self):
        self.is_active = False
        self.session_first_node = None
        self.suggestions = []

    def update_suggestions(self):
        # Placeholders are not considered as such, so matching is literal.
        # If there are not at least 2 matching commands, the activation is
        # reversed.

        if not self.is_active: return

        self.suggestions = AutocompleteDB.get_suggestions(self.command_at_cursor[1:], limit=20)

        if len(self.suggestions) > 0:
            self.view.set_items(self.suggestions)
        else:
            self.deactivate()

    def submit(self):
        # Get item that matches the current command at cursor.
        # Add it to the buffer.

        if len(self.suggestions) == 0: return

        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.cursor.get_insert_node()
        xml = AutocompleteDB.get_xml(self.view.listbox.get_selected_row().title[1:])
        UseCases.replace_section(document, self.session_first_node, insert, xml)
        UseCases.scroll_insert_on_screen(animation_type='default')

        self.deactivate()


