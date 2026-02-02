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
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class Shortcuts(object):

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application

        self.shortcut_controller_app = ShortcutControllerApp(self.application)
        self.shortcut_controller_document = ShortcutControllerDocument(self.application)

        self.main_window.add_controller(self.shortcut_controller_app)
        self.main_window.document_view.content.add_controller(self.shortcut_controller_document)

        MessageBus.subscribe(self, 'app_state_changed')

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

    def add_with_callback(self, trigger_string, callback, data=None):
        callback_action = Gtk.CallbackAction.new(self.action, (callback, data))

        shortcut = Gtk.Shortcut()
        shortcut.set_action(callback_action)
        shortcut.set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

        self.add_shortcut(shortcut)

    def action(self, a, b, arguments):
        callback, data = arguments
        if data != None:
            callback(data)
        else:
            callback()
        return True


class ShortcutControllerApp(ShortcutController):

    def __init__(self, application):
        ShortcutController.__init__(self)
        self.application = application

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.add_with_callback('<Control>q', self.application.actions.actions['quit'].activate)
        self.add_with_callback('<Control>n', self.application.actions.actions['add-document'].activate)
        self.add_with_callback('<Control>f', self.application.actions.actions['start-global-search'].activate)
        self.add_with_callback('<Alt>Left', self.application.actions.actions['go-back'].activate)
        self.add_with_callback('<Alt>Right', self.application.actions.actions['go-forward'].activate)
        self.add_with_callback('F2', self.application.actions.actions['rename-document'].activate)
        self.add_with_callback('<Control>question', self.application.actions.actions['show-shortcuts-dialog'].activate)
        self.add_with_callback('F10', self.application.actions.actions['show-hamburger-menu'].activate)
        self.add_with_callback('F12', self.application.actions.actions['show-document-menu'].activate)

        for i in range(1, 10):
            self.add_with_callback('<Alt>' + str(i), self.activate_bookmark, i)

    def activate_bookmark(self, button_pos):
        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()

        if len(bookmarks) >= button_pos:
            document_id = bookmarks[button_pos - 1]
            UseCases.set_active_document(document_id, update_history=True)


class ShortcutControllerDocument(ShortcutController):

    def __init__(self, application):
        ShortcutController.__init__(self)
        self.application = application

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

        self.add_with_callback('<Control>b', self.application.actions.actions['toggle-bold'].activate)
        self.add_with_callback('<Control>i', self.application.actions.actions['toggle-italic'].activate)
        self.add_with_callback('<Control>u', self.application.actions.actions['toggle-highlight'].activate)
        self.add_with_callback('<Control>l', self.application.actions.actions['show-link-popover'].activate)
        self.add_with_callback('<Control>minus', self.application.actions.actions['subscript'].activate)
        self.add_with_callback('<Control>underscore', self.application.actions.actions['superscript'].activate)
        self.add_with_callback('<Control>m', self.application.actions.actions['toggle-checkbox'].activate)

        self.add_with_callback('<Control>z', self.application.actions.actions['undo'].activate)
        self.add_with_callback('<Control><Shift>z', self.application.actions.actions['redo'].activate)
        self.add_with_callback('<Control>x', self.application.actions.actions['cut'].activate)
        self.add_with_callback('<Control>c', self.application.actions.actions['copy'].activate)
        self.add_with_callback('<Control>v', self.application.actions.actions['paste'].activate)
        self.add_with_callback('<Control>a', self.application.actions.actions['select-all'].activate)

        self.application.set_accels_for_action('win.set-paragraph-style::h2', ['<Control>2'])
        self.application.set_accels_for_action('win.set-paragraph-style::h3', ['<Control>3'])
        self.application.set_accels_for_action('win.set-paragraph-style::h4', ['<Control>4'])
        self.application.set_accels_for_action('win.set-paragraph-style::h5', ['<Control>5'])
        self.application.set_accels_for_action('win.set-paragraph-style::h6', ['<Control>6'])
        self.application.set_accels_for_action('win.set-paragraph-style::ul', ['<Control>7'])
        self.application.set_accels_for_action('win.set-paragraph-style::ol', ['<Control>8'])
        self.application.set_accels_for_action('win.set-paragraph-style::cl', ['<Control>9'])
        self.application.set_accels_for_action('win.set-paragraph-style::p', ['<Control>0'])


