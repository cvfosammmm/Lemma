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

from lemma.ui.dialogs.dialog_view_action import DialogViewAction


class ExportBulkView(DialogViewAction):

    def __init__(self, main_window):
        DialogViewAction.__init__(self, main_window, _('Export Documents'), 500, 'export-bulk-dialog', _('Export'))

        self.filename_label = self.add_header_label('<b>' + _('Filename') + '</b>')
        self.filename_label.set_margin_bottom(1)
        self.file_chooser_button = self.add_file_chooser_button_save()
        self.file_chooser_button.dialog.set_initial_name('.zip')
        self.file_chooser_button.dialog.set_title(_('Choose File'))

        self.documents_label = self.add_header_label('<b>' + _('Documents to export') + '</b>')
        self.documents_label.set_margin_bottom(1)

        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.list)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_max_content_height(242)
        self.content.append(self.scrolled_window)

        self.select_all_button = Gtk.CheckButton.new_with_label(_('Select All'))
        self.select_all_button.add_css_class('select-all')
        self.content.append(self.select_all_button)


class Row(Gtk.ListBoxRow):

    def __init__(self, document):
        Gtk.ListBoxRow.__init__(self)
        self.set_activatable(False)

        self.document = document
        label = Gtk.Label.new(document.title)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_margin_end(12)
        self.button = Gtk.CheckButton()
        self.button.set_child(label)

        self.set_child(self.button)


