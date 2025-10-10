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
from gi.repository import Gtk
from gi.repository import Gdk

import datetime

from lemma.document_repo.document_repo import DocumentRepo
import lemma.ui.title_widget_view as title_widget_view
import lemma.services.timer as timer


class TitleWidget(object):

    def __init__(self, document_view):
        self.document_view = document_view

        self.view = title_widget_view.TitleWidgetView()

        self.document = None
        self.title = ''
        self.title_changed = False
        self.validation_state = False
        self.is_active = False

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.view.title_entry.add_controller(self.focus_controller)

        self.view.title_entry.connect('changed', self.on_entry_changed)

    def set_document(self, document):
        self.document = document
        if document != None:
            self.reset_title()

    def on_focus_in(self, controller):
        if not self.is_active:
            self.activate()

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
        elif self.title != self.document.title and len(DocumentRepo.list_by_title(self.title)) > 0:
            validation_state = False

        if self.title != self.document.title and self.title == '':
            self.view.subtext.set_text('Name cannot be empty.')
            self.view.subtext.add_css_class('error')
            self.view.title_entry.add_css_class('error')
        elif self.title != self.document.title and len(DocumentRepo.list_by_title(self.title)) > 0:
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


