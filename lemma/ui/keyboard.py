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
from gi.repository import Gtk, Gdk, GLib

import time

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
from lemma.services.message_bus import MessageBus


class Keyboard():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.view = main_window.document_view
        self.content = self.view.content

        self.cursor_blink_time = Gtk.Settings.get_default().get_property('gtk_cursor_blink_time') / 1000
        self.cursor_blink_timeout = Gtk.Settings.get_default().get_property('gtk_cursor_blink_timeout')
        self.cursor_blink_reset = time.time()
        self.cursor_visible = True

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller.connect('key-pressed', self.on_keypress_content)
        self.key_controller.connect('key-released', self.on_keyrelease_content)
        self.view.content.add_controller(self.key_controller)

        self.im_context = Gtk.IMContextSimple()
        self.im_context.set_use_preedit(True)
        self.im_context.connect('commit', self.on_im_commit)
        self.im_context.connect('preedit-changed', self.on_preedit_changed)
        self.key_controller.set_im_context(self.im_context)

        self.content.connect('realize', self.on_realize)

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.focus_controller.connect('leave', self.on_focus_out)
        self.view.content.add_controller(self.focus_controller)

        MessageBus.subscribe(self, 'new_active_document')
        MessageBus.subscribe(self, 'document_ast_or_cursor_changed')

    def animate(self):
        messages = MessageBus.get_messages(self)

        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None:
            self.im_context.reset()

        if 'new_active_document' in messages or 'document_ast_or_cursor_changed' in messages:
            self.im_context.reset()

        time_since_blink_start = time.time() - self.cursor_blink_reset
        time_in_cycle = (time_since_blink_start % self.cursor_blink_time) / self.cursor_blink_time

        cursor_visible = True
        if time_since_blink_start <= 10 and time_in_cycle > 0.6:
            cursor_visible = False
        if not self.view.content.has_focus():
            cursor_visible = False
        if document != None and document.has_selection():
            cursor_visible = False

        if time_since_blink_start <= self.cursor_blink_timeout and cursor_visible != self.cursor_visible:
            self.cursor_visible = cursor_visible
            self.view.content.queue_draw()

    def on_keypress_content(self, controller, keyval, keycode, keyboard_state):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_shift_mask = int(Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)
        view_width, view_height = ApplicationState.get_view_size()

        ctrl_pressed = int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK or Gdk.keyval_name(keyval).startswith('Control')
        UseCases.set_ctrl_pressed(ctrl_pressed)

        if (widget := document.get_selected_widget()) != None:
            if self.application.widget_manager.on_keypress(widget, keyval, keycode, keyboard_state):
                return

        match (Gdk.keyval_name(keyval).lower(), int(keyboard_state & modifiers)):
            case ('left', 0):
                UseCases.left()
                UseCases.update_implicit_x_position()
            case ('right', 0):
                UseCases.right()
                UseCases.update_implicit_x_position()
            case ('up', 0):
                UseCases.up()
            case ('down', 0):
                UseCases.down()
            case ('home', 0):
                UseCases.paragraph_start()
                UseCases.update_implicit_x_position()
            case ('end', 0):
                UseCases.paragraph_end()
                UseCases.update_implicit_x_position()
            case ('page_up', 0):
                UseCases.page(-view_height + 100)
            case ('page_down', 0):
                UseCases.page(view_height - 100)

            case ('left', Gdk.ModifierType.SHIFT_MASK):
                UseCases.left(True)
            case ('right', Gdk.ModifierType.SHIFT_MASK):
                UseCases.right(True)
            case ('up', Gdk.ModifierType.SHIFT_MASK):
                UseCases.up(True)
            case ('down', Gdk.ModifierType.SHIFT_MASK):
                UseCases.down(True)
            case ('home', Gdk.ModifierType.SHIFT_MASK):
                UseCases.paragraph_start(True)
            case ('end', Gdk.ModifierType.SHIFT_MASK):
                UseCases.paragraph_end(True)
            case ('page_up', Gdk.ModifierType.SHIFT_MASK):
                UseCases.page(-view_height + 100, True)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK):
                UseCases.page(view_height - 100, True)

            case ('left', Gdk.ModifierType.CONTROL_MASK):
                UseCases.jump_left(False)
            case ('left', 5):
                UseCases.jump_left(True)
            case ('right', Gdk.ModifierType.CONTROL_MASK):
                UseCases.jump_right(False)
            case ('right', 5):
                UseCases.jump_right(True)

            case ('tab', 0):
                if document.has_multiple_lines_selected():
                    UseCases.change_indentation_level(1)
                elif not document.has_selection() and document.cursor_at_paragraph_start():
                    UseCases.change_indentation_level(1)
                else:
                    UseCases.select_next_placeholder()
            case ('iso_left_tab', Gdk.ModifierType.SHIFT_MASK):
                if document.has_multiple_lines_selected():
                    UseCases.change_indentation_level(-1)
                elif not document.has_selection() and document.cursor_at_paragraph_start():
                    UseCases.change_indentation_level(-1)
                else:
                    UseCases.select_prev_placeholder()
            case ('escape', _):
                if document.get_selected_widget() != None:
                    UseCases.remove_selection()
                    UseCases.update_implicit_x_position()
            case ('return', _) | ('kp_enter', _):
                if not document.has_selection() and document.get_insert_node().is_inside_link():
                    UseCases.open_link(document.get_insert_node().link)
                elif not document.has_selection():
                    insert_paragraph = document.get_insert_node().paragraph()
                    paragraph_style = insert_paragraph.style

                    if paragraph_style in ['ul', 'ol', 'cl'] and len(insert_paragraph) == 1:
                        UseCases.set_paragraph_style('p')
                        UseCases.set_indentation_level(0)
                    else:
                        UseCases.add_newline()
                        UseCases.update_implicit_x_position()
                else:
                    UseCases.add_newline()
                    UseCases.update_implicit_x_position()
            case ('backspace', _):
                UseCases.backspace()
                UseCases.update_implicit_x_position()
            case ('delete', _):
                UseCases.delete()
                UseCases.update_implicit_x_position()

            case _: return False
        return True

    def on_keyrelease_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_pressed = int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK and not Gdk.keyval_name(keyval).startswith('Control')
        UseCases.set_ctrl_pressed(ctrl_pressed)

    def on_im_commit(self, im_context, text):
        UseCases.im_commit(text)
        UseCases.update_implicit_x_position()
        self.application.autocomplete.on_keyboard_input()

    def on_preedit_changed(self, im_context):
        UseCases.set_preedit(self.im_context.get_preedit_string().str)

    def on_realize(self, content, data=None):
        self.reset_cursor_blink()

    def on_focus_in(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_pressed = int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK
        UseCases.set_ctrl_pressed(ctrl_pressed)

        self.reset_cursor_blink()
        self.im_context.focus_in()

    def on_focus_out(self, controller):
        self.im_context.focus_out()

    def reset_cursor_blink(self):
        self.cursor_blink_reset = time.time()


