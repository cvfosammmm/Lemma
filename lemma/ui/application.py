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
from gi.repository import Adw
from gi.repository import Gdk

from lemma.services.message_bus import MessageBus
from lemma.services.color_manager import ColorManager
from lemma.ui.dialogs.dialog_locator import DialogLocator
from lemma.ui.popovers.popover_manager import PopoverManager

import lemma.ui.colors as colors
import lemma.ui.window_state as window_state
import lemma.ui.main_window_view as main_window_view
import lemma.ui.document_history as document_history
import lemma.ui.document_view as document_view
import lemma.ui.context_menu_document as context_menu_document
import lemma.ui.cursor_state as cursor_state
import lemma.ui.toolbars as toolbars
import lemma.ui.document_list as document_list
import lemma.ui.document_draft as document_draft
import lemma.ui.backlinks as backlinks
import lemma.ui.actions as actions
import lemma.ui.autocomplete as autocomplete
import lemma.ui.model_state as model_state
import lemma.ui.shortcuts as shortcuts
import lemma.services.timer as timer


class Application(Adw.Application):

    def __init__(self):
        Adw.Application.__init__(self, application_id='org.cvfosammmm.Lemma')

    def do_activate(self):
        Adw.Application.do_activate(self)

        self.main_window = main_window_view.MainWindow(self)
        self.model_state = model_state.ModelState(self.main_window)

        ColorManager.init(self.main_window)
        self.main_window.add_widgets()
        DialogLocator.init_dialogs(self.main_window)

        self.colors = colors.Colors(self.main_window)
        self.popover_manager = PopoverManager(self.main_window)
        self.document_history = document_history.DocumentHistory(self.main_window)
        self.document_view = document_view.DocumentView(self.main_window, self.model_state, self)
        self.context_menu_document = context_menu_document.ContextMenuDocument(self.main_window, self.model_state, self)
        self.cursor_state = cursor_state.CursorState(self.main_window)
        self.toolbars = toolbars.ToolBars(self.main_window)
        self.document_draft = document_draft.DocumentDraft(self.main_window)
        self.document_list = document_list.DocumentList(self.main_window)
        self.backlinks = backlinks.Backlinks(self.main_window, self.model_state)
        self.actions = actions.Actions(self.main_window, self, self.model_state)
        self.autocomplete = autocomplete.Autocomplete(self.main_window)
        self.shortcuts = shortcuts.Shortcuts(self.actions, self.main_window)
        self.window_state = window_state.WindowState(self.main_window)

        Gdk.Display.get_default().get_clipboard().connect('changed', self.on_clipboard_changed)
        MessageBus.connect('history_changed', self.on_history_changed)
        MessageBus.connect('new_document', self.on_new_document)
        MessageBus.connect('document_removed', self.on_document_removed)
        MessageBus.connect('document_changed', self.on_document_changed)
        MessageBus.connect('document_ast_changed', self.on_document_ast_changed)
        MessageBus.connect('mode_set', self.on_mode_set)
        MessageBus.connect('app_state_changed', self.on_app_state_changed)
        MessageBus.connect('settings_changed', self.on_settings_changed)

        self.model_state.update()
        self.actions.update()
        self.backlinks.update()
        self.document_history.update()
        self.cursor_state.update()
        self.document_list.update()
        self.context_menu_document.update()
        self.document_draft.update()
        self.window_state.update()
        self.colors.update()
        self.popover_manager.update()

        self.actions.actions['quit'].connect('activate', self.on_quit_action)
        self.main_window.connect('close-request', self.on_window_close)

    def on_clipboard_changed(self, clipboard):
        self.model_state.update()
        self.actions.update()

    def on_history_changed(self):
        self.model_state.update()
        self.actions.update()
        self.backlinks.update()
        self.document_history.update()
        self.cursor_state.update()
        self.document_list.update()
        self.document_view.update()
        self.context_menu_document.update()
        self.popover_manager.update()
        self.toolbars.update()
        self.window_state.update()

    def on_new_document(self):
        self.model_state.update()
        self.actions.update()
        self.document_list.update()

    def on_document_removed(self):
        self.model_state.update()
        self.actions.update()
        self.backlinks.update()
        self.document_list.update()

    @timer.timer
    def on_document_changed(self):
        self.model_state.update()
        self.actions.update()
        self.cursor_state.update()
        self.document_view.update()
        self.context_menu_document.update()
        self.popover_manager.update()
        self.toolbars.update()
        self.document_history.update()

    def on_document_ast_changed(self):
        self.model_state.update()
        self.backlinks.update()
        self.document_list.update()

    def on_mode_set(self):
        self.model_state.update()
        self.actions.update()
        self.backlinks.update()
        self.document_history.update()
        self.document_list.update()
        self.document_view.update()
        self.context_menu_document.update()
        self.popover_manager.update()
        self.document_draft.update()
        self.window_state.update()

    @timer.timer
    def on_app_state_changed(self):
        self.toolbars.update()
        self.shortcuts.update()
        self.popover_manager.update()
        self.cursor_state.update_tag_toggle(self.cursor_state.toolbar.toolbar_main.bold_button, 'bold')
        self.cursor_state.update_tag_toggle(self.cursor_state.toolbar.toolbar_main.italic_button, 'italic')

    def on_settings_changed(self):
        self.window_state.update()
        self.colors.update()

    def on_window_close(self, window=None, parameter=None):
        self.save_quit()
        return True

    def on_quit_action(self, action=None, parameter=None):
        self.save_quit()

    def save_quit(self):
        self.window_state.save_window_state()
        self.quit()


