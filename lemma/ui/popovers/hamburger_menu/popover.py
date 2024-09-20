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
from lemma.ui.popovers.popover_templates import PopoverBottom


class Popover(object):

    def __init__(self, popover_manager):
        self.popover_manager = popover_manager
        self.view = View(popover_manager)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.view.add_controller(self.key_controller)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('F10'):
            if state & modifiers == 0:
                self.popover_manager.popdown()
                return True

        return False


class View(PopoverBottom):

    def __init__(self, popover_manager):
        PopoverBottom.__init__(self, popover_manager)

        self.set_width(306)

        self.button_import_markdown = MenuBuilder.create_button(_('Import Markdown Files...'))
        self.button_import_markdown.set_action_name('win.import-markdown-files')
        self.add_closing_button(self.button_import_markdown)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_bulk_export = MenuBuilder.create_button(_('Export Documents...'))
        self.button_bulk_export.set_action_name('win.export-bulk')
        self.add_closing_button(self.button_bulk_export)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_preferences = MenuBuilder.create_button(_('Settings'))
        self.button_preferences.set_action_name('win.show-preferences-dialog')
        self.add_closing_button(self.button_preferences)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_shortcuts = MenuBuilder.create_button(_('Keyboard Shortcuts'), shortcut=_('Ctrl') + '+?')
        self.button_shortcuts.set_action_name('win.show-shortcuts-dialog')
        self.add_closing_button(self.button_shortcuts)

        self.button_about = MenuBuilder.create_button(_('About'))
        self.button_about.set_action_name('win.show-about-dialog')
        self.add_closing_button(self.button_about)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_quit = MenuBuilder.create_button(_('Quit'), shortcut=_('Ctrl') + '+Q')
        self.button_quit.set_action_name('win.quit')
        self.add_closing_button(self.button_quit)


