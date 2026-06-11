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
from lemma.ui.shortcuts import Shortcuts
from lemma.services.node_type_db import NodeTypeDB
from lemma.use_cases.use_cases import UseCases
from lemma.services.message_bus import MessageBus
import lemma.services.timer as timer


class Keyboard():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.view = main_window.document_view
        self.content = self.view.content
        self.actions = self.application.actions.actions

        self.tags_at_cursor = set()
        self.implicit_x_position = 0
        self.ctrl_pressed = False
        self.insert_node = None
        self.selection_node = None

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
        self.shortcut_controller.add_cb('go_to_parent_node', self.actions['move-cursor-to-parent'].activate)
        self.shortcut_controller.add_cb('extend_selection', self.actions['extend-selection'].activate)
        self.shortcut_controller.add_cb('rename_document', self.actions['rename-document'].activate)
        for para_style in ['h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl', 'p']:
            sc_name = 'paragraph_style_' + para_style
            callback = self.actions['set-paragraph-style'].activate
            self.shortcut_controller.add_cb(sc_name, callback, GLib.Variant.new_string(para_style))
        self.view.content.add_controller(self.shortcut_controller)

        self.content.connect('realize', self.on_realize)

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.focus_controller.connect('leave', self.on_focus_out)
        self.view.content.add_controller(self.focus_controller)

        MessageBus.subscribe(self, 'new_active_document')
        MessageBus.subscribe(self, 'document_ast_or_cursor_changed')
        MessageBus.subscribe(self, 'implicit_x_position_changed')

    def animate(self):
        messages = MessageBus.get_messages(self)

        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None:
            self.im_context.reset()

        if 'new_active_document' in messages or 'document_ast_or_cursor_changed' in messages:
            self.update_tags_at_cursor()
            self.im_context.reset()

        if 'new_active_document' in messages or 'implicit_x_position_changed' in messages:
            self.update_implicit_x_position()

        time_since_blink_start = time.time() - self.cursor_blink_reset
        time_in_cycle = (time_since_blink_start % self.cursor_blink_time) / self.cursor_blink_time

        cursor_visible = True
        if time_since_blink_start <= 10 and time_in_cycle > 0.6:
            cursor_visible = False
        if not self.view.content.has_focus():
            cursor_visible = False
        if document.has_selection():
            cursor_visible = False

        if time_since_blink_start <= self.cursor_blink_timeout and cursor_visible != self.cursor_visible:
            self.cursor_visible = cursor_visible
            self.view.content.queue_draw()

    def update_implicit_x_position(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            self.implicit_x_position = 0
        else:
            layout = self.application.layout
            insert = document.cursor.get_insert_node()

            x, y = layout.get_absolute_xy(layout.get_node_layout(insert))
            self.implicit_x_position = x

    def update_tags_at_cursor(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            self.tags_at_cursor = set()
        else:
            node = document.get_insert_node()

            if node.parent.type == 'paragraph':
                prev_node = node.prev_no_descent()
            else:
                prev_node = node.prev_in_parent()

            if node == None or prev_node == None:
                self.tags_at_cursor = set()
            else:
                self.tags_at_cursor = prev_node.tags.copy()

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
                self.left()
            case ('right', 0):
                self.right()
            case ('up', 0):
                self.up()
            case ('down', 0):
                self.down()
            case ('home', 0):
                self.paragraph_start()
            case ('end', 0):
                self.paragraph_end()
            case ('page_up', 0):
                self.page(-self.application.document_view.height + 100)
            case ('page_down', 0):
                self.page(self.application.document_view.height - 100)

            case ('left', Gdk.ModifierType.SHIFT_MASK):
                self.left(True)
            case ('right', Gdk.ModifierType.SHIFT_MASK):
                self.right(True)
            case ('up', Gdk.ModifierType.SHIFT_MASK):
                self.up(True)
            case ('down', Gdk.ModifierType.SHIFT_MASK):
                self.down(True)
            case ('home', Gdk.ModifierType.SHIFT_MASK):
                self.paragraph_start(True)
            case ('end', Gdk.ModifierType.SHIFT_MASK):
                self.paragraph_end(True)
            case ('page_up', Gdk.ModifierType.SHIFT_MASK):
                self.page(-self.application.document_view.height + 100, True)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK):
                self.page(self.application.document_view.height - 100, True)

            case ('left', Gdk.ModifierType.CONTROL_MASK):
                self.jump_left(False)
            case ('left', 5):
                self.jump_left(True)
            case ('right', Gdk.ModifierType.CONTROL_MASK):
                self.jump_right(False)
            case ('right', 5):
                self.jump_right(True)

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
                    self.update_implicit_x_position()
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
                        UseCases.add_newline(self.tags_at_cursor)
                        self.update_implicit_x_position()
                else:
                    UseCases.add_newline(self.tags_at_cursor)
                    self.update_implicit_x_position()
            case ('backspace', _):
                self.backspace()
            case ('delete', _):
                self.delete()

            case _: return False
        return True

    def on_keyrelease_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.ctrl_pressed = int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK and not Gdk.keyval_name(keyval).startswith('Control')

    def on_im_commit(self, im_context, text):
        UseCases.im_commit(text, self.tags_at_cursor)

        self.update_implicit_x_position()
        self.application.autocomplete.on_keyboard_input()

    def on_preedit_changed(self, im_context):
        self.application.layout.invalidate_on_preedit_change()
        self.application.document_view.clear_render_cache()
        self.view.content.queue_draw()
        MessageBus.add_message('preedit_changed')

    def on_realize(self, content, data=None):
        self.reset_cursor_blink()

    def on_focus_in(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.ctrl_pressed = int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK

        self.reset_cursor_blink()
        self.im_context.focus_in()

    def on_focus_out(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.ctrl_pressed = int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK

        self.im_context.focus_out()

    @timer.timer
    def backspace(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        if document.has_selection():
            UseCases.delete_selection()
        elif not insert.is_first_in_parent():
            UseCases.delete_section(insert.prev_in_parent(), insert)
        elif insert.parent.type == 'paragraph' and not insert.parent.is_first_in_parent():
            UseCases.delete_section(insert.prev_no_descent(), insert)
        elif insert.parent.type != 'paragraph' and len(insert.parent) == 1:
            UseCases.select_section(insert.prev_no_descent(), insert)

        self.update_implicit_x_position()

    @timer.timer
    def delete(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        if document.has_selection():
            UseCases.delete_selection()
        elif not insert.is_last_in_parent():
            UseCases.delete_section(insert, insert.next_in_parent())
        elif insert.parent.type == 'paragraph' and not insert.parent.is_last_in_parent():
            UseCases.delete_section(insert, insert.next())
        elif insert.parent.type != 'paragraph' and len(insert.parent) == 1:
            UseCases.select_section(insert.next_no_descent(), insert)

        self.update_implicit_x_position()

    @timer.timer
    def left(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        selection = document.get_selection_node()

        if do_selection:
            new_insert = insert.prev_no_descent()
            if new_insert != None:
                UseCases.select_section(new_insert, selection)
        elif document.has_selection():
            UseCases.move_cursor_to_node(document.get_first_selection_bound())
        else:
            next_insert = insert.prev()
            if next_insert != None:
                UseCases.move_cursor_to_node(next_insert)

        if not do_selection:
            self.update_implicit_x_position()

    @timer.timer
    def jump_left(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selection = document.get_selection_node()
        original_insert = document.get_insert_node()
        insert = original_insert
        prev_insert = insert.prev_no_descent()
        while prev_insert != None and NodeTypeDB.is_whitespace(prev_insert):
            insert = prev_insert
            prev_insert = insert.prev_no_descent()

        if prev_insert != None:
            insert_new = insert.prev_no_descent().word_bounds()[0]
        else:
            insert_new = insert

        if do_selection:
            UseCases.select_section(insert_new, selection)
        elif document.has_selection():
            UseCases.move_cursor_to_node(document.get_first_selection_bound())
        else:
            UseCases.move_cursor_to_node(insert_new)

        if not do_selection:
            self.update_implicit_x_position()

    @timer.timer
    def right(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        selection = document.get_selection_node()

        if do_selection:
            new_insert = insert.next_no_descent()
            if new_insert != None:
                UseCases.select_section(new_insert, selection)
        elif document.has_selection():
            UseCases.move_cursor_to_node(document.get_last_selection_bound())
        else:
            next_insert = insert.next()
            if next_insert != None:
                UseCases.move_cursor_to_node(next_insert)

        if not do_selection:
            self.update_implicit_x_position()

    @timer.timer
    def jump_right(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selection = document.get_selection_node()
        original_insert = document.get_insert_node()
        insert = original_insert
        while NodeTypeDB.is_whitespace(insert):
            next_insert = insert.next_no_descent()
            if next_insert == None:
                break
            insert = next_insert

        if not NodeTypeDB.is_whitespace(insert):
            insert_new = insert.word_bounds()[1]
        else:
            insert_new = insert

        if do_selection:
            UseCases.select_section(insert_new, selection)
        elif document.has_selection():
            UseCases.move_cursor_to_node(document.get_last_selection_bound())
        else:
            UseCases.move_cursor_to_node(insert_new)

        if not do_selection:
            self.update_implicit_x_position()

    @timer.timer
    def up(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        x, y = self.application.layout.get_absolute_xy(self.application.layout.get_node_layout(insert))
        if self.implicit_x_position != None:
            x = self.implicit_x_position

        new_node = None
        ancestors = self.application.layout.get_ancestors(self.application.layout.get_node_layout(insert))
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][:j]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast:
                        for hbox in self.application.layout.get_paragraph_layout(paragraph)['children']:
                            if hbox['y'] + hbox['parent']['y'] < ancestors[i - 1]['y'] + ancestors[i - 1]['parent']['y']:
                                prev_hboxes.append(hbox)
                for hbox in reversed(prev_hboxes):
                    if new_node == None:
                        min_distance = 10000
                        for layout in hbox['children']:
                            layout_x, layout_y = self.application.layout.get_absolute_xy(layout)
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = layout['node']
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[0][0]

        if do_selection:
            UseCases.select_section(new_node, document.get_selection_node())
        else:
            UseCases.move_cursor_to_node(new_node)

    @timer.timer
    def down(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()
        insert_layout = self.application.layout.get_node_layout(insert)

        x, y = self.application.layout.get_absolute_xy(insert_layout)
        if self.implicit_x_position != None:
            x = self.implicit_x_position

        new_node = None
        ancestors = self.application.layout.get_ancestors(insert_layout)
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][j + 1:]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast:
                        for hbox in self.application.layout.get_paragraph_layout(paragraph)['children']:
                            if hbox['y'] + hbox['parent']['y'] > ancestors[i - 1]['y'] + ancestors[i - 1]['parent']['y']:
                                prev_hboxes.append(hbox)
                for child in prev_hboxes:
                    if new_node == None:
                        min_distance = 10000
                        for layout in child['children']:
                            layout_x, layout_y = self.application.layout.get_absolute_xy(layout)
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = layout['node']
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[-1][-1]

        if do_selection:
            UseCases.select_section(new_node, document.get_selection_node())
        else:
            UseCases.move_cursor_to_node(new_node)

    @timer.timer
    def paragraph_start(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        layout = self.application.layout.get_node_layout(insert)
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][0]['node'] == None:
            layout = layout['children'][0]
        new_node = layout['children'][0]['node']

        if do_selection:
            UseCases.select_section(new_node, document.get_selection_node())
        else:
            UseCases.move_cursor_to_node(new_node)

        if not do_selection:
            self.update_implicit_x_position()

    @timer.timer
    def paragraph_end(self, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        layout = self.application.layout.get_node_layout(insert)
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][-1]['node'] == None:
            layout = layout['children'][-1]
        new_node = layout['children'][-1]['node']

        if do_selection:
            UseCases.select_section(new_node, document.get_selection_node())
        else:
            UseCases.move_cursor_to_node(new_node)

        if not do_selection:
            self.update_implicit_x_position()

    @timer.timer
    def page(self, y, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        orig_x, orig_y = self.application.layout.get_absolute_xy(self.application.layout.get_node_layout(insert))
        if self.implicit_x_position != None:
            orig_x = self.implicit_x_position
        new_x = orig_x
        new_y = orig_y + y
        layout = self.application.layout.get_cursor_holding_layout_close_to_xy(new_x, new_y)

        if do_selection:
            UseCases.select_section(layout['node'], document.get_selection_node())
        else:
            UseCases.move_cursor_to_node(layout['node'])

    def reset_cursor_blink(self):
        self.cursor_blink_reset = time.time()


