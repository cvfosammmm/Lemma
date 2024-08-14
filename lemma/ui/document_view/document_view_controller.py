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

from urllib.parse import urlparse
import webbrowser, time

from lemma.document.document import Document


class DocumentViewController():

    def __init__(self, document_view):
        self.model = document_view
        self.view = self.model.view
        self.content = self.view.content

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.content.add_controller(self.primary_click_controller)

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
        if n_press != 1: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        document = self.model.document
        x = document.clipping.offset_x + x
        y = document.clipping.offset_y + y
        state = controller.get_current_event_state() & modifiers

        self.model.selected_link_target = None

        x -= self.view.padding_left
        y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height

        if y < -self.view.subtitle_height:
            self.model.init_renaming()

        elif y > 0:
            link = document.layout.get_link_at_xy(x, y)

            if int(state & modifiers) == Gdk.ModifierType.SHIFT_MASK:
                document.add_command('selection_xy', x, y)

            elif int(state & modifiers) == Gdk.ModifierType.CONTROL_MASK:
                document.add_command('move_cursor_to_xy', x, y)

            else:
                if link != None:
                    self.model.selected_link_target = link.target
                else:
                    document.add_command('move_cursor_to_xy', x, y)

            self.content.grab_focus()

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press != 1: return
        modifiers = Gtk.accelerator_get_default_mod_mask()

        document = self.model.document
        x = document.clipping.offset_x + x
        y = document.clipping.offset_y + y
        state = controller.get_current_event_state() & modifiers

        if state == 0:
            x -= self.view.padding_left
            y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height

            if y >= -self.view.subtitle_height:
                document = self.model.document

                link = document.layout.get_link_at_xy(x, y)
                if link != None and link.target == self.model.selected_link_target:
                    self.open_link(link.target)

    def on_drag_begin(self, gesture, x, y, data=None):
        x -= self.view.padding_left
        y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height
        y += self.model.document.clipping.offset_y

        if y <= 0:
            gesture.reset()

    def on_drag_update(self, gesture, x, y, data=None):
        start_point = gesture.get_start_point()
        x, y = start_point.x + x, start_point.y + y
        x -= self.view.padding_left
        y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height
        y += self.model.document.clipping.offset_y

        if y > 0:
            document = self.model.document
            document.add_command('selection_xy', x, y)

    def on_drag_end(self, gesture, x, y, data=None):
        pass

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0
        if abs(dy) > 0 and abs(dx / dy) >  1: dy = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            document = self.model.document
            height = document.layout.height + self.view.padding_bottom + self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height

            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= self.model.width ** (2/3)
                dy *= self.model.height ** (2/3)
            else:
                dy *= self.model.scrolling_multiplier
                dx *= self.model.scrolling_multiplier
            x = min(0, max(0, document.clipping.offset_x + dx))
            y = min(max(0, height - self.model.height), max(0, document.clipping.offset_y + dy))

            document.add_command('scroll_to_xy', x, y)
        return

    def on_modifiers_change(self, controller, state):
        self.model.set_keyboard_modifiers_state(state)

    def on_keypress_content(self, controller, keyval, keycode, state):
        if self.model.document == None: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()

        document = self.model.document
        match (Gdk.keyval_name(keyval).lower(), int(state & modifiers)):
            case ('left', 0): document.add_command('left')
            case ('right', 0): document.add_command('right')
            case ('up', 0): document.add_command('up')
            case ('down', 0): document.add_command('down')
            case ('home', 0): document.add_command('line_start')
            case ('end', 0): document.add_command('line_end')
            case ('page_up', 0): document.add_command('page_up', self.model.height)
            case ('page_down', 0): document.add_command('page_down', self.model.height)

            case ('left', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_left')
            case ('right', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_right')
            case ('up', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_up')
            case ('down', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_down')
            case ('home', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_line_start')
            case ('end', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_line_end')
            case ('page_up', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_page_up', self.model.height)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK): document.add_command('selection_page_down', self.model.height)

            case ('return', _):
                if not document.cursor.has_selection() and document.cursor.get_insert_node().is_inside_link():
                    self.open_link(document.cursor.get_insert_node().link.target)
                else:
                    document.add_command('newline')
            case ('backspace', _): document.add_command('backspace')
            case ('delete', _): document.add_command('delete')

            case _: return False
        return True

    def on_im_commit(self, im_context, text):
        if self.model.document == None: return False

        self.model.document.add_command('insert_text', text, self.model.tags_at_cursor, self.model.link_target_at_cursor)

    def on_focus_in(self, controller):
        self.im_context.focus_in()
        self.view.content.queue_draw()

    def on_focus_out(self, controller):
        self.im_context.focus_out()
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
        offset_x = self.view.adjustment_x.get_value()
        offset_y = self.view.adjustment_y.get_value()
        self.model.last_cursor_or_scrolling_change = time.time()
        self.model.document.add_command('scroll_to_xy', offset_x, offset_y)

    def open_link(self, link_target):
        workspace = self.model.workspace

        if urlparse(link_target).scheme in ['http', 'https']:
            webbrowser.open(link_target)
        else:
            target_document = workspace.get_by_title(link_target)
            if target_document != None:
                workspace.set_active_document(target_document)
            else:
                id = workspace.get_new_document_id()
                document = Document(id)
                document.title = link_target
                workspace.add(document)
                workspace.set_active_document(document)


