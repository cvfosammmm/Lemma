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

from lemma.dialogs.helpers.dialog_viewgtk import DialogView


class ImportDocumentsView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(400, -1)
        self.set_can_focus(False)
        self.get_style_context().add_class('import-markdown-files-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Import Markdown Files')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.import_button = Gtk.Button.new_with_mnemonic(_('Import'))
        self.import_button.set_can_focus(False)
        self.import_button.get_style_context().add_class('suggested-action')
        self.headerbar.pack_end(self.import_button)

        self.explainer = Gtk.Label()
        self.explainer.set_markup(_('<b>Warning:</b> This will not work with arbitrary .md-files. It\'s only supposed to work with files previously exported from Lemma.'))
        self.explainer.get_style_context().add_class('explainer')
        self.explainer.set_wrap(True)
        self.explainer.set_xalign(0)

        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list.set_sort_func(self.sort_function)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.list)

        self.drop_message_inner_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        image = Gtk.Image.new_from_icon_name('arrow1-down-symbolic')
        image.set_pixel_size(64)
        arrow_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        arrow_box.append(image)
        self.drop_message_inner_box.append(arrow_box)
        self.drop_message_inner_box.append(Gtk.Label.new('Drag and Drop .md-Files here'))

        self.drop_message_outer_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.drop_message_outer_box.get_style_context().add_class('drop-message')
        self.drop_message_outer_box.append(self.drop_message_inner_box)

        self.drop_stack = Gtk.Stack()
        self.drop_stack.add_named(self.drop_message_outer_box, 'message')
        self.drop_stack.add_named(self.scrolled_window, 'files')

        self.drop_controller = Gtk.DropTarget.new(GObject.TYPE_NONE, Gdk.DragAction.COPY)
        self.drop_controller.set_gtypes([Gdk.FileList])
        self.drop_stack.add_controller(self.drop_controller)

        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        button_box.append(Gtk.Image.new_from_icon_name('list-add-symbolic'))
        button_box.append(Gtk.Label.new('Add files...'))
        self.add_file_button = Gtk.Button()
        self.add_file_button.get_style_context().add_class('filechooser-button')
        self.add_file_button.get_style_context().add_class('flat')
        self.add_file_button.set_child(button_box)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.append(self.explainer)
        self.content.append(self.drop_stack)
        self.content.append(self.add_file_button)

        self.topbox.append(self.content)

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
        self.button.get_style_context().add_class('flat')
        box = Gtk.CenterBox()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        box.set_start_widget(Gtk.Label.new(path))
        box.set_end_widget(self.button)
        self.set_child(box)


