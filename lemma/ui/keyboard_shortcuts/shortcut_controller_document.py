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


class ShortcutControllerDocument(ShortcutController):

    def __init__(self, actions):
        ShortcutController.__init__(self)
        self.actions = actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.create_and_add_shortcut('<Control>b', self.actions.actions['toggle-bold'].activate)
        self.create_and_add_shortcut('<Control>i', self.actions.actions['toggle-italic'].activate)
        self.create_and_add_shortcut('<Control>l', self.actions.actions['insert-link'].activate)
        self.create_and_add_shortcut('<Control>z', self.actions.actions['undo'].activate)
        self.create_and_add_shortcut('<Control><Shift>z', self.actions.actions['redo'].activate)
        self.create_and_add_shortcut('<Control>x', self.actions.actions['cut'].activate)
        self.create_and_add_shortcut('<Control>c', self.actions.actions['copy'].activate)
        self.create_and_add_shortcut('<Control>v', self.actions.actions['paste'].activate)
        self.create_and_add_shortcut('<Control>a', self.actions.actions['select-all'].activate)


