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

import time

import lemma.infrastructure.xml_helpers as xml_helpers
from lemma.application_state.application_state import ApplicationState


class DocumentViewController():

    def __init__(self, document_view, use_cases):
        self.model = document_view
        self.use_cases = use_cases
        self.view = self.model.view
        self.content = self.view.content

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.content.add_controller(self.primary_click_controller)

        self.secondary_click_controller = Gtk.GestureClick()
        self.secondary_click_controller.set_button(3)
        self.secondary_click_controller.connect('pressed', self.on_secondary_button_press)
        self.content.add_controller(self.secondary_click_controller)

        self.key_controller_content = Gtk.EventControllerKey()
        self.key_controller_content.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller_content.connect('key-pressed', self.on_keypress_content)
        self.key_controller_content.connect('modifiers', self.on_modifiers_change)
        self.content.add_controller(self.key_controller_content)

        self.im_context = Gtk.IMContextSimple()
        self.im_context.set_use_preedit(True)
        self.im_context.connect('commit', self.on_im_commit)
        self.key_controller_content.set_im_context(self.im_context)

        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.on_focus_in)
        self.focus_controller.connect('leave', self.on_focus_out)
        self.focus_controller.connect('notify::is-focus', self.on_focus_change)
        self.content.add_controller(self.focus_controller)

        self.drag_controller = Gtk.GestureDrag()
        self.drag_controller.connect('drag-begin', self.on_drag_begin)
        self.drag_controller.connect('drag-update', self.on_drag_update)
        self.drag_controller.connect('drag-end', self.on_drag_end)
        self.content.add_controller(self.drag_controller)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_leave)
        self.content.add_controller(self.motion_controller)

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.on_scroll)
        self.content.add_controller(self.scrolling_controller)

        self.view.adjustment_x.connect('value-changed', self.on_adjustment_value_changed)
        self.view.adjustment_y.connect('value-changed', self.on_adjustment_value_changed)

        self.content.connect('resize', self.on_resize)

    def on_primary_button_press(self, controller, n_press, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x = document.clipping.offset_x + x
        y = document.clipping.offset_y + y
        state = controller.get_current_event_state() & modifiers

        self.model.selected_link_target = None

        x -= ApplicationState.get_value('document_padding_left')
        y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')

        if y < -ApplicationState.get_value('subtitle_height') and n_press % 3 == 1:
            self.model.init_renaming()

        elif y > 0:
            link = self.get_link_at_xy(x, y)
            leaf_box = document.layout.get_leaf_at_xy(x, y)

            if n_press == 1:
                if int(state & modifiers) == Gdk.ModifierType.SHIFT_MASK:
                    self.use_cases.move_cursor_to_xy(x, y, True)

                elif int(state & modifiers) == Gdk.ModifierType.CONTROL_MASK:
                    self.use_cases.move_cursor_to_xy(x, y, False)

                else:
                    if leaf_box != None and leaf_box.node.focus_on_click():
                        self.use_cases.select_node(leaf_box.node)
                    else:
                        self.use_cases.move_cursor_to_xy(x, y, False)
                    if link != None:
                        self.model.selected_link_target = link

            else:
                if link == None or int(state & modifiers) != 0:
                    insert = document.cursor.get_insert_node()
                    selection = document.cursor.get_selection_node()
                    line_start, line_end = insert.line_bounds()
                    if insert == line_start and selection == line_end or insert == line_end and selection == line_start:
                        self.use_cases.move_cursor_to_xy(x, y, False)
                    else:
                        self.use_cases.extend_selection()

            self.content.grab_focus()

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x = document.clipping.offset_x + x
        y = document.clipping.offset_y + y
        state = controller.get_current_event_state() & modifiers

        if state == 0:
            x -= ApplicationState.get_value('document_padding_left')
            y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')

            if y >= -ApplicationState.get_value('subtitle_height'):
                document = self.model.document

                link = self.get_link_at_xy(x, y)
                if link == self.model.selected_link_target:
                    self.use_cases.open_link(link)

    def on_secondary_button_press(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        document = self.model.document
        x_offset = document.clipping.offset_x + x - ApplicationState.get_value('document_padding_left')
        y_offset = document.clipping.offset_y + y - ApplicationState.get_value('document_padding_top') - ApplicationState.get_value('title_height') - ApplicationState.get_value('subtitle_height')

        if y > 0:
            if not document.cursor.has_selection():
                self.use_cases.move_cursor_to_xy(x_offset, y_offset, False)
            self.view.context_menu.popup_at_cursor(x, y)

    def on_drag_begin(self, gesture, x, y, data=None):
        x -= ApplicationState.get_value('document_padding_left')
        y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')
        y += self.model.document.clipping.offset_y

        if y <= 0:
            gesture.reset()

    def on_drag_update(self, gesture, x, y, data=None):
        if x == 0 and y == 0: return

        start_point = gesture.get_start_point()
        x, y = start_point.x + x, start_point.y + y

        if y < 0:
            new_x = self.model.document.clipping.offset_x
            new_y = max(0, self.model.document.clipping.offset_y + y)
            self.use_cases.scroll_to_xy(new_x, new_y)

        if y - ApplicationState.get_value('document_view_height') > 0:
            height = self.model.document.layout.height + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')
            new_x = self.model.document.clipping.offset_x
            new_y = min(max(0, height - ApplicationState.get_value('document_view_height')), self.model.document.clipping.offset_y + y - ApplicationState.get_value('document_view_height'))
            self.use_cases.scroll_to_xy(new_x, new_y)

        x -= ApplicationState.get_value('document_padding_left')
        y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')
        y += self.model.document.clipping.offset_y

        self.use_cases.move_cursor_to_xy(x, y, True)

    def on_drag_end(self, gesture, x, y, data=None):
        pass

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0
        if abs(dy) > 0 and abs(dx / dy) >  1: dy = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            document = self.model.document
            height = document.layout.height + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')

            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= ApplicationState.get_value('document_view_width') ** (2/3)
                dy *= ApplicationState.get_value('document_view_height') ** (2/3)
            else:
                dy *= self.model.scrolling_multiplier
                dx *= self.model.scrolling_multiplier
            x = min(0, max(0, document.clipping.offset_x + dx))
            y = min(max(0, height - ApplicationState.get_value('document_view_height')), max(0, document.clipping.offset_y + dy))

            self.use_cases.scroll_to_xy(x, y)
        return

    def on_modifiers_change(self, controller, state):
        self.model.set_keyboard_modifiers_state(state)

    def on_keypress_content(self, controller, keyval, keycode, state):
        if self.model.document == None: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_shift_mask = int(Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)

        document = self.model.document
        match (Gdk.keyval_name(keyval).lower(), int(state & modifiers)):
            case ('left', 0): self.use_cases.left()
            case ('right', 0): self.use_cases.right()
            case ('up', 0): self.use_cases.up()
            case ('down', 0): self.use_cases.down()
            case ('home', 0): self.use_cases.line_start()
            case ('end', 0): self.use_cases.line_end()
            case ('page_up', 0): self.use_cases.move_cursor_by_xy_offset(0, -ApplicationState.get_value('document_view_height') + 100)
            case ('page_down', 0): self.use_cases.move_cursor_by_xy_offset(0, ApplicationState.get_value('document_view_height') - 100)

            case ('left', Gdk.ModifierType.SHIFT_MASK): self.use_cases.left(True)
            case ('right', Gdk.ModifierType.SHIFT_MASK): self.use_cases.right(True)
            case ('up', Gdk.ModifierType.SHIFT_MASK): self.use_cases.up(True)
            case ('down', Gdk.ModifierType.SHIFT_MASK): self.use_cases.down(True)
            case ('home', Gdk.ModifierType.SHIFT_MASK): self.use_cases.line_start(True)
            case ('end', Gdk.ModifierType.SHIFT_MASK): self.use_cases.line_end(True)
            case ('page_up', Gdk.ModifierType.SHIFT_MASK):
                self.use_cases.move_cursor_by_xy_offset(0, -ApplicationState.get_value('document_view_height') + 100, True)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK):
                self.use_cases.move_cursor_by_xy_offset(0, ApplicationState.get_value('document_view_height') - 100, True)

            case ('up', Gdk.ModifierType.CONTROL_MASK): self.use_cases.move_cursor_to_parent()
            case ('up', 5): self.use_cases.extend_selection()
            case ('left', Gdk.ModifierType.CONTROL_MASK): self.use_cases.jump_left(False)
            case ('left', 5): self.use_cases.jump_left(True)
            case ('right', Gdk.ModifierType.CONTROL_MASK): self.use_cases.jump_right(False)
            case ('right', 5): self.use_cases.jump_right(True)

            case ('tab', 0): self.use_cases.select_next_placeholder()
            case ('iso_left_tab', Gdk.ModifierType.SHIFT_MASK): self.use_cases.select_prev_placeholder()
            case ('escape', _):
                if document.cursor.has_selection():
                    selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
                    if len(selected_nodes) == 1 and selected_nodes[0].is_widget():
                        self.use_cases.remove_selection()
            case ('return', _):
                if not document.cursor.has_selection() and document.cursor.get_insert_node().is_inside_link():
                    self.use_cases.open_link(document.cursor.get_insert_node().link)
                else:
                    self.use_cases.insert_xml('\n')
                    if not document.cursor.has_selection():
                        self.use_cases.replace_max_string_before_cursor(ApplicationState.get_value('tags_at_cursor'))
            case ('backspace', _): self.use_cases.backspace()
            case ('delete', _): self.use_cases.delete()

            case _: return False
        return True

    def on_im_commit(self, im_context, text):
        self.use_cases.im_commit(text)

    def on_focus_in(self, controller):
        self.im_context.focus_in()
        self.view.content.queue_draw()

    def on_focus_out(self, controller):
        self.im_context.focus_out()
        self.view.content.queue_draw()

    def on_focus_change(self, controller, pspec):
        self.view.content.queue_draw()

    def on_enter(self, controller, x, y):
        self.model.set_cursor_position(x, y)

    def on_hover(self, controller, x, y):
        self.model.set_cursor_position(x, y)

    def on_leave(self, controller):
        self.model.set_cursor_position(None, None)

    def on_resize(self, drawing_area, width, height):
        self.model.set_size(width, height)

    def on_adjustment_value_changed(self, adjustment):
        document = self.model.document

        offset_x = self.view.adjustment_x.get_value()
        offset_y = self.view.adjustment_y.get_value()
        self.model.last_cursor_or_scrolling_change = time.time()
        if offset_x != document.clipping.offset_x or offset_y != document.clipping.offset_y:
            self.use_cases.scroll_to_xy(offset_x, offset_y)

    def get_link_at_xy(self, x, y):
        layout = self.model.document.layout.get_leaf_at_xy(x, y)

        if layout != None:
            return layout.node.link
        else:
            return None


