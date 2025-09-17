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
from gi.repository import Gtk, GLib

from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.set_width(252)

        entries = list()
        entries.append(['p', _('Paragraph'), 'Ctrl+7'])
        entries.append(['h2', _('Heading 2'), 'Ctrl+2'])
        entries.append(['h3', _('Heading 3'), 'Ctrl+3'])
        entries.append(['h4', _('Heading 4'), 'Ctrl+4'])
        entries.append(['h5', _('Heading 5'), 'Ctrl+5'])
        entries.append(['h6', _('Heading 6'), 'Ctrl+6'])

        for entry in entries:
            button = MenuBuilder.create_button(entry[1], shortcut=entry[2])
            button.set_detailed_action_name('win.set-paragraph-style::' + entry[0])
            self.add_closing_button(button)

    def on_popup(self):
        pass

    def on_popdown(self):
        pass


