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
from gi.repository import Gtk, Gdk


class DocumentViewController():

    def __init__(self, document_view):
        self.document_view = document_view
        self.view = self.document_view.view
        self.content = self.view.content

        self.view.scrolling_widget.connect('primary_button_press', self.on_primary_button_press)

        self.key_controller_content = Gtk.EventControllerKey()
        self.key_controller_content.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_content.connect('key-pressed', self.on_keypress_content)
        self.content.add_controller(self.key_controller_content)

        self.im_context = Gtk.IMContextSimple()
        self.im_context.set_use_preedit(True)
        self.im_context.connect('commit', self.on_im_commit)
        self.key_controller_content.set_im_context(self.im_context)

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.focus_controller.connect('leave', self.on_focus_out)
        self.content.add_controller(self.focus_controller)

        self.view.scrolling_widget.connect('size_changed', self.on_size_change)
        self.view.scrolling_widget.connect('scrolling_offset_changed', self.on_scrolling_offset_change)
        self.view.scrolling_widget.connect('hover_state_changed', self.on_hover_state_changed)
        self.update_cursor()

    def on_primary_button_press(self, content, data):
        x, y, state = data

        if state == 0:
            x -= self.view.padding_left
            y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height

            if y < -self.view.subtitle_height:
                self.document_view.init_renaming()
            elif y > 0:
                self.document_view.document.add_command('click', x, y)
                self.content.grab_focus()

    def on_keypress_content(self, controller, keyval, keycode, state):
        if self.document_view.document == None: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()

        document = self.document_view.document
        match (Gdk.keyval_name(keyval).lower(), int(state & modifiers)):
            case ('left', 0): document.add_command('left')
            case ('right', 0): document.add_command('right')
            case ('up', 0): document.add_command('up')
            case ('down', 0): document.add_command('down')
            case ('home', 0): document.add_command('line_start')
            case ('end', 0): document.add_command('line_end')
            case ('page_up', 0): document.add_command('page_up', self.view.scrolling_widget.height)
            case ('page_down', 0): document.add_command('page_down', self.view.scrolling_widget.height)

            case ('left', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_left')
            case ('right', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_right')
            case ('up', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_up')
            case ('down', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_down')
            case ('home', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_line_start')
            case ('end', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_line_end')
            case ('page_up', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_page_up', self.view.scrolling_widget.height)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_page_down', self.view.scrolling_widget.height)

            case ('return', _): document.add_command('newline')
            case ('backspace', _): document.add_command('backspace')
            case ('delete', _): document.add_command('delete')

            case _: return False
        return True

    def on_im_commit(self, im_context, text):
        if self.document_view.document == None: return False

        self.document_view.document.add_command('im_commit', text)

    def on_focus_in(self, controller):
        self.im_context.focus_in()
        self.update_cursor()
        self.content.queue_draw()

    def on_focus_out(self, controller):
        self.im_context.focus_out()
        self.update_cursor()
        self.content.queue_draw()

    def on_hover_state_changed(self, widget):
        self.update_cursor()

    def on_size_change(self, *arguments):
        self.update_cursor()

    def on_scrolling_offset_change(self, *arguments):
        self.update_cursor()

    def update_cursor(self):
        widget = self.view.scrolling_widget
        x = widget.scrolling_offset_x + (widget.cursor_x if widget.cursor_x != None else 0)
        y = widget.scrolling_offset_y + (widget.cursor_y if widget.cursor_y != None else 0)

        if y < self.view.padding_top + self.view.title_height:
            self.content.set_cursor(self.view.mouse_cursor_text)
        elif y > self.view.padding_top + self.view.title_height + self.view.subtitle_height:
            self.content.set_cursor(self.view.mouse_cursor_text)
        else:
            self.content.set_cursor(self.view.mouse_cursor_default)


