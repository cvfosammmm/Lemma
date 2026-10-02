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


class KernelStateButton(Gtk.Button):

    def __init__(self):
        Gtk.Button.__init__(self)
        self.add_css_class('kernel-state')

        self.spinner = Gtk.Spinner()
        self.spinner.start()

        self.icon = Gtk.Image.new_from_icon_name('coding-menu-symbolic')

        self.overlay = Gtk.Overlay()
        self.overlay.set_child(self.spinner)
        self.overlay.add_overlay(self.icon)

        self.set_child(self.overlay)
        self.set_tooltip_text(_('Computation Menu'))

    def show_busy_state(self):
        self.add_css_class('busy')

    def show_idle_state(self):
        self.remove_css_class('busy')


