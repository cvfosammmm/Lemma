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

import lemma.commands.commands as commands


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
                self.document_view.document.command_processor.add_command(commands.Click(x, y))
                self.content.grab_focus()

    def on_keypress_content(self, controller, keyval, keycode, state):
        if self.document_view.document == None: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()

        command = None
        match (Gdk.keyval_name(keyval).lower(), int(state & modifiers)):
            case ('left', 0): command = commands.Left(1)
            case ('right', 0): command = commands.Right(1)
            case ('up', 0): command = commands.Up()
            case ('down', 0): command = commands.Down()

            case ('home', 0): command = commands.LineStart()
            case ('end', 0): command = commands.LineEnd()

            case ('return', _): command = commands.Return()
            case ('backspace', _): command = commands.Backspace()
            case ('delete', _): command = commands.Delete()

            case _: return False
        if command != None:
            self.document_view.document.command_processor.add_command(command)
        return True

    def on_im_commit(self, im_context, text):
        if self.document_view.document == None: return False

        self.document_view.document.command_processor.add_command(commands.IMCommit(text))

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


