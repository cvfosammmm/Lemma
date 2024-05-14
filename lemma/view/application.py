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
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from lemma.app.service_locator import ServiceLocator
from lemma.app.color_manager import ColorManager
from lemma.view.dialogs.dialog_locator import DialogLocator
from lemma.view.popovers.popover_manager import PopoverManager

import lemma.view.colors.colors as colors
import lemma.view.panels.panels as panels
import lemma.view.toolbars.toolbars as toolbars
import lemma.view.main_window.main_window as main_window
import lemma.view.document_history.document_history as document_history
import lemma.view.document_view.document_view as document_view
import lemma.view.document_list.document_list as document_list
import lemma.view.document_draft.document_draft as document_draft
import lemma.view.actions.actions as actions
import lemma.view.keyboard_shortcuts.shortcuts as shortcuts


class Application(Adw.Application):

    def __init__(self, workspace):
        Adw.Application.__init__(self, application_id='org.cvfosammmm.Lemma')

        self.workspace = workspace

    def do_activate(self):
        Adw.Application.do_activate(self)

        self.main_window = main_window.MainWindow(self)
        ServiceLocator.set_main_window(self.main_window)
        ColorManager.init(self.main_window)
        PopoverManager.init(self.main_window, self.workspace)
        self.main_window.add_widgets()
        DialogLocator.init_dialogs(self.main_window)

        self.colors = colors.Colors(self.workspace, self.main_window)
        self.document_history = document_history.DocumentHistory(self.workspace, self.main_window)
        self.document_view = document_view.DocumentView(self.workspace, self.main_window)
        self.document_draft = document_draft.DocumentDraft(self.workspace, self.main_window)
        self.document_list = document_list.DocumentList(self.workspace, self.main_window)
        self.toolbars = toolbars.Toolbars(self.workspace, self.main_window)
        self.actions = actions.Actions(self.workspace, self.document_view)
        self.shortcuts = shortcuts.Shortcuts(self.actions)
        self.panels = panels.Panels(self.workspace, self.main_window, self)

        self.document = self.workspace.get_active_document()
        if self.document != None: self.document.connect('changed', self.on_document_change)

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('mode_set', self.on_mode_set)
        self.workspace.history.connect('changed', self.on_history_change)
        ServiceLocator.get_settings().connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'color_scheme':
            self.colors.update()

    def on_history_change(self, history):
        self.actions.update()
        self.document_history.update()

    def on_new_document(self, workspace, document=None):
        self.actions.update()
        self.document_list.update()

    def on_document_removed(self, workspace, document=None):
        self.actions.update()
        self.document_list.update()

    def on_new_active_document(self, workspace, document=None):
        if self.document != None: self.document.disconnect('changed', self.on_document_change)
        self.document = document
        if document != None: self.document.connect('changed', self.on_document_change)

        self.panels.update()
        self.actions.update()
        self.document_history.update()
        self.document_list.update()
        self.toolbars.update()

    def on_document_change(self, document):
        self.actions.update()
        self.document_list.update()
        self.toolbars.update()

    def on_mode_set(self, workspace):
        self.panels.update()
        self.actions.update()
        self.document_draft.update()


