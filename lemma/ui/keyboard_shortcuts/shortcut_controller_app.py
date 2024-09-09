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

from lemma.ui.keyboard_shortcuts.shortcut_controller import ShortcutController


class ShortcutControllerApp(ShortcutController):

    def __init__(self, actions):
        ShortcutController.__init__(self)
        self.actions = actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.add_with_callback('<Control>q', self.actions.actions['quit'].activate)
        self.add_with_callback('<Control>n', self.actions.actions['add-document'].activate)
        self.add_with_callback('<Control>f', self.actions.actions['start-global-search'].activate)
        self.add_with_callback('<Alt>Left', self.actions.actions['go-back'].activate)
        self.add_with_callback('<Alt>Right', self.actions.actions['go-forward'].activate)
        self.add_with_callback('F2', self.actions.actions['rename-document'].activate)
        self.add_with_callback('<Control>question', self.actions.actions['show-shortcuts-dialog'].activate)
        self.add_with_callback('<Control>m', self.actions.actions['toggle-math-sidebar'].activate)
        self.add_with_callback('F10', self.actions.actions['show-hamburger-menu'].activate)
        self.add_with_callback('F12', self.actions.actions['show-document-menu'].activate)


