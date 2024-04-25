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

from lemma.view.popovers.popover_menu_builder import MenuBuilder
from lemma.view.popovers.popover_templates import PopoverBottom


class Popover(object):

    def __init__(self, popover_manager):
        self.popover_manager = popover_manager
        self.view = View(popover_manager)


class View(PopoverBottom):

    def __init__(self, popover_manager):
        PopoverBottom.__init__(self, popover_manager)

        self.set_width(306)

        self.button_add_document = MenuBuilder.create_button(_('New Document'), shortcut=_('Ctrl') + '+N')
        self.button_add_document.set_action_name('win.add-document')
        self.add_closing_button(self.button_add_document)

        self.button_import_markdown = MenuBuilder.create_button(_('Import Markdown Files...'))
        self.button_import_markdown.set_action_name('win.import-markdown-files')
        self.add_closing_button(self.button_import_markdown)


