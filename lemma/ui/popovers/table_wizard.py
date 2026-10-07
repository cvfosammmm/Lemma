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

from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView
from lemma.use_cases.use_cases import UseCases


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.add_css_class('table-wizard')
        self.set_width(206)

        self.size_hover = (-1, -1)
        self.buttons = dict()

        self.overlay = Gtk.Overlay()

        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_box.add_css_class('topbox')
        for i in range(1, 7):
            box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

            for j in range(1, 9):
                button = Gtk.Button()
                button.connect('clicked', self.on_button_clicked, (i, j))

                motion_controller = Gtk.EventControllerMotion()
                motion_controller.connect('enter', self.on_enter_button, (i, j))
                motion_controller.connect('leave', self.on_leave_button, (i, j))
                button.add_controller(motion_controller)

                self.buttons[(i, j)] = button
                box.append(button)

            button_box.append(box)

        self.buttons[(1, 1)].add_css_class('first-first')
        self.buttons[(1, 8)].add_css_class('first-last')
        self.buttons[(6, 1)].add_css_class('last-first')
        self.buttons[(6, 8)].add_css_class('last-last')

        self.overlay_label = Gtk.Label.new('')
        self.overlay_label.add_css_class('overlay')
        self.overlay_label.set_can_target(False)
        self.overlay.add_overlay(self.overlay_label)

        self.overlay.set_child(button_box)
        self.add_widget(self.overlay)

    def animate(self):
        for i in range(1, 7):
            for j in range(1, 9):
                if self.size_hover[0] >= i and self.size_hover[1] >= j:
                    self.buttons[(i, j)].add_css_class('hover')
                else:
                    self.buttons[(i, j)].remove_css_class('hover')
        if self.size_hover != (-1, -1):
            self.overlay_label.set_text(str(self.size_hover[0]) + ' x ' + str(self.size_hover[1]))
        else:
            self.overlay_label.set_text('')

    def on_popup(self):
        pass

    def on_popdown(self):
        pass

    def on_enter_button(self, controller, x, y, size):
        self.size_hover = size

    def on_leave_button(self, controller, size):
        if self.size_hover == size:
            self.size_hover = (-1, -1)

    def on_button_clicked(self, controller, size):
        UseCases.hide_popovers()
        UseCases.insert_table(size)


