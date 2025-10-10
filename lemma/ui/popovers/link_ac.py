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
from gi.repository import Gtk, Gdk, GObject

import os

from lemma.ui.popovers.popover_templates import PopoverView
from lemma.document_repo.document_repo import DocumentRepo
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
import lemma.services.xml_helpers as xml_helpers


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.current_values = dict()
        self.bounds = None

        self.add_css_class('insert-link-popover')
        self.set_width(300)
        self.set_size_request(300, 260)

        self.add_button = Gtk.Button.new_from_icon_name('keyboard-enter-symbolic')
        self.add_button.add_css_class('flat')
        self.add_button.set_can_focus(False)

        self.entry_link_target = Gtk.Entry()
        self.entry_link_target.set_placeholder_text(_('Link Target'))
        self.entry_link_target.set_hexpand(True)

        self.entry_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.entry_wrapper.append(self.entry_link_target)
        self.entry_wrapper.append(self.add_button)

        self.listbox = Gtk.ListBox()
        self.listbox.set_activate_on_single_click(True)
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_can_focus(False)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.listbox)
        self.scrolled_window.set_vexpand(True)

        self.add_widget(self.entry_wrapper)
        self.add_widget(self.scrolled_window)

        self.add_button.connect('clicked', self.on_add_button_clicked)

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.entry_link_target.add_controller(self.key_controller)
        self.entry_link_target.connect('changed', self.on_entry_link_target_changed)
        self.entry_link_target.connect('activate', self.on_entry_link_target_activate)

        self.listbox.connect('row-activated', self.on_suggestion_row_activated)
        self.listbox.connect('selected-rows-changed', self.on_selected_rows_changed)

    def on_popup(self):
        UseCases.app_state_set_value('document_view_hide_cursor_on_unfocus', False)

        self.init_current_values()

        document = DocumentRepo.get_active_document()
        if document.cursor.has_selection():
            nodes = document.ast.get_subtree(*document.cursor.get_state())
            first_node = nodes[0] if len(nodes) > 0 else None
            match_func = lambda x: (x != None and x.link != None and x.link == first_node.link)
            if len([node for node in nodes if match_func(node) == False]) > 0:
                self.bounds = [document.cursor.get_insert_node(), document.cursor.get_selection_node()]
                self.entry_link_target.set_text('')
                self.add_button.set_tooltip_text(_('Insert Link'))
            else:
                self.bounds = [document.cursor.get_insert_node(), document.cursor.get_selection_node()]
                self.entry_link_target.set_text(first_node.link)
                self.add_button.set_tooltip_text(_('Edit Link'))
        else:
            self.bounds = None
            self.entry_link_target.set_text('')
            self.add_button.set_tooltip_text(_('Insert Link'))

        self.entry_link_target.grab_focus()
        self.update_list()

    def on_popdown(self):
        UseCases.app_state_set_value('document_view_hide_cursor_on_unfocus', True)

    def init_current_values(self):
        self.current_values['link_target'] = ''

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('Escape'):
            if state & modifiers == 0:
                UseCases.hide_popovers()
                return True

        if keyval == Gdk.keyval_from_name('Up'):
            if state & modifiers == 0:
                self.select_prev()
                return True

        if keyval == Gdk.keyval_from_name('Down'):
            if state & modifiers == 0:
                self.select_next()
                return True

        return False

    def select_next(self):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row == None:
            listbox.select_row(listbox.get_first_child())
        else:
            listbox.select_row(listbox.get_row_at_index(selected_row.get_index() + 1))

    def select_prev(self):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row == None:
            listbox.select_row(listbox.get_last_child())
        else:
            listbox.select_row(listbox.get_row_at_index(selected_row.get_index() - 1))

    def on_selected_rows_changed(self, listbox):
        listbox = self.listbox

        selected_row = listbox.get_selected_row()
        if selected_row != None:
            self.entry_link_target.get_buffer().set_text(selected_row.title, len(selected_row.title))
            self.entry_link_target.set_position(-1)

        adjustment = self.scrolled_window.get_vadjustment()
        if selected_row == None:
            adjustment.set_value(0)
        else:
            bounds = selected_row.compute_bounds(listbox).out_bounds
            item_height = bounds.size.height
            y = bounds.origin.y
            page_size = adjustment.get_page_size()
            offset = adjustment.get_value()
            if offset > y:
                adjustment.set_value(y)
            if offset < y + item_height - page_size:
                adjustment.set_value(y + item_height - page_size)

    def on_entry_link_target_changed(self, entry):
        self.current_values['link_target'] = entry.get_text()
        if self.listbox.get_selected_row() == None or (entry.get_text() != self.listbox.get_selected_row().title):
            self.update_list()

    def on_entry_link_target_activate(self, entry):
        self.submit()

    def on_suggestion_row_activated(self, listbox, row):
        self.entry_link_target.set_text(row.title)
        self.entry_link_target.set_position(-1)
        self.submit()

    def update_list(self):
        search_terms = self.entry_link_target.get_text().split()

        self.listbox.remove_all()
        for document_stub in DocumentRepo.list_by_terms_in_title(search_terms, limit=20):
            self.listbox.append(ACItem(document_stub['title']))

    def on_add_button_clicked(self, button):
        self.submit()

    def submit(self):
        document = DocumentRepo.get_active_document()

        if self.current_values['link_target'] != '':
            if self.bounds == None:
                tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
                text = xml_helpers.escape(self.current_values['link_target'])
                xml = xml_helpers.embellish_with_link_and_tags(text, text, tags_at_cursor)
                UseCases.insert_xml(xml)
                UseCases.animated_scroll_to_xy(*UseCases.get_insert_on_screen_scrolling_position())
            else:
                UseCases.set_link(document, self.bounds, self.current_values['link_target'])
        elif self.bounds != None:
            UseCases.set_link(document, self.bounds, None)

        UseCases.hide_popovers()


class ACItem(Gtk.ListBoxRow):

    def __init__(self, title):
        Gtk.ListBoxRow.__init__(self)
        self.set_size_request(-1, 30)

        self.title = title

        label = Gtk.Label.new(self.title)
        label.set_xalign(Gtk.Align.FILL)
        self.set_child(label)


