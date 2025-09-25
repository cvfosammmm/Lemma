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
from gi.repository import Gtk, Gdk, Graphene

import os, shutil

from lemma.services.color_manager import ColorManager
from lemma.services.paths import Paths
import lemma.services.timer as timer


class PageStorage(object):

    def __init__(self, settings, main_window):
        self.view = PageStorageView()
        self.settings = settings
        self.main_window = main_window

    @timer.timer
    def init(self):
        self.view.folder_label.set_text(Paths.get_notes_folder())

        lemma_disk_space = sum([file.stat().st_size for file in os.scandir(Paths.get_notes_folder())])
        total_disk_space, used_disk_space, free_disk_space = shutil.disk_usage(Paths.get_notes_folder())
        system_disk_space = used_disk_space - lemma_disk_space

        self.view.disk_used_label.set_text('{0:.2f} GB Used'.format(used_disk_space / 1024 / 1024 / 1024))
        self.view.disk_total_label.set_text('{0:.2f} GB Total'.format(total_disk_space / 1024 / 1024 / 1024))

        fraction_others = system_disk_space / total_disk_space
        fraction_lemma = lemma_disk_space / total_disk_space
        self.view.storage_scale.set_fractions(fraction_others, fraction_others + fraction_lemma)

        if lemma_disk_space > 1024 * 1024 * 1024:
            self.view.lemma_size.set_text('{0:.2f} GB'.format(lemma_disk_space / 1024 / 1024 / 1024))
        else:
            self.view.lemma_size.set_text('{0:.2f} MB'.format(lemma_disk_space / 1024 / 1024))

        if system_disk_space > 1024 * 1024 * 1024:
            self.view.system_size.set_text('{0:.2f} GB'.format(system_disk_space / 1024 / 1024 / 1024))
        else:
            self.view.system_size.set_text('{0:.2f} MB'.format(system_disk_space / 1024 / 1024))

        if free_disk_space > 1024 * 1024 * 1024:
            self.view.freespace_size.set_text('{0:.2f} GB'.format(free_disk_space / 1024 / 1024 / 1024))
        else:
            self.view.freespace_size.set_text('{0:.2f} MB'.format(free_disk_space / 1024 / 1024))


class PageStorageView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('settings-page')

        self.folder_header = Gtk.Label.new(_('Data Folder'))
        self.folder_header.add_css_class('settings-header')
        self.folder_header.set_xalign(0)
        self.folder_header.set_margin_top(21)

        self.folder_label = Gtk.Label()
        self.folder_label.add_css_class('settings-text-data-display')
        self.folder_label.set_xalign(0)
        self.folder_label.set_margin_top(18)

        self.disk_use_header = Gtk.Label.new(_('Disk Use'))
        self.disk_use_header.add_css_class('settings-header')
        self.disk_use_header.set_xalign(0)
        self.disk_use_header.set_margin_top(36)

        self.disk_used_label = Gtk.Label()
        self.disk_used_label.set_xalign(0)

        self.disk_total_label = Gtk.Label()
        self.disk_total_label.set_xalign(1)
        self.disk_total_label.set_hexpand(True)

        self.disk_scale_labels_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.disk_scale_labels_box.add_css_class('settings-margin-box')
        self.disk_scale_labels_box.set_hexpand(True)
        self.disk_scale_labels_box.set_margin_top(18)
        self.disk_scale_labels_box.append(self.disk_used_label)
        self.disk_scale_labels_box.append(self.disk_total_label)

        self.lemma_colorcode = Gtk.DrawingArea()
        self.lemma_colorcode.add_css_class('settings-colorcode')
        self.lemma_colorcode.add_css_class('settings-color-lemma')

        self.lemma_label = Gtk.Label.new('Lemma')
        self.lemma_label.set_xalign(0)

        self.lemma_size = Gtk.Label()
        self.lemma_size.set_xalign(1)
        self.lemma_size.set_hexpand(True)

        self.storage_scale = StorageScale()
        self.storage_scale.set_margin_top(6)

        self.separator = Gtk.Separator()
        self.separator.add_css_class('settings-margin-box')
        self.separator.set_margin_top(18)

        self.lemma_space_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.lemma_space_box.add_css_class('settings-margin-box')
        self.lemma_space_box.set_hexpand(True)
        self.lemma_space_box.set_margin_top(18)
        self.lemma_space_box.append(self.lemma_colorcode)
        self.lemma_space_box.append(self.lemma_label)
        self.lemma_space_box.append(self.lemma_size)

        self.system_colorcode = Gtk.DrawingArea()
        self.system_colorcode.add_css_class('settings-colorcode')
        self.system_colorcode.add_css_class('settings-color-system')

        self.system_label = Gtk.Label.new('System')
        self.system_label.set_xalign(0)

        self.system_size = Gtk.Label()
        self.system_size.set_xalign(1)
        self.system_size.set_hexpand(True)

        self.system_space_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.system_space_box.add_css_class('settings-margin-box')
        self.system_space_box.set_hexpand(True)
        self.system_space_box.set_margin_top(18)
        self.system_space_box.append(self.system_colorcode)
        self.system_space_box.append(self.system_label)
        self.system_space_box.append(self.system_size)

        self.freespace_colorcode = Gtk.DrawingArea()
        self.freespace_colorcode.add_css_class('settings-colorcode')
        self.freespace_colorcode.add_css_class('settings-color-freespace')

        self.freespace_label = Gtk.Label.new('Free Space')
        self.freespace_label.set_xalign(0)

        self.freespace_size = Gtk.Label()
        self.freespace_size.set_xalign(1)
        self.freespace_size.set_hexpand(True)

        self.freespace_space_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.freespace_space_box.add_css_class('settings-margin-box')
        self.freespace_space_box.set_hexpand(True)
        self.freespace_space_box.set_margin_top(18)
        self.freespace_space_box.append(self.freespace_colorcode)
        self.freespace_space_box.append(self.freespace_label)
        self.freespace_space_box.append(self.freespace_size)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.append(self.folder_header)
        self.vbox.append(self.folder_label)
        self.vbox.append(self.disk_use_header)
        self.vbox.append(self.disk_scale_labels_box)
        self.vbox.append(self.storage_scale)
        self.vbox.append(self.separator)
        self.vbox.append(self.lemma_space_box)
        self.vbox.append(self.system_space_box)
        self.vbox.append(self.freespace_space_box)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


class StorageScale(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)
        self.add_css_class('storage-scale')
        self.set_hexpand(True)

        self.fractions = (0.33, 0.66)

        self.width = 0
        self.height = 0

    def set_fractions(self, fraction_1, fraction_2):
        self.fractions = (fraction_1, fraction_2)
        self.queue_draw()

    def do_snapshot(self, snapshot):
        ctx = snapshot.append_cairo(Graphene.Rect().init(0, 0, self.width, self.height))

        color_system = ColorManager.get_ui_color('storage_color_system')
        color_lemma = ColorManager.get_ui_color('storage_color_lemma')
        color_free = ColorManager.get_ui_color('storage_color_free')

        offset_1 = min(max(2, self.fractions[0] * self.width), self.width)
        offset_2 = min(max(offset_1 + 2, self.fractions[1] * self.width), self.width)

        Gdk.cairo_set_source_rgba(ctx, color_system)
        ctx.rectangle(0, 0, offset_1, self.height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, color_lemma)
        ctx.rectangle(offset_1, 0, offset_2, self.height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, color_free)
        ctx.rectangle(offset_2, 0, self.width, self.height)
        ctx.fill()

    def do_size_allocate(self, width, height, baseline):
        self.width = width
        self.height = height


