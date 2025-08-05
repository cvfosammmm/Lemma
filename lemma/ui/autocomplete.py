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

from lemma.message_bus.message_bus import MessageBus
from lemma.history.history import History
from lemma.settings.settings import Settings
from lemma.db.autocomplete_db import AutocompleteDB
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases


class Autocomplete():

    def __init__(self, main_window):
        self.main_window = main_window
        self.widget = AutocompleteWidget()
        self.main_window.document_view.add_overlay(self.widget)

        self.is_active = False
        self.command_at_cursor = ''
        self.command_at_cursor_first_node = None
        self.session_first_node = None
        self.suggestions = []

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.main_window.document_view.content.add_controller(key_controller)
        self.widget.listbox.connect('row-activated', self.on_row_activated)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect('enter', self.on_focus_in)
        focus_controller.connect('leave', self.on_focus_out)
        self.main_window.document_view.content.add_controller(focus_controller)

        MessageBus.connect('history_changed', self.on_history_changed)
        MessageBus.connect('document_changed', self.on_document_changed)
        MessageBus.connect('keyboard_input', self.on_keyboard_input)

    def on_keyboard_input(self):
        document = History.get_active_document()
        if document == None:
            self.deactivate()
            return

        self.update_command_at_cursor()
        if not self.is_active:
            self.activate_if_possible()
        self.update()

    def on_document_changed(self):
        document = History.get_active_document()
        if document == None:
            self.deactivate()
            return

        self.update_command_at_cursor()
        self.update()

    def on_history_changed(self):
        document = History.get_active_document()
        if document == None:
            self.deactivate()
            return

        self.update_command_at_cursor()
        self.update()

    def on_keypress(self, controller, keyval, keycode, state):
        document = History.get_active_document()
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
                self.widget.select_next()
                return True

        elif (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Up')):
            if self.is_active:
                self.widget.select_prev()
                return True

        return False

    def on_row_activated(self, listbox, row):
        self.submit()
        self.update()

    def on_focus_out(self, controller):
        document = History.get_active_document()
        if document == None:
            self.deactivate()
            return

        self.widget.focus_hide = True
        self.update()

    def on_focus_in(self, controller):
        document = History.get_active_document()
        if document == None:
            self.deactivate()
            return

        self.widget.focus_hide = False
        self.update()

    def update(self):
        if self.is_active:
            self.deactivate_if_necessary()
            self.update_suggestions()

        self.widget.set_visible(self.is_active)
        self.widget.update_position()
        self.widget.set_visible(self.is_active and self.widget.position_is_visible() and not self.widget.focus_hide)
        self.widget.queue_draw()

    def update_command_at_cursor(self):
        # Tries to match a backslash followed by letters from the
        # last backslash before the cursor to the cursor.

        document = History.get_active_document()
        node = document.cursor.get_insert_node()
        command_at_cursor = ''
        first_command_node = None
        while True:
            node = node.prev_in_parent()
            if node == None:
                break
            elif node.is_char() and node.value.isalpha():
                command_at_cursor = node.value + command_at_cursor
            elif node.is_char() and node.value == '\\':
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
        # The cursor must be on the same line as the starting point
        # and it must come after it on that line, ...

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
            self.widget.set_items(self.suggestions)
        else:
            self.deactivate()

    def submit(self):
        # Get item that matches the current command at cursor.
        # Add it to the buffer.

        if len(self.suggestions) == 0: return

        document = History.get_active_document()
        insert = document.cursor.get_insert_node()
        xml = AutocompleteDB.get_xml(self.widget.listbox.get_selected_row().title[1:])
        UseCases.replace_section(document, self.session_first_node, insert, xml)

        self.deactivate()


class AutocompleteWidget(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.add_css_class('autocomplete')

        self.width = 300
        self.height = 0
        self.x = 0
        self.y = 0
        self.line_height = 35
        self.max_height = 5 * self.line_height + 2
        self.position_on_screen = False
        self.focus_hide = True
        self.set_size_request(self.width, self.height)
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)

        self.listbox = Gtk.ListBox()
        self.listbox.set_activate_on_single_click(True)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_can_focus(False)

        self.listbox.connect('selected-rows-changed', self.on_selected_rows_changed)

        self.set_child(self.listbox)

    def set_items(self, items):
        self.listbox.remove_all()
        for item in items:
            self.listbox.append(ACItem('\\' + item))
        self.listbox.select_row(self.listbox.get_first_child())

        self.height = min(len(items), 5) * self.line_height + 2
        self.width = 300
        self.set_size_request(self.width, self.height)

    def select_next(self):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row == listbox.get_last_child():
            listbox.select_row(listbox.get_first_child())
        else:
            listbox.select_row(listbox.get_row_at_index(selected_row.get_index() + 1))

    def select_prev(self):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row == listbox.get_first_child():
            listbox.select_row(listbox.get_last_child())
        else:
            listbox.select_row(listbox.get_row_at_index(selected_row.get_index() - 1))

    def on_selected_rows_changed(self, listbox):
        selected_row = self.listbox.get_selected_row()
        adjustment = self.get_vadjustment()

        if selected_row == None:
            adjustment.set_value(0)
        else:
            bounds = selected_row.compute_bounds(self.listbox).out_bounds
            item_height = bounds.size.height
            y = bounds.origin.y
            page_size = adjustment.get_page_size()
            offset = adjustment.get_value()
            if offset > y:
                adjustment.set_value(y)
            if offset < y + item_height - page_size:
                adjustment.set_value(y + item_height - page_size)

    def update_position(self):
        document = History.get_active_document()
        insert = document.cursor.get_insert_node()
        insert_x, insert_y = document.get_absolute_xy(insert.layout)
        content_offset = ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')
        scrolling_offset_y = document.clipping.offset_y
        insert_y += content_offset - scrolling_offset_y
        insert_height = insert.layout['height']
        insert_x += ApplicationState.get_value('document_padding_left')
        window_height = ApplicationState.get_value('document_view_height')
        window_width = ApplicationState.get_value('document_view_width')

        self.x = min(insert_x, window_width - self.width - 18)
        if insert_y + insert_height + self.max_height > window_height:
            self.y = insert_y - self.height
            self.position_on_screen = (self.y + self.height - self.max_height >= 0 and self.y + self.height + insert_height <= window_height)
        else:
            self.y = insert_y + insert_height
            self.position_on_screen = (self.y - insert_height >= 0 and self.y + self.max_height <= window_height)

        self.set_margin_top(self.y)
        self.set_margin_start(self.x)

    def position_is_visible(self):
        return self.position_on_screen


class ACItem(Gtk.ListBoxRow):

    def __init__(self, title):
        Gtk.ListBoxRow.__init__(self)
        self.set_size_request(-1, 30)

        self.title = title

        label = Gtk.Label.new(self.title)
        label.set_xalign(Gtk.Align.FILL)
        self.set_child(label)


