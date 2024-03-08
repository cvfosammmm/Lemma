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
from gi.repository import Gtk, Gdk, GLib

from lemma.popovers.popover_menu_builder import MenuBuilder
from lemma.popovers.popover_templates import PopoverTop


class Popover(object):

    def __init__(self, popover_manager):
        self.popover_manager = popover_manager
        self.view = View(popover_manager)


class View(PopoverTop):

    def __init__(self, popover_manager):
        PopoverTop.__init__(self, popover_manager)
        self.get_style_context().add_class('insert-symbols')

        self.set_width(330)

        self.up_button = Gtk.Button.new_from_icon_name('go-up-symbolic')
        self.up_button.get_style_context().add_class('flat')
        self.down_button = Gtk.Button.new_from_icon_name('go-down-symbolic')
        self.down_button.get_style_context().add_class('flat')

        self.header = Gtk.CenterBox()
        self.header.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.header.get_style_context().add_class('header')
        self.header_right = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        self.header_right.append(self.up_button)
        self.header_right.append(self.down_button)
        self.header.set_start_widget(Gtk.Label.new('Greek Letters'))
        self.header.set_end_widget(self.header_right)
        self.add_widget(self.header)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_row_spacing(1)
        self.flowbox.set_column_spacing(1)
        self.flowbox.set_max_children_per_line(7)

        self.symbols_list = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']
        for name in self.symbols_list:
            button = Gtk.Button.new_from_icon_name('sidebar-' + name + '-symbolic')
            button.set_action_name('win.insert-symbol')
            button.set_action_target_value(GLib.Variant('as', [name]))
            button.get_style_context().add_class('flat')
            button.connect('clicked', self.on_closing_button_click)
            self.flowbox.append(button)
        for i in range((- len(self.symbols_list)) % 7):
            self.flowbox.append(Gtk.Label.new(''))

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_child(self.flowbox)
        self.scrolled_window.set_size_request(-1, 280)
        self.add_widget(self.scrolled_window)


