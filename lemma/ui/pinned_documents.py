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
import lemma.services.timer as timer


class PinnedDocuments():

    def __init__(self, main_window):
        self.main_window = main_window

        self.current_popover_index = None

        self.view = main_window.headerbar.hb_right.pin_buttons_box
        self.pin_buttons = self.view.pin_buttons

        for i, button in enumerate(self.pin_buttons):
            button.connect('clicked', self.on_pin_clicked, i)
            secondary_click_controller = Gtk.GestureClick()
            secondary_click_controller.set_button(3)
            secondary_click_controller.connect('pressed', self.on_secondary_button_press)
            button.add_controller(secondary_click_controller)

        self.view.context_menu.unpin_button.connect('clicked', self.on_unpin_button_click)

        wrapbox = self.view.context_menu.icon_wrapbox
        for icon_name in ['user-home-symbolic', 'folder-visiting-symbolic', 'inbox-symbolic', 'outbox-symbolic', 'audio-x-generic-symbolic', 'folder-download-symbolic', 'folder-pictures-symbolic', 'folder-saved-search-symbolic', 'folder-videos-symbolic', 'file-cabinet-symbolic', 'bear-symbolic', 'cat-sleeping-symbolic', 'cat-symbolic', 'cow-symbolic', 'dog-symbolic', 'horse-symbolic', 'leaf-symbolic', 'penguin-alt-symbolic', 'penguin-symbolic', 'seal-symbolic', 'sprout-symbolic', 'bug-symbolic', 'archive-symbolic', 'image-alt-symbolic', 'dice3-symbolic', 'theater-symbolic', 'cafe-symbolic', 'soup-symbolic', 'ink-tool-symbolic', 'online-symbolic', 'address-book-symbolic', 'meeting-symbolic', 'briefcase-symbolic', 'map-marker-symbolic', 'museum-symbolic', 'non-emergency-healthcare-symbolic', 'restaurant-symbolic', 'school-symbolic', 'pin-symbolic', 'view-grid-symbolic', 'mail-attachment-symbolic', 'emoji-symbols-symbolic', 'emoji-body-symbolic', 'applications-graphics-symbolic', 'applications-multimedia-symbolic', 'applications-games-symbolic', 'accessories-dictionary-symbolic', 'x-office-calendar-symbolic', 'star-large-symbolic', 'heart-filled-symbolic', 'editor-symbolic', 'library-symbolic', 'rescue-symbolic', 'globe-symbolic', 'bank-symbolic', 'shopping-cart-symbolic', 'body-symbolic', 'steps-symbolic', 'tag-outline-symbolic', 'text-x-generic-symbolic', 'lightbulb-symbolic', 'puzzle-piece-symbolic', 'people-symbolic', 'license-symbolic']:
            button = Gtk.Button.new_from_icon_name(icon_name)
            button.set_can_focus(False)
            button.add_css_class('flat')
            button.connect('clicked', self.on_icon_button_click, icon_name)
            wrapbox.append(button)

        self.view.context_menu.no_icon_button.connect('clicked', self.on_icon_button_click, None)

        MessageBus.subscribe(self, 'pinned_documents_changed')

        self.update()

    @timer.timer
    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'pinned_documents_changed' in messages:
            self.update()

    @timer.timer
    def update(self):
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
            button.set_sensitive(len(pinned_documents) > i)
            button.set_visible(len(pinned_documents) > i)

        self.view.set_visible(len(pinned_documents) > 0)

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

        self.view.context_menu.popover.popdown()
        UseCases.unpin_document(document_id)

    def on_icon_button_click(self, button, icon_name):
        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()
        document_id = pinned_documents[self.current_popover_index]

        UseCases.set_pinned_document_icon(document_id, icon_name)

    def on_secondary_button_press(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        button = controller.get_widget()
        allocation = button.compute_bounds(self.view).out_bounds

        rect = Gdk.Rectangle()
        rect.x = allocation.origin.x
        rect.y = allocation.origin.y + allocation.size.height
        rect.width = 1
        rect.height = 1

        workspace = WorkspaceRepo.get_workspace()
        pinned_documents = workspace.get_pinned_document_ids()
        i = self.pin_buttons.index(button)
        document_title = DocumentRepo.get_stub_by_id(pinned_documents[i])['title']
        self.current_popover_index = i

        self.view.context_menu.unpin_button_label.set_label('Unpin "' + document_title + '"')
        self.view.context_menu.popover.set_pointing_to(rect)
        self.view.context_menu.popover.popup()

        return True


