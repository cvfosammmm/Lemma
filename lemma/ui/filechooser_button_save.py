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
from gi.repository import Gtk, Pango, Gio

import os.path

from lemma.ui.observable import Observable


class FilechooserButtonView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.add_css_class('filechooser')

        self.icon = Gtk.Image.new_from_icon_name('filechooser-symbolic')
        self.icon.set_margin_start(1)
        self.icon.set_margin_end(12)
        self.append(self.icon)

        self.label = Gtk.Label()
        self.label.set_ellipsize(Pango.EllipsizeMode.START)
        self.label.set_margin_end(9)

        self.button_change = Gtk.Button()
        self.button_change.add_css_class('link')
        self.button_change.set_child(Gtk.Label.new(_('Change...')))

        self.label_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.label_box.append(self.label)
        self.label_box.append(Gtk.Label.new('('))
        self.label_box.append(self.button_change)
        self.label_box.append(Gtk.Label.new(')'))
        self.append(self.label_box)

        self.button_choose = Gtk.Button()
        self.button_choose.add_css_class('link')
        self.button_choose.set_child(Gtk.Label.new(_('Choose Filename...')))
        self.append(self.button_choose)


class FilechooserButton(Observable):

    def __init__(self, parent_window):
        Observable.__init__(self)

        self.parent_window = parent_window
        self.filename = None

        self.view = FilechooserButtonView()
        self.view.button_choose.connect('clicked', self.on_button_clicked)
        self.view.button_change.connect('clicked', self.on_button_clicked)

        self.view.button_choose.set_visible(True)
        self.view.label_box.set_visible(False)

        self.dialog = Gtk.FileDialog()
        self.dialog.set_modal(True)
        self.dialog.set_title(_('Choose File'))

    def reset(self):
        self.filename = None
        self.view.label.set_text('')
        self.view.button_choose.set_visible(True)
        self.view.label_box.set_visible(False)

    def get_filename(self):
        return self.filename

    def on_button_clicked(self, button):
        if self.filename != None:
            self.dialog.set_initial_folder(Gio.File.new_for_path(os.path.dirname(self.filename)))
            self.dialog.set_initial_name(os.path.basename(self.filename))
        self.dialog.save(self.parent_window, None, self.dialog_process_response)

    def dialog_process_response(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except Exception: pass
        else:
            if file != None:
                self.filename = file.get_path()
                self.view.label.set_text(self.filename)
                self.view.button_choose.set_visible(False)
                self.view.label_box.set_visible(True)
                self.add_change_code('file-set')


