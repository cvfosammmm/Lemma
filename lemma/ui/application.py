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

from lemma.infrastructure.color_manager import ColorManager
from lemma.ui.dialogs.dialog_locator import DialogLocator
from lemma.ui.popovers.popover_manager import PopoverManager

import lemma.ui.colors.colors as colors
import lemma.ui.panels.panels as panels
import lemma.ui.main_window.main_window as main_window
import lemma.ui.document_history.document_history as document_history
import lemma.ui.document_view.document_view as document_view
import lemma.ui.cursor_state.cursor_state as cursor_state
import lemma.ui.toolbar.toolbar as toolbar
import lemma.ui.document_list.document_list as document_list
import lemma.ui.document_draft.document_draft as document_draft
import lemma.ui.backlinks.backlinks as backlinks
import lemma.ui.actions.actions as actions
import lemma.ui.keyboard_shortcuts.shortcuts as shortcuts


class Application(Adw.Application):

    def __init__(self, workspace, use_cases):
        Adw.Application.__init__(self, application_id='org.cvfosammmm.Lemma')
        self.workspace = workspace
        self.use_cases = use_cases

    def do_activate(self):
        Adw.Application.do_activate(self)

        self.main_window = main_window.MainWindow(self)
        ColorManager.init(self.main_window)
        PopoverManager.init(self.main_window, self.workspace)
        self.main_window.add_widgets()
        DialogLocator.init_dialogs(self.main_window)

        self.colors = colors.Colors(self.workspace, self.main_window)
        self.document_history = document_history.DocumentHistory(self.workspace, self.main_window)
        self.document_view = document_view.DocumentView(self.workspace, self.main_window, self)
        self.cursor_state = cursor_state.CursorState(self.workspace, self.main_window)
        self.toolbar = toolbar.ToolBar(self.workspace, self.main_window)
        self.document_draft = document_draft.DocumentDraft(self.workspace, self.main_window)
        self.document_list = document_list.DocumentList(self.workspace, self.main_window)
        self.backlinks = backlinks.Backlinks(self.workspace, self.main_window, self)
        self.actions = actions.Actions(self.workspace, self.main_window, self)
        self.shortcuts = shortcuts.Shortcuts(self.actions, self.main_window)
        self.panels = panels.Panels(self.workspace, self.main_window, self)


