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
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk
from gi.repository import Adw

from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView
from lemma.use_cases.use_cases import UseCases


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.set_width(260)

        self.icon_chooser_headline = Gtk.Label.new('Set Icon')
        self.icon_chooser_headline.add_css_class('icon-chooser-header')
        self.icon_chooser_headline.set_xalign(0)
        self.add_widget(self.icon_chooser_headline)

        self.icon_wrapbox = Adw.WrapBox()
        self.icon_wrapbox.set_line_spacing(0)
        self.icon_wrapbox.set_natural_line_length(272)

        self.add_widget(self.icon_wrapbox)

        self.no_icon_label = Gtk.Label.new('No Icon')
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_box.append(self.no_icon_label)

        self.no_icon_button = Gtk.Button()
        self.no_icon_button.set_can_focus(False)
        self.no_icon_button.set_child(button_box)
        self.no_icon_button.add_css_class('action')
        self.add_widget(self.no_icon_button)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.unpin_button_label = Gtk.Label.new('')
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_box.append(self.unpin_button_label)

        self.unpin_button = Gtk.Button()
        self.unpin_button.set_can_focus(False)
        self.unpin_button.set_child(button_box)
        self.unpin_button.add_css_class('action')

        self.add_widget(self.unpin_button)

    def on_popup(self):
        pass

    def on_popdown(self):
        pass


