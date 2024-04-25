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

from lemma.document.document import Document


class DocumentDraft():

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.title_widget = main_window.draft_title_widget
        self.document = None

        self.title_widget.view.title_entry.connect('activate', self.on_entry_activate)
        self.title_widget.view.submit_button.connect('clicked', self.on_submit_button_clicked)
        self.title_widget.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)

        self.key_controller_window = Gtk.EventControllerKey()
        self.key_controller_window.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_window.connect('key-pressed', self.on_entry_keypress)
        self.title_widget.view.title_entry.add_controller(self.key_controller_window)

    def update(self):
        if self.workspace.mode == 'draft':
            self.init()
        else:
            self.title_widget.deactivate()

    def on_entry_activate(self, entry=None):
        if self.title_widget.validation_state:
            self.submit()

    def on_submit_button_clicked(self, widget=None):
        if self.title_widget.validation_state:
            self.submit()

    def submit(self):
        self.document.title = self.title_widget.title
        self.title_widget.deactivate()
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
        self.title_widget.document = self.document
        self.reset_title()
        self.title_widget.grab_focus()
        self.title_widget.activate()
        self.title_widget.validate()

    def reset_title(self):
        self.title_widget.title = ''
        self.title_widget.view.title_entry.set_enable_undo(False)
        self.title_widget.view.title_entry.set_text('')
        self.title_widget.view.title_entry.set_enable_undo(True)
        self.title_widget.title_changed = False


