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


class DocumentPinning():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application

        self.current_popover_index = None

        self.view = main_window.headerbar.hb_right.pin_buttons_box
        self.pin_buttons = self.view.pin_buttons
        self.document_menu = self.application.popover_manager.popovers["document_menu"]
        self.popover = self.application.popover_manager.popovers["pin_edit_menu"]

        self.document_menu.pin_document_button.connect('clicked', self.pin_document)
        self.document_menu.unpin_document_button.connect('clicked', self.unpin_document)

        for i, button in enumerate(self.pin_buttons):
            button.connect('clicked', self.on_pin_clicked, i)
            secondary_click_controller = Gtk.GestureClick()
            secondary_click_controller.set_button(3)
            secondary_click_controller.connect('pressed', self.on_secondary_button_press)
            button.add_controller(secondary_click_controller)

        self.popover.unpin_button.connect('clicked', self.on_unpin_button_click)
        self.popover.move_left_button.connect('clicked', self.move_pin_left)
        self.popover.move_right_button.connect('clicked', self.move_pin_right)

        wrapbox = self.popover.icon_wrapbox
        for icon_name in ['user-home-symbolic', 'folder-visiting-symbolic', 'inbox-symbolic', 'outbox-symbolic', 'audio-x-generic-symbolic', 'folder-download-symbolic', 'folder-pictures-symbolic', 'folder-saved-search-symbolic', 'folder-videos-symbolic', 'file-cabinet-symbolic', 'bear-symbolic', 'cat-sleeping-symbolic', 'cat-symbolic', 'cow-symbolic', 'dog-symbolic', 'horse-symbolic', 'leaf-symbolic', 'penguin-alt-symbolic', 'penguin-symbolic', 'seal-symbolic', 'sprout-symbolic', 'bug-symbolic', 'archive-symbolic', 'image-alt-symbolic', 'dice3-symbolic', 'theater-symbolic', 'cafe-symbolic', 'soup-symbolic', 'ink-tool-symbolic', 'online-symbolic', 'address-book-symbolic', 'meeting-symbolic', 'briefcase-symbolic', 'map-marker-symbolic', 'museum-symbolic', 'non-emergency-healthcare-symbolic', 'restaurant-symbolic', 'school-symbolic', 'pin-symbolic', 'view-grid-symbolic', 'mail-attachment-symbolic', 'emoji-symbols-symbolic', 'emoji-body-symbolic', 'applications-graphics-symbolic', 'applications-multimedia-symbolic', 'applications-games-symbolic', 'accessories-dictionary-symbolic', 'x-office-calendar-symbolic', 'star-large-symbolic', 'heart-filled-symbolic', 'editor-symbolic', 'library-symbolic', 'rescue-symbolic', 'globe-symbolic', 'bank-symbolic', 'shopping-cart-symbolic', 'body-symbolic', 'steps-symbolic', 'tag-outline-symbolic', 'text-x-generic-symbolic', 'lightbulb-symbolic', 'puzzle-piece-symbolic', 'people-symbolic', 'license-symbolic']:
            button = Gtk.Button.new_from_icon_name(icon_name)
            button.set_can_focus(False)
            button.add_css_class('flat')
            button.connect('clicked', self.on_icon_button_click, icon_name)
            wrapbox.append(button)

        self.popover.no_icon_button.connect('clicked', self.on_icon_button_click, None)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'pinned_documents_changed')
        MessageBus.subscribe(self, 'app_state_changed')

        self.update_pin_buttons()
        self.update_document_menu()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'pinned_documents_changed' in messages:
            self.update_pin_buttons()

        if 'pinned_documents_changed' in messages or 'history_changed' in messages:
            self.update_document_menu()

        if 'app_state_changed' in messages:
            self.update_toggle_states()

    @timer.timer
    def update_pin_buttons(self):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()

        for i in range(len(pinned_documents)):
            document_title = DocumentRepo.get_stub_by_id(pinned_documents[i])['title']
            if document_title != None:
                document_title = '"' + document_title + '"'
            else:
                document_title = 'Pinned Document ' + str(i + 1)

            button = self.pin_buttons[i]
            button.set_icon_name(workspace.get_pin_icon_name(pinned_documents[i]))
            button.set_tooltip_text('Open ' + document_title + ' (Alt+' + str(i + 1) + ')')

        for i, button in enumerate(self.pin_buttons):
            if len(pinned_documents) > i:
                button.set_sensitive(True)
                button.set_visible(True)
            else:
                button.set_sensitive(False)
                button.set_visible(False)

        self.view.set_visible(len(pinned_documents) > 0)

    @timer.timer
    def update_toggle_states(self):
        name = ApplicationState.get_value('active_popover')
        if name == 'pin_edit_menu':
            index = self.current_popover_index
        else:
            index = None

        for i, button in enumerate(self.pin_buttons):
            if i == index:
                button.add_css_class('checked')
            else:
                button.remove_css_class('checked')

    @timer.timer
    def update_document_menu(self):
        workspace = WorkspaceRepo.get_workspace()
        document = workspace.get_active_document()

        self.document_menu.pin_document_button.set_sensitive(document != None and document.id not in workspace.get_pinned_document_ids() and len(workspace.get_pinned_document_ids()) < 9)
        self.document_menu.unpin_document_button.set_sensitive(document != None and document.id in workspace.get_pinned_document_ids())

    def on_pin_clicked(self, button, button_pos):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()

        if len(pinned_documents) >= button_pos:
            document_id = pinned_documents[button_pos]
            UseCases.set_active_document(document_id, update_history=True)

    def on_unpin_button_click(self, button):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()
        document_id = pinned_documents[self.current_popover_index]

        UseCases.hide_popovers()
        UseCases.unpin_document(document_id)

    def move_pin_left(self, button=None, parameter=''):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()

        new_index = max(0, self.current_popover_index - 1)

        UseCases.move_document_pin(pinned_documents[self.current_popover_index], new_index)
        self.popup_at_index(new_index)

    def move_pin_right(self, button=None, parameter=''):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()

        new_index = min(len(pinned_documents) - 1, self.current_popover_index + 1)

        UseCases.move_document_pin(pinned_documents[self.current_popover_index], new_index)
        self.popup_at_index(new_index)

    def on_icon_button_click(self, button, icon_name):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()
        document_id = pinned_documents[self.current_popover_index]

        UseCases.set_pinned_document_icon(document_id, icon_name)

    def on_secondary_button_press(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        index = self.pin_buttons.index(controller.get_widget())
        self.popup_at_index(index)

        controller.reset()
        return True

    def pin_document(self, button=None, parameter=''):
        active_document_id = WorkspaceRepo.get_workspace().get_active_document_id()

        UseCases.pin_document(active_document_id)

        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()
        self.popup_at_index(len(pinned_documents) - 1)

    def unpin_document(self, button=None, parameter=''):
        active_document_id = WorkspaceRepo.get_workspace().get_active_document_id()

        UseCases.unpin_document(active_document_id)

    def popup_at_index(self, index):
        allocation = self.main_window.headerbar.hb_right.compute_bounds(self.main_window).out_bounds

        x = allocation.origin.x + 23 + 33 * index
        y = 40

        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()
        document_title = DocumentRepo.get_stub_by_id(pinned_documents[index])['title']
        self.current_popover_index = index
        self.popover.move_left_button.set_sensitive(self.current_popover_index != None and self.current_popover_index >= 1)
        self.popover.move_right_button.set_sensitive(self.current_popover_index != None and self.current_popover_index < len(pinned_documents) - 1)

        self.popover.unpin_button_label.set_label('Unpin "' + document_title + '"')
        UseCases.show_popover('pin_edit_menu', x, y, 'bottom')


