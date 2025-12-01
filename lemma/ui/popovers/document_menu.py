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

from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView
from lemma.use_cases.use_cases import UseCases


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.set_width(306)

        self.delete_document_button = MenuBuilder.create_button(_('Delete Document'))
        self.delete_document_button.set_action_name('win.delete-document')
        self.add_closing_button(self.delete_document_button)

        self.rename_document_button = MenuBuilder.create_button(_('Rename Document'), shortcut='F2')
        self.rename_document_button.set_action_name('win.rename-document')
        self.add_closing_button(self.rename_document_button)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.export_document_button = MenuBuilder.create_button(_('Export Markdown...'))
        self.export_document_button.set_action_name('win.export-markdown')
        self.add_closing_button(self.export_document_button)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.add_controller(self.key_controller)

    def on_popup(self):
        pass

    def on_popdown(self):
        pass

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('F12'):
            if state & modifiers == 0:
                UseCases.hide_popovers()

                return True

        return super().on_keypress(controller, keyval, keycode, state)


