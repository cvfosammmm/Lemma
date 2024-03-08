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

import os.path

from lemma.popovers.popover_button import PopoverButton
from lemma.app.service_locator import ServiceLocator


class PopoverManager():

    popovers = dict()
    popover_buttons = dict()
    current_popover_name = None
    main_window = None
    workspace = None
    popoverlay = None
    inbetween = Gtk.DrawingArea()

    connected_functions = dict() # observers' functions to be called when change codes are emitted

    def init(main_window, workspace):
        PopoverManager.main_window = main_window
        PopoverManager.workspace = workspace
        PopoverManager.popoverlay = main_window.popoverlay
        PopoverManager.popoverlay.add_overlay(PopoverManager.inbetween)

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', PopoverManager.on_click_inbetween)
        controller_click.set_button(1)
        PopoverManager.inbetween.add_controller(controller_click)

        PopoverManager.inbetween.set_can_target(False)

        for (path, directories, files) in os.walk(os.path.dirname(os.path.realpath(__file__))):
            if 'popover.py' in files:
                name = os.path.basename(path)
                exec('import lemma.popovers.' + name + '.popover as ' + name)
                exec('PopoverManager.popovers["' + name + '"] = ' + name + '.Popover(PopoverManager)')

    def create_popover_button(name):
        popover_button = PopoverButton(name, PopoverManager)
        PopoverManager.popover_buttons[name] = popover_button
        return popover_button

    def get_popover(name):
        if name in PopoverManager.popovers: return PopoverManager.popovers[name]
        else: return None

    def popup_at_button(name):
        popover = PopoverManager.get_popover(name)

        if popover == None: return
        if PopoverManager.current_popover_name == name: return
        if PopoverManager.current_popover_name != None: PopoverManager.popdown()

        button = PopoverManager.popover_buttons[name]
        allocation = button.compute_bounds(PopoverManager.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        window_width = PopoverManager.main_window.get_width()
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
        popover.view.set_margin_top(max(0, y))

        PopoverManager.current_popover_name = name
        PopoverManager.popoverlay.add_overlay(popover.view)
        PopoverManager.inbetween.set_can_target(True)

        popover.view.grab_focus()
        button.set_active(True)

        PopoverManager.add_change_code('popup', name)

    def popdown():
        if PopoverManager.current_popover_name == None: return

        name = PopoverManager.current_popover_name
        popover = PopoverManager.popovers[name]

        PopoverManager.popoverlay.remove_overlay(popover.view)
        PopoverManager.current_popover_name = None
        PopoverManager.inbetween.set_can_target(False)

        popover.view.show_page(None, 'main', Gtk.StackTransitionType.NONE)
        if name in PopoverManager.popover_buttons:
            PopoverManager.popover_buttons[name].set_active(False)

        PopoverManager.add_change_code('popdown', name)
        PopoverManager.main_window.document_view.scrolling_widget.content.grab_focus()

    def on_click_inbetween(controller, n_press, x, y):
        PopoverManager.popdown()

    def add_change_code(change_code, parameter=None):
        if change_code in PopoverManager.connected_functions:
            for callback in PopoverManager.connected_functions[change_code]:
                if parameter != None:
                    callback(parameter)
                else:
                    callback()

    def connect(change_code, callback):
        if change_code in PopoverManager.connected_functions:
            PopoverManager.connected_functions[change_code].add(callback)
        else:
            PopoverManager.connected_functions[change_code] = {callback}

    def disconnect(change_code, callback):
        if change_code in PopoverManager.connected_functions:
            PopoverManager.connected_functions[change_code].discard(callback)
            if len(PopoverManager.connected_functions[change_code]) == 0:
                del(PopoverManager.connected_functions[change_code])


