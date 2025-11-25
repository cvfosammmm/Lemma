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

from lemma.ui.views.animated_paned import AnimatedVPaned


class NavigationSidebar(Gtk.Box):

    def __init__(self, document_list, backlinks):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('navbar')

        self.paned = AnimatedVPaned(document_list, backlinks, False)
        self.paned.set_vexpand(True)
        self.paned.set_wide_handle(False)

        self.backlinks_toggle = Gtk.ToggleButton()
        self.backlinks_toggle.set_tooltip_text(_('Backlinks'))
        self.backlinks_toggle.set_icon_name('backlinks-symbolic')
        self.backlinks_toggle.set_can_focus(False)
        self.backlinks_toggle.add_css_class('flat')

        self.toolbar = Gtk.ActionBar()
        self.toolbar.add_css_class('nav-toolbar')
        self.toolbar.pack_start(self.backlinks_toggle)

        self.append(self.paned)
        self.append(self.toolbar)


