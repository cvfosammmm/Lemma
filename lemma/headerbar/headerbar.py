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

from lemma.headerbar.headerbar_view import HeaderBarView


class HeaderBar(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.view = HeaderBarView()

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('mode_set', self.on_mode_set)

        self.update_buttons()

    def on_new_active_document(self, workspace, document=None):
        self.update_buttons()

    def on_mode_set(self, workspace):
        self.update_buttons()

    def update_buttons(self):
        self.view.hb_right.document_menu_button.set_sensitive(self.workspace.mode == 'documents' and self.workspace.active_document != None)


