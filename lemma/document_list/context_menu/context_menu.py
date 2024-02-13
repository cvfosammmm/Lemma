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
from gi.repository import Gdk
from gi.repository import Gtk

from lemma.document_list.context_menu.context_menu_viewgtk import ContextMenuView


class ContextMenu(object):
    
    def __init__(self, document_list):
        self.document_list = document_list
        self.view = ContextMenuView(document_list.view)

        self.view.delete_document_button.connect('clicked', self.on_delete_document_clicked)
        self.view.connect('closed', self.on_menu_closed)

    def on_delete_document_clicked(self, button):
        index = self.document_list.selected_index
        self.view.popdown()
        self.document_list.workspace.delete_document(self.document_list.documents[index])

    def popup_at_cursor(self, x, y):
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = 1
        rect.height = 1
        self.view.set_pointing_to(rect)
        self.view.popup()

    def on_menu_closed(self, popover):
        self.document_list.set_selected_index(None)


