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
from gi.repository import Gtk, Pango

from lemma.services.message_bus import MessageBus
from lemma.services.layout_info import LayoutInfo
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
from lemma.services.settings import Settings
from lemma.ui.shortcuts import Shortcuts
import lemma.services.timer as timer


class Toolbars():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.headerbar = main_window.headerbar
        self.toolbar = main_window.toolbar

        self.hamburger_button_controller = Gtk.GestureClick()
        self.hamburger_button_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.hamburger_button_controller.set_button(1)
        self.hamburger_button_controller.connect('pressed', self.on_hamburger_button_press)
        self.headerbar.hb_left.hamburger_menu_button.add_controller(self.hamburger_button_controller)

        self.bookmarks_button_controller = Gtk.GestureClick()
        self.bookmarks_button_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.bookmarks_button_controller.set_button(1)
        self.bookmarks_button_controller.connect('pressed', self.on_bookmarks_button_press)
        self.headerbar.hb_right.bookmarks_button.add_controller(self.bookmarks_button_controller)

        self.docmenu_button_controller = Gtk.GestureClick()
        self.docmenu_button_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.docmenu_button_controller.set_button(1)
        self.docmenu_button_controller.connect('pressed', self.on_docmenu_button_press)
        self.headerbar.hb_right.document_menu_button.add_controller(self.docmenu_button_controller)

        self.paragraph_button_controller = Gtk.GestureClick()
        self.paragraph_button_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.paragraph_button_controller.set_button(1)
        self.paragraph_button_controller.connect('pressed', self.on_paragraph_button_press)
        self.toolbar.toolbar_main.paragraph_style_menu_button.add_controller(self.paragraph_button_controller)

        self.edit_button_controller = Gtk.GestureClick()
        self.edit_button_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.edit_button_controller.set_button(1)
        self.edit_button_controller.connect('pressed', self.on_edit_button_press)
        self.toolbar.toolbar_right.edit_menu_button.add_controller(self.edit_button_controller)

        self.shortcut_controller = Shortcuts.new_controller()
        self.shortcut_controller.add_cb('show_hamburger_menu', self.on_hamburger_button_press)
        self.shortcut_controller.add_cb('show_document_menu', self.on_docmenu_button_press)
        self.shortcut_controller.add_cb('show_bookmarks', self.on_bookmarks_button_press)
        self.main_window.add_controller(self.shortcut_controller)

        MessageBus.subscribe(self, 'new_active_document')
        MessageBus.subscribe(self, 'document_ast_or_cursor_changed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'settings_changed')
        MessageBus.subscribe(self, 'tags_at_cursor_changed')
        MessageBus.subscribe(self, 'popover_changed')

        self.update_tag_toggle('bold')
        self.update_tag_toggle('italic')
        self.update_tag_toggle('verbatim')
        self.update_tag_toggle('highlight')
        self.update()
        self.update_paragraph_style()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'new_active_document' in messages or 'document_changed' in messages or 'settings_changed' in messages:
            self.update()
            self.update_paragraph_style()

        if 'tags_at_cursor_changed' in messages:
            self.update_tag_toggle('bold')
            self.update_tag_toggle('italic')
            self.update_tag_toggle('verbatim')
            self.update_tag_toggle('highlight')

        if 'popover_changed' in messages:
            popover = ApplicationState.get_popover()
            if popover != None: popover = popover[0]

            data = list()
            data.append((self.main_window.headerbar.hb_left.hamburger_menu_button, 'hamburger_menu'))
            data.append((self.main_window.headerbar.hb_right.bookmarks_button, 'bookmarks'))
            data.append((self.toolbar.toolbar_right.edit_menu_button, 'edit_menu'))
            data.append((self.toolbar.toolbar_main.paragraph_style_menu_button, 'paragraph_style'))
            data.append((self.main_window.headerbar.hb_right.document_menu_button, 'document_menu'))

            for button, name in data:
                if popover == name:
                    button.add_css_class('active')
                else:
                    button.remove_css_class('active')

    def on_hamburger_button_press(self, controller=None, n_press=None, x=None, y=None):
        button = self.main_window.headerbar.hb_left.hamburger_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds
        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        UseCases.show_popover('hamburger_menu', x, y, 'bottom')
        self.hamburger_button_controller.reset()

    def on_bookmarks_button_press(self, controller=None, n_press=None, x=None, y=None):
        button = self.main_window.headerbar.hb_right.bookmarks_button
        allocation = button.compute_bounds(self.main_window).out_bounds
        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        UseCases.show_popover('bookmarks', x, y, 'bottom')
        self.bookmarks_button_controller.reset()

    def on_edit_button_press(self, controller=None, n_press=None, x=None, y=None):
        button = self.toolbar.toolbar_right.edit_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds
        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y

        UseCases.show_popover('edit_menu', x, y, 'top')
        self.edit_button_controller.reset()

    def on_paragraph_button_press(self, controller=None, n_press=None, x=None, y=None):
        button = self.toolbar.toolbar_main.paragraph_style_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds
        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y

        UseCases.show_popover('paragraph_style', x, y, 'top')
        self.paragraph_button_controller.reset()

    def on_docmenu_button_press(self, controller=None, n_press=None, x=None, y=None):
        button = self.main_window.headerbar.hb_right.document_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds
        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        UseCases.show_popover('document_menu', x, y, 'bottom')
        self.docmenu_button_controller.reset()

    @timer.timer
    def update(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        cursor_inside_link = document.get_insert_node().is_inside_link()
        edit_link_visible = ((not document.has_selection()) and cursor_inside_link)

        if (widget := document.get_selected_widget()) != None and self.application.widget_manager.has_toolbar(widget):
            if self.toolbar.mode_stack.get_child_by_name(widget.get_type()) == None:
                self.toolbar.mode_stack.add_named(self.application.widget_manager.get_toolbar(widget), widget.get_type())

            self.toolbar.mode_stack.set_visible_child_name(widget.get_type())
            self.application.widget_manager.update_toolbar(widget)
        else:
            self.toolbar.mode_stack.set_visible_child_name('main')
            if edit_link_visible:
                self.toolbar.toolbar_main.insert_link_button.set_tooltip_text(_('Edit Link') + ' (' + Shortcuts.get_for_labels('link_popover') + ')')
            else:
                self.toolbar.toolbar_main.insert_link_button.set_tooltip_text(_('Insert Link') + ' (' + Shortcuts.get_for_labels('link_popover') + ')')

        self.update_button_visibility()

    def update_paragraph_style(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        current_node = document.get_first_selection_bound()
        paragraph_style_at_cursor = current_node.paragraph().style

        labels_dict = {'p': _('Normal'), 'h1': _('Heading 2'), 'h2': _('Heading 2'), 'h3': _('Heading 3'), 'h4': _('Heading 4'), 'h5': _('Heading 5'), 'h6': _('Heading 6'), 'ul': _('Bullet List'), 'ol': _('Numbered List'), 'cl': _('Checklist')}
        self.toolbar.toolbar_main.paragraph_style_menu_button_label.set_text(labels_dict[paragraph_style_at_cursor])

    def update_button_visibility(self):
        self.toolbar.toolbar_main.bold_button.set_visible(Settings.get_value('button_visible_bold'))
        self.toolbar.toolbar_main.italic_button.set_visible(Settings.get_value('button_visible_italic'))
        self.toolbar.toolbar_main.verbatim_button.set_visible(Settings.get_value('button_visible_verbatim'))
        self.toolbar.toolbar_main.highlight_button.set_visible(Settings.get_value('button_visible_highlight'))
        self.toolbar.toolbar_main.indent_less_button.set_visible(Settings.get_value('button_visible_decrease_indent'))
        self.toolbar.toolbar_main.indent_more_button.set_visible(Settings.get_value('button_visible_increase_indent'))
        self.toolbar.toolbar_main.ul_button.set_visible(Settings.get_value('button_visible_ul'))
        self.toolbar.toolbar_main.ol_button.set_visible(Settings.get_value('button_visible_ol'))
        self.toolbar.toolbar_main.cl_button.set_visible(Settings.get_value('button_visible_cl'))
        self.toolbar.toolbar_main.image_button.set_visible(Settings.get_value('button_visible_insert_image'))
        self.toolbar.toolbar_main.files_button.set_visible(Settings.get_value('button_visible_attach_files'))
        self.toolbar.toolbar_main.insert_link_button.set_visible(Settings.get_value('button_visible_insert_link'))

        tag_buttons_visible = Settings.get_value('button_visible_bold') or Settings.get_value('button_visible_italic') or Settings.get_value('button_visible_verbatim') or Settings.get_value('button_visible_highlight')
        self.toolbar.toolbar_main.tag_buttons_separator.set_visible(tag_buttons_visible)

        list_buttons_visible = Settings.get_value('button_visible_ul') or Settings.get_value('button_visible_ol') or Settings.get_value('button_visible_cl')
        self.toolbar.toolbar_main.list_buttons_separator.set_visible(list_buttons_visible)

        indentation_buttons_visible = Settings.get_value('button_visible_decrease_indent') or Settings.get_value('button_visible_increase_indent')
        self.toolbar.toolbar_main.indentation_buttons_separator.set_visible(indentation_buttons_visible)

        insert_buttons_visible = Settings.get_value('button_visible_insert_image') or Settings.get_value('button_visible_attach_files')
        self.toolbar.toolbar_main.insert_buttons_separator.set_visible(insert_buttons_visible)

        link_buttons_visible = Settings.get_value('button_visible_insert_link')
        self.toolbar.toolbar_main.link_buttons_separator.set_visible(link_buttons_visible)

    @timer.timer
    def update_tag_toggle(self, tagname):
        button_dict = {'bold': self.toolbar.toolbar_main.bold_button, 'italic': self.toolbar.toolbar_main.italic_button, 'verbatim': self.toolbar.toolbar_main.verbatim_button, 'highlight': self.toolbar.toolbar_main.highlight_button}
        button = button_dict[tagname]

        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        chars_selected = False
        all_tagged = True
        if document.has_selection():
            selected_nodes = document.get_selected_nodes()
            for node in (node for node in selected_nodes if node.type == 'char'):
                chars_selected = True
                if tagname not in node.tags:
                    all_tagged = False
                    break

        if chars_selected and all_tagged:
            button.add_css_class('checked')
        elif not chars_selected and tagname in ApplicationState.get_tags_at_cursor():
            button.add_css_class('checked')
        else:
            button.remove_css_class('checked')


