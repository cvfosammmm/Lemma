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

from lemma.app.service_locator import ServiceLocator
from lemma.keyboard_shortcuts.shortcut_controller import ShortcutController


class ShortcutControllerApp(ShortcutController):

    def __init__(self):
        ShortcutController.__init__(self)

        self.main_window = ServiceLocator.get_main_window()
        self.workspace = ServiceLocator.get_workspace()
        self.actions = self.workspace.actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.create_and_add_shortcut('<Control>q', self.actions.actions['quit'].activate)
        self.create_and_add_shortcut('<Control>n', self.actions.actions['add-document'].activate)
        self.create_and_add_shortcut('<Alt>Left', self.actions.actions['go-back'].activate)
        self.create_and_add_shortcut('<Alt>Right', self.actions.actions['go-forward'].activate)
        self.create_and_add_shortcut('F2', self.actions.actions['rename-document'].activate)
        self.create_and_add_shortcut('<Control>question', self.actions.actions['show-shortcuts-dialog'].activate)
        self.create_and_add_shortcut('F10', self.actions.actions['show-hamburger-menu'].activate)
        self.create_and_add_shortcut('F12', self.actions.actions['show-document-menu'].activate)


