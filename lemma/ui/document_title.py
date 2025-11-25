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

import time, math, datetime
from urllib.parse import urlparse

from lemma.services.settings import Settings
from lemma.ui.document_view_controller import DocumentViewController
from lemma.ui.document_view_presenter import DocumentViewPresenter
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
from lemma.services.layout_info import LayoutInfo
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class DocumentTitle():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.document_view = main_window.document_view
        self.view = main_window.document_view.title_widget

        self.is_active = False
        self.document = None

        self.view.title_entry.connect('activate', self.on_entry_activate)
        self.view.submit_button.connect('clicked', self.on_submit_button_clicked)
        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)

        self.focus_controller_entry = Gtk.EventControllerFocus()
        self.focus_controller_entry.connect('enter', self.on_title_entry_focus_in)
        self.view.title_entry.add_controller(self.focus_controller_entry)

        self.focus_controller_content = Gtk.EventControllerFocus()
        self.focus_controller_content.connect('enter', self.on_content_focus_in)
        self.document_view.content.add_controller(self.focus_controller_content)

        self.key_controller_window = Gtk.EventControllerKey()
        self.key_controller_window.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_window.connect('key-pressed', self.on_entry_keypress)
        self.view.title_entry.add_controller(self.key_controller_window)

        self.view.title_entry.connect('changed', self.on_title_entry_changed)

    @timer.timer
    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        new_active_document = document != self.document
        if new_active_document:
            self.document = document
            self.cancel()
            self.reset_title()

        if document == None:
            self.view.set_offset_y(0)
        else:
            offset = document.get_current_scrolling_offsets()[1]
            self.view.set_offset_y(offset)
        self.document_view.queue_allocate()

    def on_entry_activate(self, entry=None):
        self.submit()

    def on_submit_button_clicked(self, widget=None):
        self.submit()

    def on_cancel_button_clicked(self, widget=None):
        self.cancel()

    def on_title_entry_focus_in(self, controller):
        if not self.is_active:
            self.is_active = True
            self.reset_title()
            self.validate_title()
            self.view.button_revealer.set_reveal_child(True)
            UseCases.app_state_set_value('title_buttons_height', 50)
            UseCases.scroll_to_xy(0, 0, animation_type='default')

    def on_content_focus_in(self, controller):
        self.cancel()

    def on_entry_keypress(self, controller, keyval, keycode, state):
        if keyval == Gdk.keyval_from_name('Escape'):
            if state & Gtk.accelerator_get_default_mod_mask() == 0:
                self.cancel()
                return True
        return False

    def on_title_entry_changed(self, entry):
        self.validate_title()

    def init_renaming(self):
        if self.document != None:
            self.view.title_entry.grab_focus()
            self.view.title_entry.set_position(self.view.title_entry.get_text_length())

    def submit(self):
        if not self.view.submit_button.get_sensitive(): return

        document = WorkspaceRepo.get_workspace().get_active_document()
        prev_title = document.title
        title = self.view.title_entry.get_text()

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

        self.view.button_revealer.set_reveal_child(False)
        UseCases.app_state_set_value('title_buttons_height', 0)
        self.document_view.content.grab_focus()

        self.is_active = False

    def cancel(self):
        self.reset_title()

        self.view.button_revealer.set_reveal_child(False)
        UseCases.app_state_set_value('title_buttons_height', 0)
        self.document_view.content.grab_focus()

        self.is_active = False

    def reset_title(self):
        if self.document == None:
            self.view.title_entry.set_enable_undo(False)
            self.view.title_entry.set_text('')
            self.view.title_entry.set_enable_undo(True)

            self.view.subtext.set_text('')
        else:
            self.view.title_entry.set_enable_undo(False)
            self.view.title_entry.set_text(self.document.title)
            self.view.title_entry.set_enable_undo(True)

            datetime_last_modified = datetime.datetime.fromtimestamp(self.document.last_modified)
            self.view.subtext.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))

        self.view.subtext.remove_css_class('error')
        self.view.title_entry.remove_css_class('error')

    def validate_title(self):
        if self.document == None: return

        title = self.view.title_entry.get_text()

        validation_state = True
        if title == '':
            validation_state = False
        elif title != self.document.title and len(DocumentRepo.list_by_title(title)) > 0:
            validation_state = False
        self.view.submit_button.set_sensitive(validation_state)

        if title != self.document.title and title == '':
            self.view.subtext.set_text('Name cannot be empty.')
            self.view.subtext.add_css_class('error')
            self.view.title_entry.add_css_class('error')
        elif title != self.document.title and len(DocumentRepo.list_by_title(title)) > 0:
            self.view.subtext.set_text('A document with this name already exists.')
            self.view.subtext.add_css_class('error')
            self.view.title_entry.add_css_class('error')
        else:
            self.view.subtext.set_text('Please enter a name for this document.')
            self.view.subtext.remove_css_class('error')
            self.view.title_entry.remove_css_class('error')


