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

from lemma.services.message_bus import MessageBus
import lemma.ui.popovers.document_menu as document_menu
from lemma.ui.document_context_menu import EditMenu
import lemma.ui.popovers.hamburger_menu as hamburger_menu
import lemma.ui.popovers.paragraph_style as paragraph_style
import lemma.ui.popovers.link_autocomplete as link_autocomplete
import lemma.ui.popovers.pin_edit_menu as pin_edit_menu
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class PopoverManager():

    def __init__(self, main_window):
        self.current_popover_name = None
        self.prev_focus_widget = None
        self.main_window = main_window
        self.popoverlay = main_window.popoverlay
        self.inbetween = main_window.inbetween

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', self.on_click_inbetween)
        controller_click.set_button(1)
        self.inbetween.add_controller(controller_click)

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', self.on_click_inbetween)
        controller_click.set_button(3)
        self.inbetween.add_controller(controller_click)

        self.inbetween.set_can_target(False)

        self.popovers = dict()
        self.popovers["document_menu"] = document_menu.Popover()
        self.popovers["edit_menu"] = EditMenu()
        self.popovers["hamburger_menu"] = hamburger_menu.Popover()
        self.popovers["paragraph_style"] = paragraph_style.Popover()
        self.popovers["link_autocomplete"] = link_autocomplete.Popover()
        self.popovers["pin_edit_menu"] = pin_edit_menu.Popover()

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'mode_set')
        MessageBus.subscribe(self, 'app_state_changed')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'document_changed' in messages or 'mode_set' in messages or 'app_state_changed' in messages:
            self.update()

    @timer.timer
    def update(self):
        name = ApplicationState.get_value('active_popover')

        if name == None:
            self.popdown()
        else:
            if name != self.current_popover_name:
                self.popdown()

                x, y = ApplicationState.get_value('popover_position')
                orientation = ApplicationState.get_value('popover_orientation')
                self.popup(name, x, y, orientation)

    def popup(self, name, x, y, orientation):
        popover = self.popovers[name]
        popover.show_page(None, 'main', Gtk.StackTransitionType.NONE)

        window_width = self.main_window.get_width()
        window_height = self.main_window.get_height()
        arrow_width = 20
        if x - popover.width / 2 < 0:
            popover.set_margin_start(0)
            popover.arrow.set_margin_start(x - arrow_width / 2)
        elif x - popover.width / 2 > window_width - popover.width:
            popover.set_margin_start(window_width - popover.width)
            popover.arrow.set_margin_start(x - window_width + popover.width - arrow_width / 2)
        else:
            popover.set_margin_start(x - popover.width / 2)
            popover.arrow.set_margin_start(popover.width / 2 - arrow_width / 2)

        if orientation == 'bottom':
            popover.set_margin_bottom(0)
            popover.set_margin_top(max(0, y))

            popover.set_halign(Gtk.Align.START)
            popover.set_valign(Gtk.Align.START)

            popover.remove_css_class('popover-top')
            popover.add_css_class('popover-bottom')

            popover.arrow_box.set_valign(Gtk.Align.START)
            popover.arrow_box.set_halign(Gtk.Align.START)
            popover.add_overlay(popover.arrow_box)

        else:
            popover.set_margin_bottom(window_height - y)
            popover.set_margin_top(0)

            popover.set_halign(Gtk.Align.START)
            popover.set_valign(Gtk.Align.END)

            popover.remove_css_class('popover-bottom')
            popover.add_css_class('popover-top')

            popover.arrow_box.set_valign(Gtk.Align.END)
            popover.arrow_box.set_halign(Gtk.Align.START)
            popover.add_overlay(popover.arrow_box)

        if name != self.current_popover_name:
            self.remember_focus_widget()

        self.current_popover_name = name
        self.popoverlay.add_overlay(popover)
        self.inbetween.set_can_target(True)

        popover.grab_focus()
        popover.on_popup()

    def popdown(self):
        if self.current_popover_name == None: return

        name = self.current_popover_name
        popover = self.popovers[name]

        if popover.is_focus() or popover.get_focus_child() != None and self.prev_focus_widget != None:
            self.prev_focus_widget.grab_focus()
            self.prev_focus_widget = None

        self.popoverlay.remove_overlay(popover)
        self.current_popover_name = None
        self.inbetween.set_can_target(False)

        popover.on_popdown()

    def remember_focus_widget(self):
        widget = self.main_window
        while widget.get_focus_child() != None:
            widget = widget.get_focus_child()
        self.prev_focus_widget = widget

    def on_click_inbetween(self, controller, n_press, x, y):
        UseCases.hide_popovers()


