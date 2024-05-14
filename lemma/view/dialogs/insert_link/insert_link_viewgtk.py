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
from gi.repository import Gtk, Gdk, GObject

import os

from lemma.view.dialogs.helpers.dialog_viewgtk import DialogView


class InsertLinkView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(400, -1)
        self.get_style_context().add_class('insert-link-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.add_button = Gtk.Button.new_with_mnemonic(_('Insert'))
        self.add_button.set_can_focus(False)
        self.add_button.get_style_context().add_class('suggested-action')
        self.headerbar.pack_end(self.add_button)

        self.entry_link_target = Gtk.Entry()
        self.entry_link_target.set_placeholder_text(_('Link Target'))

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.append(self.entry_link_target)

        self.topbox.append(self.content)


