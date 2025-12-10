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
gi.require_version('Adw', '1')
from gi.repository import Adw

from lemma.services.color_manager import ColorManager
from lemma.ui.dialogs.dialog_locator import DialogLocator
from lemma.ui.popovers.popover_manager import PopoverManager
import lemma.services.timer as timer

import lemma.ui.colors as colors
import lemma.ui.window_state as window_state
import lemma.ui.views.main_window_view as main_window_view
import lemma.ui.history as history
import lemma.ui.document_view as document_view
import lemma.ui.document_title as document_title
import lemma.ui.scrollbars as scrollbars
import lemma.ui.document_context_menu as context_menu_document
import lemma.ui.cursor_state as cursor_state
import lemma.ui.toolbars as toolbars
import lemma.ui.pinned_documents as pinned_documents
import lemma.ui.document_list as document_list
import lemma.ui.document_draft as document_draft
import lemma.ui.backlinks as backlinks
import lemma.ui.actions as actions
import lemma.ui.sidebar_emojis as sidebar_emojis
import lemma.ui.sidebar_math as sidebar_math
import lemma.ui.autocomplete as autocomplete
import lemma.ui.shortcuts as shortcuts


class Application(Adw.Application):

    def __init__(self):
        Adw.Application.__init__(self, application_id='org.cvfosammmm.Lemma')

    def do_activate(self):
        Adw.Application.do_activate(self)

        self.main_window = main_window_view.MainWindow(self)

        ColorManager.init(self.main_window)
        self.main_window.add_widgets()
        DialogLocator.init_dialogs(self.main_window)

        self.colors = colors.Colors(self.main_window)
        self.popover_manager = PopoverManager(self.main_window)
        self.history = history.History(self.main_window)
        self.document_view = document_view.DocumentView(self.main_window, self)
        self.document_title = document_title.DocumentTitle(self.main_window, self)
        self.scrollbars = scrollbars.Scrollbars(self.main_window, self)
        self.context_menu_document = context_menu_document.ContextMenuDocument(self.main_window, self)
        self.cursor_state = cursor_state.CursorState(self.main_window)
        self.toolbars = toolbars.ToolBars(self.main_window)
        self.pinned_documents = pinned_documents.PinnedDocuments(self.main_window, self)
        self.document_draft = document_draft.DocumentDraft(self.main_window)
        self.document_list = document_list.DocumentList(self.main_window)
        self.backlinks = backlinks.Backlinks(self.main_window)
        self.actions = actions.Actions(self.main_window, self)
        self.sidebar_emojis = sidebar_emojis.SidebarEmojis(self.main_window, self)
        self.sidebar_math = sidebar_math.SidebarMath(self.main_window, self)
        self.autocomplete = autocomplete.Autocomplete(self.main_window, self)
        self.shortcuts = shortcuts.Shortcuts(self.main_window, self)
        self.window_state = window_state.WindowState(self.main_window)

        self.actions.actions['quit'].connect('activate', self.on_quit_action)
        self.main_window.connect('close-request', self.on_window_close)

        self.main_window.add_tick_callback(self.animate)

    @timer.timer
    def animate(self, widget, frame_clock):
        self.colors.animate()
        self.actions.animate()
        self.shortcuts.animate()
        self.window_state.animate()
        self.popover_manager.animate()
        self.document_list.animate()
        self.history.animate()
        self.backlinks.animate()
        self.document_draft.animate()
        self.document_view.animate()
        self.document_title.animate()
        self.context_menu_document.animate()
        self.autocomplete.animate()
        self.scrollbars.animate()
        self.cursor_state.animate()
        self.toolbars.animate()
        self.pinned_documents.animate()
        self.sidebar_emojis.animate()
        self.sidebar_math.animate()

        return True

    def on_window_close(self, window=None, parameter=None):
        self.save_quit()
        return True

    def on_quit_action(self, action=None, parameter=None):
        self.save_quit()

    def save_quit(self):
        self.window_state.save_window_state()
        self.quit()


