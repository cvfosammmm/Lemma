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

from lemma.helpers.menu_builder import MenuBuilder


class ContextMenuView(Gtk.Popover):

    def __init__(self, document_list_view):
        Gtk.Popover.__init__(self)

        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_parent(document_list_view)
        self.set_size_request(260, -1)
        self.set_offset(130, 0)
        self.set_has_arrow(False)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.set_child(self.box)

        self.delete_document_button = MenuBuilder.create_button('Delete document')
        MenuBuilder.add_button(self, self.delete_document_button)


