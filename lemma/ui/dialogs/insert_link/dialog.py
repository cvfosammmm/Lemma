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

from lemma.ui.dialogs.helpers.dialog_viewgtk import DialogView
from lemma.document.document import Document
from lemma.infrastructure.service_locator import ServiceLocator
from lemma.document.ast.services import ASTIterator, node_to_position, node_inside_link, get_link_bounds_by_node


class Dialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.document = None
        self.bounds = None
        self.current_values = dict()

    def run(self, document):
        self.document = document
        self.init_current_values()
        self.view = InsertLinkView(self.main_window)
        self.setup()

        if self.document.ast.has_selection():
            nodes = document.ast.get_subtree(*document.ast.get_cursor_state())
            first_node = nodes[0] if len(nodes) > 0 else None
            match_func = lambda x: (x != None and x.link != None and x.link == first_node.link)
            if len([node for node in nodes if match_func(node) == False]) > 0:
                self.bounds = None
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))
            else:
                self.bounds = document.ast.get_cursor_state()
                self.view.entry_link_target.set_text(first_node.link.target)
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Edit Link')))
        else:
            insert_node = self.document.ast.get_insert_node()
            if node_inside_link(insert_node):
                self.bounds = get_link_bounds_by_node(insert_node)
                self.view.entry_link_target.set_text(insert_node.link.target)
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Edit Link')))
            else:
                self.bounds = None
                self.view.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))

        self.validate()
        self.view.present()

    def init_current_values(self):
        self.current_values['link_target'] = ''

    def setup(self):
        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.add_button.connect('clicked', self.on_add_button_clicked)
        self.view.entry_link_target.connect('changed', self.on_entry_link_target_changed)
        self.view.entry_link_target.connect('activate', self.on_entry_link_target_activate)

    def on_entry_link_target_changed(self, entry):
        self.current_values['link_target'] = entry.get_text()
        self.validate()

    def on_entry_link_target_activate(self, entry):
        self.submit()

    def validate(self):
        self.view.add_button.set_sensitive(self.is_valid())

    def is_valid(self):
        return self.current_values['link_target'] != ''

    def on_cancel_button_clicked(self, button):
        self.view.close()

    def on_add_button_clicked(self, button):
        self.submit()

    def submit(self):
        if self.is_valid():
            self.document.add_command('add_link', self.current_values['link_target'], self.bounds)
            self.view.close()


class InsertLinkView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(400, -1)
        self.add_css_class('insert-link-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Insert Link')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.add_button = Gtk.Button.new_with_mnemonic(_('Insert'))
        self.add_button.set_can_focus(False)
        self.add_button.add_css_class('suggested-action')
        self.headerbar.pack_end(self.add_button)

        self.entry_link_target = Gtk.Entry()
        self.entry_link_target.set_placeholder_text(_('Link Target'))

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.append(self.entry_link_target)

        self.topbox.append(self.content)


