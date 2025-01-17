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

from lemma.ui.helpers.dialog_view import DialogView
from lemma.document.document import Document
from lemma.infrastructure.service_locator import ServiceLocator
from lemma.document.ast.node import Node
import lemma.infrastructure.xml_helpers as xml_helpers
import lemma.infrastructure.xml_parser as xml_parser


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.application = None
        self.workspace = None
        self.document = None
        self.bounds = None
        self.current_values = dict()
        self.search_terms = []

    def run(self, application, workspace, document):
        self.application = application
        self.workspace = workspace
        self.document = document
        self.use_cases = application.use_cases
        self.init_current_values()
        self.view = InsertLinkView(self.main_window)
        self.setup()

        if self.document.cursor.has_selection():
            nodes = document.ast.get_subtree(*document.cursor.get_state())
            first_node = nodes[0] if len(nodes) > 0 else None
            match_func = lambda x: (x != None and x.link != None and x.link == first_node.link)
            if len([node for node in nodes if match_func(node) == False]) > 0:
                self.bounds = [document.cursor.get_insert_node(), document.cursor.get_selection_node()]
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))
                self.view.add_button.set_label(_('Insert'))
            else:
                self.bounds = [document.cursor.get_insert_node(), document.cursor.get_selection_node()]
                self.view.entry_link_target.set_text(first_node.link.target)
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Edit Link')))
                self.view.add_button.set_label(_('Edit'))
        else:
            insert_node = self.document.cursor.get_insert_node()
            if insert_node.is_inside_link():
                self.bounds = insert_node.link_bounds()
                self.view.entry_link_target.set_text(insert_node.link.target)
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Edit Link')))
                self.view.add_button.set_label(_('Edit'))
            else:
                self.bounds = None
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))
                self.view.add_button.set_label(_('Insert'))

        self.validate()
        self.view.present()

    def init_current_values(self):
        self.current_values['link_target'] = ''

    def setup(self):
        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.add_button.connect('clicked', self.on_add_button_clicked)
        self.view.entry_link_target.connect('changed', self.on_entry_link_target_changed)
        self.view.entry_link_target.connect('activate', self.on_entry_link_target_activate)
        self.view.listbox.connect('row-activated', self.on_suggestion_row_activated)
        self.search_terms = self.view.entry_link_target.get_text().split()

    def on_entry_link_target_changed(self, entry):
        self.search_terms = entry.get_text().split()
        self.current_values['link_target'] = entry.get_text()
        self.validate()

    def on_entry_link_target_activate(self, entry):
        self.submit()

    def on_suggestion_row_activated(self, listbox, row):
        self.view.entry_link_target.set_text(row.title)
        self.view.entry_link_target.set_position(-1)

    def validate(self):
        line_height = 30
        count = 0

        self.view.listbox.remove_all()
        for document in self.workspace.documents:
            if self.is_match(document):
                self.view.listbox.append(ACItem(document.title))
                count += 1

        self.view.scrolled_window.set_visible(count > 0)
        self.view.set_default_size(400, (105 if count > 0 else 93) + min(count, 5) * line_height)
        self.view.add_button.set_sensitive(self.is_valid())

    def is_valid(self):
        return self.current_values['link_target'] != ''

    def is_match(self, document):
        if len(self.search_terms) == 0: return True
        return min(map(lambda x: x.lower() in document.title.lower(), self.search_terms))

    def on_cancel_button_clicked(self, button):
        self.view.close()

    def on_add_button_clicked(self, button):
        self.submit()

    def submit(self):
        if self.is_valid():
            if self.bounds == None:
                tags_at_cursor = self.application.cursor_state.tags_at_cursor
                text = xml_helpers.escape(self.current_values['link_target'])
                xml = '<char tags="' + ' '.join(tags_at_cursor) + '" link_target="' + text + '">' + text + '</char>'
                self.use_cases.insert_xml(xml)
            else:
                self.document.add_command('set_link', self.bounds, self.current_values['link_target'])
            self.view.close()


class InsertLinkView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_resizable(False)
        self.set_default_size(400, -1)
        self.add_css_class('insert-link-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.add_button = Gtk.Button.new_with_label(_('Insert'))
        self.add_button.set_can_focus(False)
        self.add_button.add_css_class('suggested-action')
        self.headerbar.pack_end(self.add_button)

        self.entry_link_target = Gtk.Entry()
        self.entry_link_target.set_placeholder_text(_('Link Target'))

        self.listbox = Gtk.ListBox()
        self.listbox.set_activate_on_single_click(True)
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.set_can_focus(False)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.listbox)
        self.scrolled_window.set_vexpand(True)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.append(self.entry_link_target)
        self.content.append(self.scrolled_window)

        self.topbox.append(self.content)


class ACItem(Gtk.ListBoxRow):

    def __init__(self, title):
        Gtk.ListBoxRow.__init__(self)
        self.set_size_request(-1, 30)

        self.title = title

        label = Gtk.Label.new(self.title)
        label.set_xalign(Gtk.Align.FILL)
        self.set_child(label)


