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

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.ui.shortcuts import Shortcuts
from lemma.use_cases.use_cases import UseCases
from lemma.services.message_bus import MessageBus


class KeyboardInput():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.view = main_window.document_view
        self.content = self.view.content
        self.actions = self.application.actions.actions

        self.ctrl_pressed = False

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller.connect('key-pressed', self.on_keypress_content)
        self.key_controller.connect('key-released', self.on_keyrelease_content)
        self.view.content.add_controller(self.key_controller)

        self.im_context = Gtk.IMContextSimple()
        self.im_context.set_use_preedit(True)
        self.im_context.connect('commit', self.on_im_commit)
        self.key_controller.set_im_context(self.im_context)

        self.shortcut_controller = Shortcuts.new_controller()
        self.shortcut_controller.add_cb('toggle_bold', self.actions['toggle-bold'].activate)
        self.shortcut_controller.add_cb('toggle_italic', self.actions['toggle-italic'].activate)
        self.shortcut_controller.add_cb('toggle_verbatim', self.actions['toggle-verbatim'].activate)
        self.shortcut_controller.add_cb('toggle_highlight', self.actions['toggle-highlight'].activate)
        self.shortcut_controller.add_cb('link_popover', self.actions['show-link-popover'].activate)
        self.shortcut_controller.add_cb('subscript', self.actions['subscript'].activate)
        self.shortcut_controller.add_cb('superscript', self.actions['superscript'].activate)
        self.shortcut_controller.add_cb('toggle_checkbox', self.actions['toggle-checkbox'].activate)
        self.shortcut_controller.add_cb('undo', self.actions['undo'].activate)
        self.shortcut_controller.add_cb('redo', self.actions['redo'].activate)
        self.shortcut_controller.add_cb('cut', self.actions['cut'].activate)
        self.shortcut_controller.add_cb('copy', self.actions['copy'].activate)
        self.shortcut_controller.add_cb('paste', self.actions['paste'].activate)
        self.shortcut_controller.add_cb('select_all', self.actions['select-all'].activate)
        self.shortcut_controller.add_cb('go_to_parent_node', UseCases.move_cursor_to_parent)
        self.shortcut_controller.add_cb('extend_selection', UseCases.extend_selection)
        self.shortcut_controller.add_cb('rename_document', self.actions['rename-document'].activate)
        for para_style in ['h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl', 'p']:
            sc_name = 'paragraph_style_' + para_style
            callback = self.actions['set-paragraph-style'].activate
            self.shortcut_controller.add_cb(sc_name, callback, GLib.Variant.new_string(para_style))
        self.view.content.add_controller(self.shortcut_controller)

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.focus_controller.connect('leave', self.on_focus_out)
        self.view.content.add_controller(self.focus_controller)

        MessageBus.subscribe(self, 'new_active_document')

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'new_active_document' in messages:
            self.im_context.reset()

    def on_keypress_content(self, controller, keyval, keycode, keyboard_state):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_shift_mask = int(Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)

        self.ctrl_pressed = int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK or Gdk.keyval_name(keyval).startswith('Control')

        if (widget := document.get_selected_widget()) != None:
            if self.application.widget_manager.on_keypress(widget, keyval, keycode, keyboard_state):
                return

        match (Gdk.keyval_name(keyval).lower(), int(keyboard_state & modifiers)):
            case ('left', 0):
                UseCases.left()
            case ('right', 0):
                UseCases.right()
            case ('up', 0):
                UseCases.up(self.application.cursor_state.implicit_x_position)
            case ('down', 0):
                UseCases.down(self.application.cursor_state.implicit_x_position)
            case ('home', 0):
                UseCases.paragraph_start()
            case ('end', 0):
                UseCases.paragraph_end()
            case ('page_up', 0):
                UseCases.page(self.application.cursor_state.implicit_x_position, -self.application.document_view.document_view_height + 100)
            case ('page_down', 0):
                UseCases.page(self.application.cursor_state.implicit_x_position, self.application.document_view.document_view_height - 100)

            case ('left', Gdk.ModifierType.SHIFT_MASK):
                UseCases.left(True)
            case ('right', Gdk.ModifierType.SHIFT_MASK):
                UseCases.right(True)
            case ('up', Gdk.ModifierType.SHIFT_MASK):
                UseCases.up(self.application.cursor_state.implicit_x_position, True)
            case ('down', Gdk.ModifierType.SHIFT_MASK):
                UseCases.down(self.application.cursor_state.implicit_x_position, True)
            case ('home', Gdk.ModifierType.SHIFT_MASK):
                UseCases.paragraph_start(True)
            case ('end', Gdk.ModifierType.SHIFT_MASK):
                UseCases.paragraph_end(True)
            case ('page_up', Gdk.ModifierType.SHIFT_MASK):
                UseCases.page(self.application.cursor_state.implicit_x_position, -self.application.document_view.document_view_height + 100, True)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK):
                UseCases.page(self.application.cursor_state.implicit_x_position, self.application.document_view.document_view_height - 100, True)

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
                        tags_at_cursor = self.application.cursor_state.tags_at_cursor
                        UseCases.add_newline(tags_at_cursor)
                else:
                    tags_at_cursor = self.application.cursor_state.tags_at_cursor
                    UseCases.add_newline(tags_at_cursor)
            case ('backspace', _):
                UseCases.backspace()
            case ('delete', _):
                UseCases.delete()

            case _: return False
        return True

    def on_keyrelease_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.ctrl_pressed = int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK and not Gdk.keyval_name(keyval).startswith('Control')

    def on_im_commit(self, im_context, text):
        tags_at_cursor = self.application.cursor_state.tags_at_cursor
        UseCases.im_commit(text, tags_at_cursor)

    def on_focus_in(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.ctrl_pressed = int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK

        self.im_context.focus_in()

    def on_focus_out(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.ctrl_pressed = int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK

        self.im_context.focus_out()

    def on_im_commit(self, im_context, text):
        tags_at_cursor = self.application.cursor_state.tags_at_cursor
        UseCases.im_commit(text, tags_at_cursor)


