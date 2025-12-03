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

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.message_bus import MessageBus
from lemma.ui.views.context_menu import ContextMenu
from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView
import lemma.services.timer as timer


class ContextMenuDocument():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application

        self.view_right_click = ContextMenuDocumentView(main_window.document_view)
        self.view_edit_menu = application.popover_manager.popovers['edit_menu']

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'mode_set')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'document_changed' in messages or 'mode_set' in messages:
            self.update()

    @timer.timer
    def update(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        self.view_right_click.open_link_button.set_visible(document.cursor_inside_link())
        self.view_right_click.open_link_separator.set_visible(document.cursor_inside_link())
        self.view_right_click.copy_link_button.set_visible(document.whole_selection_is_one_link() or document.cursor_inside_link())
        self.view_right_click.remove_link_button.set_visible(document.links_inside_selection() or document.cursor_inside_link())
        self.view_right_click.edit_link_button.set_visible(document.whole_selection_is_one_link() or document.cursor_inside_link())
        self.view_right_click.link_buttons_separator.set_visible(document.links_inside_selection() or document.cursor_inside_link())
        hide_back_and_forward = document.links_inside_selection() or document.cursor_inside_link()
        self.view_right_click.back_button.set_visible(not hide_back_and_forward)
        self.view_right_click.forward_button.set_visible(not hide_back_and_forward)
        self.view_right_click.back_forward_separator.set_visible(not hide_back_and_forward)
        self.view_right_click.export_image_button.set_visible(document.widget_selected())
        self.view_right_click.image_functions_separator.set_visible(document.widget_selected())

        self.view_edit_menu.open_link_button.set_visible(document.cursor_inside_link())
        self.view_edit_menu.open_link_separator.set_visible(document.cursor_inside_link())
        self.view_edit_menu.copy_link_button.set_visible(document.whole_selection_is_one_link() or document.cursor_inside_link())
        self.view_edit_menu.remove_link_button.set_visible(document.links_inside_selection() or document.cursor_inside_link())
        self.view_edit_menu.edit_link_button.set_visible(document.whole_selection_is_one_link() or document.cursor_inside_link())
        self.view_edit_menu.link_buttons_separator.set_visible(document.links_inside_selection() or document.cursor_inside_link())
        self.view_edit_menu.export_image_button.set_visible(document.widget_selected())
        self.view_edit_menu.image_functions_separator.set_visible(document.widget_selected())

    def popup_at_cursor(self, x, y):
        self.view_right_click.popup_at_cursor(x, y)


class ContextMenuDocumentView(ContextMenu):

    def __init__(self, parent):
        ContextMenu.__init__(self)

        self.popover.set_parent(parent)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)

        self.open_link_button = self.create_button(_('Open Link'))
        self.open_link_button.set_action_name('win.open-link')
        self.box.append(self.open_link_button)

        self.open_link_separator = Gtk.Separator()
        self.box.append(self.open_link_separator)

        self.copy_link_button = self.create_button('Copy Link Target')
        self.copy_link_button.set_action_name('win.copy-link')
        self.box.append(self.copy_link_button)

        self.remove_link_button = self.create_button('Remove Link')
        self.remove_link_button.set_action_name('win.remove-link')
        self.box.append(self.remove_link_button)

        self.edit_link_button = self.create_button('Edit Link')
        self.edit_link_button.set_action_name('win.show-link-popover')
        self.box.append(self.edit_link_button)

        self.link_buttons_separator = Gtk.Separator()
        self.box.append(self.link_buttons_separator)

        self.back_button = self.create_button('Back', _('Alt') + '+Left Arrow')
        self.back_button.set_action_name('win.go-back')
        self.box.append(self.back_button)

        self.forward_button = self.create_button('Forward', _('Alt') + '+Right Arrow')
        self.forward_button.set_action_name('win.go-forward')
        self.box.append(self.forward_button)

        self.back_forward_separator = Gtk.Separator()
        self.box.append(self.back_forward_separator)

        self.export_image_button = self.create_button('Export Image...')
        self.export_image_button.set_action_name('win.export-image')
        self.box.append(self.export_image_button)

        self.image_functions_separator = Gtk.Separator()
        self.box.append(self.image_functions_separator)

        self.cut_button = self.create_button('Cut', _('Ctrl') + '+X')
        self.cut_button.set_action_name('win.cut')
        self.box.append(self.cut_button)

        self.copy_button = self.create_button('Copy', _('Ctrl') + '+C')
        self.copy_button.set_action_name('win.copy')
        self.box.append(self.copy_button)

        self.paste_button = self.create_button('Paste', _('Ctrl') + '+V')
        self.paste_button.set_action_name('win.paste')
        self.box.append(self.paste_button)

        self.delete_button = self.create_button('Delete')
        self.delete_button.set_action_name('win.delete')
        self.box.append(self.delete_button)

        self.box.append(Gtk.Separator())

        self.select_all_button = self.create_button('Select All', _('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.box.append(self.select_all_button)


class EditMenu(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.set_width(306)

        self.open_link_button = MenuBuilder.create_button(_('Open Link'))
        self.open_link_button.set_action_name('win.open-link')
        self.add_closing_button(self.open_link_button)

        self.open_link_separator = Gtk.Separator()
        self.add_widget(self.open_link_separator)

        self.copy_link_button = MenuBuilder.create_button(_('Copy Link Target'))
        self.copy_link_button.set_action_name('win.copy-link')
        self.add_closing_button(self.copy_link_button)

        self.remove_link_button = MenuBuilder.create_button(_('Remove Link'))
        self.remove_link_button.set_action_name('win.remove-link')
        self.add_closing_button(self.remove_link_button)

        self.edit_link_button = MenuBuilder.create_button(_('Edit Link'))
        self.edit_link_button.set_action_name('win.show-link-popover')
        self.add_closing_button(self.edit_link_button)

        self.link_buttons_separator = Gtk.Separator()
        self.add_widget(self.link_buttons_separator)

        self.export_image_button = MenuBuilder.create_button('Export Image...')
        self.export_image_button.set_action_name('win.export-image')
        self.add_closing_button(self.export_image_button)

        self.image_functions_separator = Gtk.Separator()
        self.add_widget(self.image_functions_separator)

        self.cut_button = MenuBuilder.create_button(_('Cut'), shortcut=_('Ctrl') + '+X')
        self.cut_button.set_action_name('win.cut')
        self.add_closing_button(self.cut_button)
        self.copy_button = MenuBuilder.create_button(_('Copy'), shortcut=_('Ctrl') + '+C')
        self.copy_button.set_action_name('win.copy')
        self.add_closing_button(self.copy_button)
        self.paste_button = MenuBuilder.create_button(_('Paste'), shortcut=_('Ctrl') + '+V')
        self.paste_button.set_action_name('win.paste')
        self.add_closing_button(self.paste_button)
        self.delete_button = MenuBuilder.create_button(_('Delete'))
        self.delete_button.set_action_name('win.delete')
        self.add_closing_button(self.delete_button)

        self.add_widget(Gtk.Separator())

        self.select_all_button = MenuBuilder.create_button(_('Select All'), shortcut=_('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.add_closing_button(self.select_all_button)

    def on_popup(self):
        pass

    def on_popdown(self):
        pass


