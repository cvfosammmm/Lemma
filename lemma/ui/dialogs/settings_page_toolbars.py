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

from lemma.services.settings import Settings
from lemma.use_cases.use_cases import UseCases


class PageToolbars(object):

    def __init__(self, settings, main_window):
        self.settings = settings
        self.main_window = main_window

        self.button_list = []
        self.button_list.append([])
        self.button_list[-1].append(['bold-text-symbolic', 'button_visible_bold', 'Bold'])
        self.button_list[-1].append(['italic-text-symbolic', 'button_visible_italic', 'Italic'])
        self.button_list[-1].append(['highlight-text-symbolic', 'button_visible_highlight', 'Highlight'])
        self.button_list.append([])
        self.button_list[-1].append(['view-list-bullet-symbolic', 'button_visible_ul', 'Bullet List'])
        self.button_list[-1].append(['view-list-ordered-symbolic', 'button_visible_ol', 'Numbered List'])
        self.button_list[-1].append(['view-checklist-symbolic', 'button_visible_cl', 'Checklist'])
        self.button_list.append([])
        self.button_list[-1].append(['indent-less-symbolic', 'button_visible_decrease_indent', 'Decrease Indent'])
        self.button_list[-1].append(['indent-more-symbolic', 'button_visible_increase_indent', 'Increase Indent'])
        self.button_list.append([])
        self.button_list[-1].append(['insert-image-symbolic', 'button_visible_insert_image', 'Insert image'])
        self.button_list.append([])
        self.button_list[-1].append(['link-symbolic', 'button_visible_insert_link', 'Insert Link'])

        self.view = PageToolbarsView(self.button_list)

    def init(self):
        for i, section in enumerate(self.button_list):
            for item in section:
                self.view.checkboxes[item[1]].connect('toggled', self.on_checkbutton_toggled, item[1])
                self.view.checkboxes[item[1]].set_active(Settings.get_value(item[1]))

    def on_checkbutton_toggled(self, button, key):
        UseCases.settings_set_value(key, button.get_active())


class PageToolbarsView(Gtk.Box):

    def __init__(self, button_list):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('settings-page')
        self.get_style_context().add_class('settings-page-toolbars')

        self.checkboxes = dict()

        self.visible_buttons_header = Gtk.Label.new(_('Visible Buttons'))
        self.visible_buttons_header.add_css_class('settings-header')
        self.visible_buttons_header.set_xalign(0)
        self.visible_buttons_header.set_margin_top(21)
        self.visible_buttons_header.set_margin_bottom(20)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.set_margin_bottom(18)

        self.vbox.append(self.visible_buttons_header)

        for i, section in enumerate(button_list):
            for item in section:
                box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
                box.append(Gtk.Image.new_from_icon_name(_(item[0])))
                box.append(Gtk.Label.new(_(item[2])))

                checkbox = Gtk.CheckButton()
                checkbox.add_css_class('single')
                checkbox.set_child(box)

                self.vbox.append(checkbox)
                self.checkboxes[item[1]] = checkbox

            if not i == len(button_list) - 1:
                separator = Gtk.Separator()
                separator.set_halign(Gtk.Align.START)
                separator.set_hexpand(False)
                self.vbox.append(separator)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


