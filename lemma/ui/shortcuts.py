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

from lemma.services.message_bus import MessageBus
from lemma.ui.popovers.popover_manager import PopoverManager
from lemma.application_state.application_state import ApplicationState
import lemma.services.timer as timer


class Shortcuts(object):

    def __init__(self, actions, main_window):
        self.main_window = main_window
        self.actions = actions

        self.shortcut_controller_app = ShortcutControllerApp(self.actions)
        self.shortcut_controller_document = ShortcutControllerDocument(self.actions)

        self.main_window.add_controller(self.shortcut_controller_app)
        self.main_window.document_view.content.add_controller(self.shortcut_controller_document)

        MessageBus.subscribe(self, 'app_state_changed')

    @timer.timer
    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'app_state_changed' in messages:
            self.update()

    @timer.timer
    def update(self):
        if ApplicationState.get_value('active_popover') != None:
            if self.shortcut_controller_app.get_widget() == self.main_window:
                self.main_window.remove_controller(self.shortcut_controller_app)
        else:
            if self.shortcut_controller_app.get_widget() == None:
                self.main_window.add_controller(self.shortcut_controller_app)


class ShortcutController(Gtk.ShortcutController):

    def __init__(self):
        Gtk.ShortcutController.__init__(self)

    def add_with_callback(self, trigger_string, callback):
        shortcut = Gtk.Shortcut()

        shortcut.set_action(Gtk.CallbackAction.new(self.action, callback))
        shortcut.set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

        self.add_shortcut(shortcut)

    def action(self, a, b, callback):
        callback()
        return True


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
        actions.application.set_accels_for_action('win.toggle-tools-sidebar::math', ['<Alt>1'])
        actions.application.set_accels_for_action('win.toggle-tools-sidebar::emojis', ['<Alt>2'])
        self.add_with_callback('F10', self.actions.actions['show-hamburger-menu'].activate)
        self.add_with_callback('F12', self.actions.actions['show-document-menu'].activate)


class ShortcutControllerDocument(ShortcutController):

    def __init__(self, actions):
        ShortcutController.__init__(self)
        self.actions = actions

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.add_with_callback('<Control>b', self.actions.actions['toggle-bold'].activate)
        self.add_with_callback('<Control>i', self.actions.actions['toggle-italic'].activate)
        actions.application.set_accels_for_action('win.set-paragraph-style::h2', ['<Control>2'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h3', ['<Control>3'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h4', ['<Control>4'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h5', ['<Control>5'])
        actions.application.set_accels_for_action('win.set-paragraph-style::h6', ['<Control>6'])
        actions.application.set_accels_for_action('win.set-paragraph-style::ul', ['<Control>7'])
        actions.application.set_accels_for_action('win.set-paragraph-style::ol', ['<Control>8'])
        actions.application.set_accels_for_action('win.set-paragraph-style::cl', ['<Control>9'])
        actions.application.set_accels_for_action('win.set-paragraph-style::p', ['<Control>0'])
        self.add_with_callback('<Control>l', self.actions.actions['show-link-popover'].activate)
        self.add_with_callback('<Control>minus', self.actions.actions['subscript'].activate)
        self.add_with_callback('<Control>underscore', self.actions.actions['superscript'].activate)
        self.add_with_callback('<Control>m', self.actions.actions['toggle-checkbox'].activate)

        self.add_with_callback('<Control>z', self.actions.actions['undo'].activate)
        self.add_with_callback('<Control><Shift>z', self.actions.actions['redo'].activate)
        self.add_with_callback('<Control>x', self.actions.actions['cut'].activate)
        self.add_with_callback('<Control>c', self.actions.actions['copy'].activate)
        self.add_with_callback('<Control>v', self.actions.actions['paste'].activate)
        self.add_with_callback('<Control>a', self.actions.actions['select-all'].activate)


