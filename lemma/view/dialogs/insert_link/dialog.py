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


import lemma.view.dialogs.insert_link.insert_link_viewgtk as view
from lemma.document.document import Document
from lemma.app.service_locator import ServiceLocator


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.workspace = None
        self.current_values = dict()

    def run(self, workspace):
        self.workspace = workspace

        self.init_current_values()
        self.view = view.InsertLinkView(self.main_window)
        self.setup()
        self.validate()
        self.view.present()

    def init_current_values(self):
        self.current_values['link_target'] = ''

    def setup(self):
        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.add_button.connect('clicked', self.on_add_button_clicked)
        self.view.entry_link_target.connect('changed', self.on_entry_link_target_changed)
        self.view.entry_link_target.connect('activate', self.on_entry_link_target_activate)

    def on_entry_link_target_changed(self, entry):
        self.current_values['link_target'] = entry.get_text()
        self.validate()

    def on_entry_link_target_activate(self, entry):
        self.submit()

    def validate(self):
        self.view.add_button.set_sensitive(self.is_valid())

    def is_valid(self):
        return self.current_values['link_target'] != ''

    def on_cancel_button_clicked(self, button):
        self.view.close()

    def on_add_button_clicked(self, button):
        self.submit()

    def submit(self):
        if self.is_valid():
            self.workspace.get_active_document().add_command('add_link', self.current_values['link_target'])
            self.view.close()


