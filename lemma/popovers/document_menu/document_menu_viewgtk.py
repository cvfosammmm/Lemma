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

from lemma.popovers.helpers.popover_menu_builder import MenuBuilder
from lemma.popovers.helpers.popover import Popover


class DocumentMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(306)

        self.delete_document_button = MenuBuilder.create_button(_('Delete Document'))
        self.delete_document_button.set_action_name('win.delete-document')
        self.add_closing_button(self.delete_document_button)

        self.rename_document_button = MenuBuilder.create_button(_('Rename Document'), shortcut='F2')
        self.rename_document_button.set_action_name('win.rename-document')
        self.add_closing_button(self.rename_document_button)


