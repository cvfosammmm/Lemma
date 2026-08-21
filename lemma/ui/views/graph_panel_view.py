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


class GraphPanelView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('graph-panel')
        self.set_size_request(262, 280)

        self.headline = Gtk.Label.new('Graph View')
        self.headline.add_css_class('headline')
        self.headline.set_xalign(0)
        self.append(self.headline)

        self.content = GraphPanelDrawingArea()
        self.append(self.content)


class GraphPanelDrawingArea(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)

        self.set_vexpand(True)

        self.draw_func = lambda snapshot: None
        self.allocate_func = lambda width, height, baseline: None

    def set_draw_func(self, draw_func):
        self.draw_func = draw_func

    def set_allocate_func(self, allocate_func):
        self.allocate_func = allocate_func

    def do_snapshot(self, snapshot):
        self.draw_func(snapshot)

    def do_size_allocate(self, width, height, baseline):
        self.allocate_func(width, height, baseline)


