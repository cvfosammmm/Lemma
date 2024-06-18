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

import datetime

from lemma.document.document import Document


class DocumentDraft():

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.view = main_window.draft_view
        self.document = None

        self.title = ''
        self.title_changed = False
        self.validation_state = False
        self.is_active = False

        self.view.title_entry.connect('changed', self.on_entry_changed)
        self.view.title_entry.connect('activate', self.on_entry_activate)
        self.view.submit_button.connect('clicked', self.on_submit_button_clicked)
        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)

        self.key_controller_window = Gtk.EventControllerKey()
        self.key_controller_window.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_window.connect('key-pressed', self.on_entry_keypress)
        self.view.title_entry.add_controller(self.key_controller_window)

        self.workspace.connect('mode_set', self.on_mode_set)
        self.update()

    def on_mode_set(self, workspace): self.update()

    def update(self):
        if self.workspace.mode == 'draft':
            self.init()
        else:
            self.deactivate()

    def on_entry_changed(self, entry):
        if self.is_active:
            self.set_title(entry.get_text())

    def set_title(self, title):
        if title != self.title:
            self.title = title
            self.title_changed = True
            self.validate()

    def validate(self):
        if self.document == None: return

        validation_state = True
        if self.title == '':
            validation_state = False
        elif self.title != self.document.title and self.workspace.get_by_title(self.title):
            validation_state = False

        if self.title != self.document.title and self.title == '':
            self.view.subtext.set_text('Name cannot be empty.')
            self.view.subtext.add_css_class('error')
            self.view.title_entry.add_css_class('error')
        elif self.title != self.document.title and self.workspace.get_by_title(self.title):
            self.view.subtext.set_text('A document with this name already exists.')
            self.view.subtext.add_css_class('error')
            self.view.title_entry.add_css_class('error')
        else:
            self.view.subtext.set_text('Please enter a name for this document.')
            self.view.subtext.remove_css_class('error')
            self.view.title_entry.remove_css_class('error')

        if validation_state != self.validation_state:
            self.validation_state = validation_state
        self.view.submit_button.set_sensitive(validation_state)

    def grab_focus(self):
        self.view.title_entry.grab_focus()
        self.view.title_entry.set_position(len(self.title))

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.reset_title()
            self.validate()
            self.view.button_revealer.set_reveal_child(True)

    def deactivate(self):
        self.is_active = False
        self.view.title_entry.set_position(0)
        self.view.button_revealer.set_reveal_child(False)
        self.set_subtext_to_last_modified_date()

    def reset_title(self):
        if self.document == None:
            self.view.title_entry.set_enable_undo(False)
            self.view.title_entry.set_text('')
            self.view.title_entry.set_enable_undo(True)
            self.title_changed = False
        else:
            self.view.title_entry.set_enable_undo(False)
            self.view.title_entry.set_text(self.document.title)
            self.view.title_entry.set_enable_undo(True)
            self.title_changed = False

    def set_subtext_to_last_modified_date(self):
        if self.document == None:
            self.view.subtext.set_text('')
        else:
            datetime_last_modified = datetime.datetime.fromtimestamp(self.document.last_modified)
            self.view.subtext.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))
        self.view.subtext.remove_css_class('error')

    def on_entry_activate(self, entry=None):
        if self.validation_state:
            self.submit()

    def on_submit_button_clicked(self, widget=None):
        if self.validation_state:
            self.submit()

    def submit(self):
        self.document.title = self.title
        self.deactivate()
        self.workspace.add(self.document)
        self.workspace.set_active_document(self.document)
        self.document = None

    def on_entry_keypress(self, controller, keyval, keycode, state):
        if keyval == Gdk.keyval_from_name('Escape'):
            if state & Gtk.accelerator_get_default_mod_mask() == 0:
                self.workspace.leave_draft_mode()
                return True
        return False

    def on_cancel_button_clicked(self, widget=None):
        self.workspace.leave_draft_mode()

    def init(self):
        id = self.workspace.get_new_document_id()
        self.document = Document(id)
        self.reset_title()
        self.grab_focus()
        self.activate()
        self.validate()

    def reset_title(self):
        self.title = ''
        self.view.title_entry.set_enable_undo(False)
        self.view.title_entry.set_text('')
        self.view.title_entry.set_enable_undo(True)
        self.title_changed = False


