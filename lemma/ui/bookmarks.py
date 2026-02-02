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
from gi.repository import Gtk, Gdk

from lemma.services.message_bus import MessageBus
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
from lemma.application_state.application_state import ApplicationState
import lemma.services.timer as timer


class Bookmarks():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.popover = self.application.popover_manager.popovers["bookmarks"]
        self.drag_start_id = None

        for i, button in enumerate(self.popover.bookmark_buttons):
            button.connect('clicked', self.on_bookmark_clicked, i)
        for i, button in enumerate(self.popover.bookmark_remove_buttons):
            button.connect('clicked', self.on_bookmark_remove_clicked, i)
        for i, handle in enumerate(self.popover.bookmark_drag_handles):
            drag_controller = Gtk.GestureDrag()
            drag_controller.connect('drag-begin', self.on_drag_begin, i)
            drag_controller.connect('drag-update', self.on_drag_update, i)
            drag_controller.connect('drag-end', self.on_drag_end, i)
            handle.add_controller(drag_controller)
        self.popover.edit_bookmarks_button.connect('clicked', self.on_edit_bookmarks_button_clicked)
        self.popover.done_editing_button.connect('clicked', self.on_done_editing_button_clicked)
        self.popover.bookmark_document_button.connect('clicked', self.bookmark_document)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'bookmarks_changed')
        MessageBus.subscribe(self, 'app_state_changed')

        self.update_bookmark_buttons()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'bookmarks_changed' in messages or 'history_changed' in messages or 'app_state_changed' in messages:
            self.update_bookmark_buttons()

    @timer.timer
    def update_bookmark_buttons(self):
        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()
        document = workspace.get_active_document()

        for i in range(len(bookmarks)):
            document_title = DocumentRepo.get_stub_by_id(bookmarks[i])['title']
            self.popover.bookmark_button_labels[i].set_text(document_title)
            self.popover.bookmark_labels[i].set_text(document_title)

        for i, button in enumerate(self.popover.bookmark_buttons):
            button.set_sensitive(len(bookmarks) > i and not self.popover.edit_mode)
            button.set_visible(len(bookmarks) > i and not self.popover.edit_mode)

        for i, button in enumerate(self.popover.bookmark_labels):
            button.set_sensitive(len(bookmarks) > i and self.popover.edit_mode)
            button.set_visible(len(bookmarks) > i and self.popover.edit_mode)

        for i, box in enumerate(self.popover.bookmark_button_boxes):
            box.set_visible(len(bookmarks) > i)

        self.popover.empty_state.set_visible(len(bookmarks) <= 0)
        self.popover.headline.set_visible(len(bookmarks) > 0)

        self.popover.edit_mode = self.popover.edit_mode and len(workspace.get_bookmarked_document_ids()) > 0

        current_document_has_no_bookmark = (document != None and document.id not in workspace.get_bookmarked_document_ids())
        space_available = (len(workspace.get_bookmarked_document_ids()) < 9)
        self.popover.bookmark_document_button.set_sensitive(current_document_has_no_bookmark and space_available)

        self.popover.edit_bookmarks_button.set_sensitive(len(workspace.get_bookmarked_document_ids()) > 0 and not self.popover.edit_mode)
        self.popover.edit_bookmarks_button.set_visible(len(workspace.get_bookmarked_document_ids()) > 0 and not self.popover.edit_mode)
        self.popover.done_editing_button.set_sensitive(len(workspace.get_bookmarked_document_ids()) > 0 and self.popover.edit_mode)
        self.popover.done_editing_button.set_visible(len(workspace.get_bookmarked_document_ids()) > 0 and self.popover.edit_mode)

        for i, button in enumerate(self.popover.bookmark_remove_buttons):
            button.set_sensitive(self.popover.edit_mode)
            button.set_visible(self.popover.edit_mode)

        for i, handle in enumerate(self.popover.bookmark_drag_handles):
            handle.set_sensitive(self.popover.edit_mode)
            handle.set_visible(self.popover.edit_mode)

    def on_bookmark_clicked(self, button, button_pos):
        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()

        if len(bookmarks) >= button_pos:
            document_id = bookmarks[button_pos]
            UseCases.set_active_document(document_id, update_history=True)
            UseCases.hide_popovers()

    def on_bookmark_remove_clicked(self, button, button_pos):
        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()

        if len(bookmarks) >= button_pos:
            document_id = bookmarks[button_pos]
            UseCases.unbookmark_document(document_id)

    def on_drag_begin(self, gesture, x, y, start_position):
        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()

        self.drag_start_id = bookmarks[start_position]

        gesture.get_widget().set_cursor_from_name('grabbing')

    def on_drag_update(self, gesture, x, y, start_position):
        if self.drag_start_id == None: return

        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()

        new_position = max(0, min(len(bookmarks) - 1, round(start_position + y / 34)))
        UseCases.move_bookmark(self.drag_start_id, new_position)

    def on_drag_end(self, gesture, x, y, start_position):
        gesture.get_widget().set_cursor_from_name('grab')

    def on_edit_bookmarks_button_clicked(self, button):
        self.popover.edit_mode = True
        self.update_bookmark_buttons()

    def on_done_editing_button_clicked(self, button):
        self.popover.edit_mode = False
        self.update_bookmark_buttons()

    def bookmark_document(self, button=None, parameter=''):
        active_document_id = WorkspaceRepo.get_workspace().get_active_document_id()

        UseCases.bookmark_document(active_document_id)


