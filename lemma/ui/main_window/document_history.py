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

from lemma.ui.main_window.scrolling_widget import ScrollingWidget


class DocumentHistoryView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.set_hexpand(True)
        self.add_css_class('history')

        self.scrolling_widget = ScrollingWidget()
        self.content = self.scrolling_widget.content
        self.set_child(self.scrolling_widget.view)


