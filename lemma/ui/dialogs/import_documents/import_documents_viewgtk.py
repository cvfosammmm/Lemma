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
from gi.repository import Gtk, GLib, Gdk, GObject

import os

from lemma.ui.helpers.dialog_view_action import DialogViewAction


class ImportDocumentsView(DialogViewAction):

    def __init__(self, main_window):
        DialogViewAction.__init__(self, main_window, _('Import Markdown Files'), 500, 'import-markdown-files-dialog', _('Import'))

        self.explainer = self.add_explainer_label(_('<b>Warning:</b> This will not work with arbitrary .md-files. It\'s only supposed to work with files previously exported from Lemma.'))

        self.list_label = self.add_header_label('<b>' + _('Files to import') + '</b>')
        self.list_label.set_margin_bottom(1)

        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list.set_sort_func(self.sort_function)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.list)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_max_content_height(242)

        self.drop_message_inner_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        image = Gtk.Image.new_from_icon_name('arrow1-down-symbolic')
        image.set_pixel_size(64)
        arrow_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        arrow_box.append(image)
        self.drop_message_inner_box.append(arrow_box)
        self.drop_message_inner_box.append(Gtk.Label.new('Drag and Drop .md-Files here'))

        self.drop_message_outer_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.drop_message_outer_box.add_css_class('drop-message')
        self.drop_message_outer_box.append(self.drop_message_inner_box)

        self.drop_stack = Gtk.Stack()
        self.drop_stack.add_named(self.drop_message_outer_box, 'message')
        self.drop_stack.add_named(self.scrolled_window, 'files')
        self.drop_controller = Gtk.DropTarget.new(GObject.TYPE_NONE, Gdk.DragAction.COPY)
        self.drop_controller.set_gtypes([Gdk.FileList])
        self.drop_stack.add_controller(self.drop_controller)
        self.content.append(self.drop_stack)

        self.add_file_button = Gtk.Button.new_with_label(_('Add files...'))
        self.add_file_button.add_css_class('add-file-button')
        self.add_file_button.add_css_class('link')

        self.button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.button_box.add_css_class('button-box')
        self.button_box.append(Gtk.Image.new_from_icon_name('list-add-symbolic'))
        self.button_box.append(self.add_file_button)
        self.content.append(self.button_box)

    def sort_function(self, row1, row2, user_data=None):
        val1 = row1.path.lower()
        val2 = row2.path.lower()

        if val1 > val2:
            return 1
        elif  val1 == val2:
            return 0
        elif val1 < val2:
            return -1


class Row(Gtk.ListBoxRow):

    def __init__(self, path):
        Gtk.ListBoxRow.__init__(self)
        self.set_activatable(False)

        self.path = path

        self.button = Gtk.Button.new_from_icon_name('user-trash-symbolic')
        self.button.add_css_class('flat')
        box = Gtk.CenterBox()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        box.set_start_widget(Gtk.Label.new(path))
        box.set_end_widget(self.button)
        self.set_child(box)


