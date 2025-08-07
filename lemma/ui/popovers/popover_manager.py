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

import lemma.ui.popovers.document_menu as document_menu
import lemma.ui.popovers.edit_menu as edit_menu
import lemma.ui.popovers.hamburger_menu as hamburger_menu
import lemma.ui.popovers.paragraph_style as paragraph_style
import lemma.ui.popovers.link_ac as link_ac
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases


class PopoverManager():

    def __init__(self, main_window, model_state):
        self.current_popover_name = None
        self.prev_focus_widget = None
        self.model_state = model_state
        self.main_window = main_window
        self.popoverlay = main_window.popoverlay
        self.inbetween = main_window.inbetween

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', self.on_click_inbetween)
        controller_click.set_button(1)
        self.inbetween.add_controller(controller_click)
        self.inbetween.set_can_target(False)

        self.popovers = dict()
        self.popovers["document_menu"] = document_menu.Popover(self.model_state)
        self.popovers["edit_menu"] = edit_menu.Popover(self.model_state)
        self.popovers["hamburger_menu"] = hamburger_menu.Popover(self.model_state)
        self.popovers["paragraph_style"] = paragraph_style.Popover(self.model_state)
        self.popovers["link_ac"] = link_ac.Popover(self.model_state)

    def update(self):
        for popover in self.popovers.values(): popover.update()

        name = ApplicationState.get_value('active_popover')

        if self.current_popover_name == name: return
        if self.current_popover_name != None: self.popdown()
        if name == None: return

        x, y = ApplicationState.get_value('popover_position')
        orientation = ApplicationState.get_value('popover_orientation')
        self.popup(name, x, y, orientation)

    def popup(self, name, x, y, orientation):
        popover = self.popovers[name]
        popover.view.show_page(None, 'main', Gtk.StackTransitionType.NONE)

        window_width = self.main_window.get_width()
        window_height = self.main_window.get_height()
        arrow_width = 20
        if x - popover.view.width / 2 < 0:
            popover.view.set_margin_start(0)
            popover.view.arrow.set_margin_start(x - arrow_width / 2)
        elif x - popover.view.width / 2 > window_width - popover.view.width:
            popover.view.set_margin_start(window_width - popover.view.width)
            popover.view.arrow.set_margin_start(x - window_width + popover.view.width - arrow_width / 2)
        else:
            popover.view.set_margin_start(x - popover.view.width / 2)
            popover.view.arrow.set_margin_start(popover.view.width / 2 - arrow_width / 2)

        if orientation == 'bottom':
            popover.view.set_margin_bottom(0)
            popover.view.set_margin_top(max(0, y))

            popover.view.set_halign(Gtk.Align.START)
            popover.view.set_valign(Gtk.Align.START)

            popover.view.remove_css_class('popover-top')
            popover.view.add_css_class('popover-bottom')

            popover.view.arrow_box.set_valign(Gtk.Align.START)
            popover.view.arrow_box.set_halign(Gtk.Align.START)
            popover.view.add_overlay(popover.view.arrow_box)

        else:
            popover.view.set_margin_bottom(window_height - y)
            popover.view.set_margin_top(0)

            popover.view.set_halign(Gtk.Align.START)
            popover.view.set_valign(Gtk.Align.END)

            popover.view.remove_css_class('popover-bottom')
            popover.view.add_css_class('popover-top')

            popover.view.arrow_box.set_valign(Gtk.Align.END)
            popover.view.arrow_box.set_halign(Gtk.Align.START)
            popover.view.add_overlay(popover.view.arrow_box)

        self.remember_focus_widget()
        self.current_popover_name = name
        self.popoverlay.add_overlay(popover.view)
        self.inbetween.set_can_target(True)

        popover.view.grab_focus()
        popover.on_popup()

    def popdown(self):
        if self.current_popover_name == None: return

        name = self.current_popover_name
        popover = self.popovers[name]

        self.popoverlay.remove_overlay(popover.view)
        self.current_popover_name = None
        self.inbetween.set_can_target(False)

        popover.on_popdown()

        if self.prev_focus_widget != None:
            self.prev_focus_widget.grab_focus()
            self.prev_focus_widget = None

    def remember_focus_widget(self):
        widget = self.main_window
        while widget.get_focus_child() != None:
            widget = widget.get_focus_child()
        self.prev_focus_widget = widget

    def on_click_inbetween(self, controller, n_press, x, y):
        UseCases.hide_popovers()


