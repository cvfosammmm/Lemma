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
from gi.repository import Gtk, Gdk, GObject

import os

from lemma.ui.popovers.popover_templates import PopoverView
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
import lemma.services.xml_helpers as xml_helpers


class Popover(PopoverView):

    def __init__(self, manager):
        PopoverView.__init__(self, manager)
        self.application = manager.application

        self.current_values = dict()
        self.is_valid = False

        self.add_css_class('rename-file-popover')
        self.set_width(300)
        self.set_size_request(300, -1)

        self.title_label = Gtk.Label.new(_('Rename File'))
        self.title_label.add_css_class('title-2')
        self.title_label.set_margin_top(18)
        self.title_label.set_margin_bottom(12)

        self.entry = Gtk.Entry()
        self.entry.set_margin_start(18)
        self.entry.set_margin_end(18)
        self.entry.set_margin_bottom(6)

        self.error_msg = Gtk.Label.new('')
        self.error_msg.set_xalign(0)
        self.error_msg.set_margin_start(18)
        self.error_msg.set_margin_end(18)
        self.error_msg.set_margin_bottom(6)
        self.error_msg.add_css_class('error')

        self.error_msg_revealer = Gtk.Revealer()
        self.error_msg_revealer.set_child(self.error_msg)
        self.error_msg_revealer.set_reveal_child(False)
        self.error_msg_revealer.set_margin_bottom(6)

        self.submit_button = Gtk.Button.new_with_label(_('Rename'))
        self.submit_button.add_css_class('suggested-action')
        self.submit_button.set_can_focus(False)
        self.submit_button.set_margin_bottom(18)
        self.submit_button.set_hexpand(False)
        self.submit_button.set_margin_end(18)

        submit_button_box = Gtk.CenterBox.new()
        submit_button_box.set_end_widget(self.submit_button)

        self.add_widget(self.title_label)
        self.add_widget(self.entry)
        self.add_widget(self.error_msg_revealer)
        self.add_widget(submit_button_box)

        self.submit_button.connect('clicked', self.on_submit_button_clicked)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.entry.add_controller(self.key_controller)
        self.entry.connect('changed', self.on_entry_changed)
        self.entry.connect('activate', self.on_entry_activate)

    def on_popup(self):
        self.init_current_values()

        document = WorkspaceRepo.get_workspace().get_active_document()

        nodes = document.get_selected_nodes()
        widget = nodes[0].value
        filename = os.path.basename(widget.get_attribute('filename'))

        self.current_values['original_name'] = filename
        self.entry.set_text(filename)

        self.validate()
        self.entry.grab_focus()

    def on_popdown(self):
        pass

    def init_current_values(self):
        self.current_values['original_name'] = ''
        self.current_values['name'] = ''

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('Escape'):
            if state & modifiers == 0:
                self.manager.hide_popovers()
                return True

        return False

    def on_entry_changed(self, entry):
        self.current_values['name'] = entry.get_text()
        self.validate()

    def on_entry_activate(self, entry):
        self.submit()

    def on_suggestion_row_activated(self, listbox, row):
        self.entry.set_text(row.title)
        self.entry.set_position(-1)
        self.submit()

    def on_submit_button_clicked(self, button):
        self.submit()

    def validate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        self.is_valid = True
        if self.current_values['name'] == '':
            self.is_valid = False
            self.error_msg.set_text('Filename cannot be empty.')
        if self.current_values['name'] != self.current_values['original_name'] and self.current_values['name'] in [os.path.basename(file) for file in document.files]:
            self.is_valid = False
            self.error_msg.set_text('A file with this name already exists.')

        self.submit_button.set_sensitive(self.is_valid)
        self.error_msg_revealer.set_reveal_child(not self.is_valid)
        if self.is_valid:
            self.entry.remove_css_class('error')
        else:
            self.entry.add_css_class('error')

    def submit(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if self.is_valid:
            UseCases.set_widget_attribute_filename('filename', str(document.id) + '_files/' + self.current_values['name'])

            self.manager.hide_popovers()


