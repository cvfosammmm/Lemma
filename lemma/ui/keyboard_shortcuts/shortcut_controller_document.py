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
from gi.repository import Gtk, Gio, GLib

from lemma.ui.keyboard_shortcuts.shortcut_controller import ShortcutController


class ShortcutControllerDocument(ShortcutController):

    def __init__(self, actions):
        ShortcutController.__init__(self)
        self.actions = actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.add_with_callback('<Control>b', self.actions.actions['toggle-bold'].activate)
        self.add_with_callback('<Control>i', self.actions.actions['toggle-italic'].activate)
        actions.application.set_accels_for_action('win.set-paragraph-style::p', ['<Control>7'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h2', ['<Control>2'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h3', ['<Control>3'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h4', ['<Control>4'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h5', ['<Control>5'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h6', ['<Control>6'])
        self.add_with_callback('<Control>l', self.actions.actions['insert-link'].activate)
        self.add_with_callback('<Control>minus', self.actions.actions['subscript'].activate)

        self.add_with_callback('<Control>z', self.actions.actions['undo'].activate)
        self.add_with_callback('<Control><Shift>z', self.actions.actions['redo'].activate)
        self.add_with_callback('<Control>x', self.actions.actions['cut'].activate)
        self.add_with_callback('<Control>c', self.actions.actions['copy'].activate)
        self.add_with_callback('<Control>v', self.actions.actions['paste'].activate)
        self.add_with_callback('<Control>a', self.actions.actions['select-all'].activate)


