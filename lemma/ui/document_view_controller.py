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
from gi.repository import Gtk, Gdk, GLib, GObject, Gio

from urllib.parse import urlparse
import time

import lemma.services.xml_helpers as xml_helpers
from lemma.widgets.factory import WidgetFactory
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.node_type_db import NodeTypeDB
from lemma.services.xml_exporter import XMLExporter
from lemma.services.layout_info import LayoutInfo
from lemma.services.files import Files
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class DocumentViewController():

    def __init__(self, document_view):
        self.model = document_view
        self.view = self.model.view
        self.content = self.view.content

        self.content.connect('realize', self.on_realize)

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
        self.key_controller_content.connect('key-released', self.on_keyrelease_content)
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

        self.scroll_on_drop_callback_id = None
        self.drop_target = Gtk.DropTarget.new(GObject.TYPE_NONE, Gdk.DragAction.COPY)
        self.drop_target.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.drop_target.set_gtypes([Gdk.FileList, str, Gdk.Texture])
        self.drop_target.connect('drop', self.on_drop)
        self.drop_target.connect('enter', self.on_drop_enter)
        self.drop_target.connect('motion', self.on_drop_hover)
        self.drop_target.connect('leave', self.on_drop_leave)
        self.view.add_controller(self.drop_target)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_leave)
        self.content.add_controller(self.motion_controller)

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.on_scroll)
        self.scrolling_controller.connect('decelerate', self.on_decelerate)
        self.view.add_controller(self.scrolling_controller)

        self.view.scrollbar_vertical.observe('dragged', self.on_scrollbar_drag)

    def on_realize(self, content, data=None):
        self.model.reset_cursor_blink()

    def on_primary_button_press(self, controller, n_press, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x += self.model.scrolling_position_x - LayoutInfo.get_document_padding_left()
        y += self.model.scrolling_position_y - LayoutInfo.get_normal_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        self.model.selected_click_target = (x, y)

        if y > 0:
            link = document.get_link_at_xy(x, y)
            leaf_layout = document.get_leaf_layout_at_xy(x, y)

            if leaf_layout != None and leaf_layout['node'].type == 'widget':
                self.model.application.widget_manager.on_primary_button_press(leaf_layout['node'].value, n_press, x, y)
                if n_press == 1:
                    UseCases.select_node(leaf_layout['node'])

            elif n_press == 1:
                if int(keyboard_state & modifiers) == Gdk.ModifierType.SHIFT_MASK:
                    UseCases.move_cursor_to_xy(x, y, True)

                elif int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK:
                    UseCases.move_cursor_to_xy(x, y, False)

                else:
                    if leaf_layout != None and NodeTypeDB.focus_on_click(leaf_layout['node']):
                        UseCases.select_node(leaf_layout['node'])
                    else:
                        UseCases.move_cursor_to_xy(x, y, False)

            else:
                if link == None or int(keyboard_state & modifiers) != 0:
                    insert = document.get_insert_node()
                    selection = document.get_selection_node()
                    paragraph_start, paragraph_end = insert.paragraph_bounds()
                    if insert == paragraph_start and selection == paragraph_end or insert == paragraph_end and selection == paragraph_start:
                        UseCases.move_cursor_to_xy(x, y, False)
                    else:
                        UseCases.extend_selection()

            self.content.grab_focus()

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x += self.model.scrolling_position_x - LayoutInfo.get_document_padding_left()
        y += self.model.scrolling_position_y - LayoutInfo.get_normal_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        if keyboard_state == 0:
            if y >= -LayoutInfo.get_subtitle_height():
                document = self.model.document

                link_at_press = document.get_link_at_xy(*self.model.selected_click_target)
                link_at_release = document.get_link_at_xy(x, y)

                if link_at_press == link_at_release and link_at_release != None:
                    UseCases.open_link(link_at_release)
                    return

                x_at_press, y_at_press = self.model.selected_click_target
                line_layout_at_press = document.get_line_layout_at_y(y_at_press)
                paragraph_layout_at_press = line_layout_at_press['parent']

                line_layout_at_release = document.get_line_layout_at_y(y)
                paragraph_layout_at_release = line_layout_at_release['parent']

                if paragraph_layout_at_press != paragraph_layout_at_release: return
                if paragraph_layout_at_release['node'].style != 'cl': return
                if line_layout_at_release != paragraph_layout_at_release['children'][0]: return

                indentation = LayoutInfo.get_indentation('cl', paragraph_layout_at_release['node'].indentation_level)
                x_start = indentation - 35
                x_end = indentation - 16

                if y < paragraph_layout_at_release['y'] + line_layout_at_release['height'] - 23 or y > paragraph_layout_at_release['y'] + line_layout_at_release['height'] - 4 or x < x_start or x > x_end: return
                if y_at_press < paragraph_layout_at_press['y'] + line_layout_at_press['height'] - 23 or y_at_press > paragraph_layout_at_press['y'] + line_layout_at_press['height'] - 4 or x_at_press < x_start or x_at_press > x_end: return

                UseCases.toggle_checkbox_at_cursor()

    def on_secondary_button_press(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x_offset = self.model.scrolling_position_x + x - LayoutInfo.get_document_padding_left()
        y_offset = self.model.scrolling_position_y + y - LayoutInfo.get_normal_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        if y_offset > 0:
            if not document.has_selection():
                leaf_layout = document.get_leaf_layout_at_xy(x_offset, y_offset)
                if keyboard_state == 0 and leaf_layout != None and NodeTypeDB.focus_on_click(leaf_layout['node']):
                    UseCases.select_node(leaf_layout['node'])
                else:
                    UseCases.move_cursor_to_xy(x_offset, y_offset, False)
            self.model.application.context_menu_document.popup_at_cursor(x, y)

    def on_drag_begin(self, gesture, x, y, data=None):
        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()
        y += self.model.scrolling_position_y

        if y <= 0:
            gesture.reset()

    def on_drag_update(self, gesture, x, y, data=None):
        if x == 0 and y == 0: return

        start_point = gesture.get_start_point()
        x, y = start_point.x + x, start_point.y + y

        if y < 0:
            new_x = self.model.scrolling_position_x
            new_y = max(0, self.model.scrolling_position_y + y)
            self.model.application.scrolling.scroll_to_xy(new_x, new_y, animation_type=None)

        if y - self.model.document_view_height > 0:
            height = self.model.document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + self.model.application.document_title.title_buttons_height
            new_x = self.model.scrolling_position_x
            new_y = min(max(0, height - self.model.document_view_height), self.model.scrolling_position_y + y - self.model.document_view_height)
            self.model.application.scrolling.scroll_to_xy(new_x, new_y, animation_type=None)

        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()
        y += self.model.scrolling_position_y

        UseCases.move_cursor_to_xy(x, y, True)

    def on_drag_end(self, gesture, x, y, data=None):
        pass

    def on_drop(self, controller, value, x, y):
        if self.scroll_on_drop_callback_id != None:
            self.content.remove_tick_callback(self.scroll_on_drop_callback_id)
            self.scroll_on_drop_callback_id = None

        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()
        y += self.model.scrolling_position_y

        self.handle_drop(value, x, y)
        controller.reset()

    def handle_drop(self, value, x, y):
        document = WorkspaceRepo.get_workspace().get_active_document()

        self.model.set_drop_cursor_position(-1, -1)

        if isinstance(value, Gdk.FileList):
            for file in value.get_files():
                file_info = file.query_info('standard::content-type', 0, None)
                path = file.get_parse_name()
                content_type = file_info.get_content_type()
                done_with_file = False

                if content_type.endswith('/directory'):
                    continue

                if content_type.startswith('image/'):
                    try:
                        texture = Gdk.Texture.new_from_file(file)
                    except Exception: pass
                    else:
                        filename = Files.get_distinct_document_file_name(document, '.png')
                        texture.save_to_png(Files.abspath_for_document_file(filename))
                        image = WidgetFactory.make_widget('image', {'filename': filename})

                        UseCases.move_cursor_to_xy(x, y)
                        UseCases.add_widget(image)

                        done_with_file = True

                if not done_with_file:
                    filename = Files.add_file_to_doc_folder_with_distinct_name(document, path)
                    widget = WidgetFactory.make_widget('attachment', {'filename': filename})

                    UseCases.move_cursor_to_xy(x, y)
                    UseCases.add_widget(widget)

        elif isinstance(value, str):
            text = value

            if len(text) < 2000 and urlparse(text.strip()).scheme in ['http', 'https'] and '.' in urlparse(text.strip()).netloc:
                text = xml_helpers.escape(text.strip())
                xml = xml_helpers.embellish_with_link_and_tags(text, text, set())
            else:
                xml = xml_helpers.escape(text)

            UseCases.move_cursor_to_xy(x, y)
            UseCases.insert_xml(xml)

        elif isinstance(value, Gdk.Texture):
            texture = value
            filename = Files.get_distinct_document_file_name(document, '.png')
            texture.save_to_png(Files.abspath_for_document_file(filename))
            image = WidgetFactory.make_widget('image', {'filename': filename})

            UseCases.move_cursor_to_xy(x, y)
            UseCases.add_widget(image)

    def on_drop_enter(self, controller, x, y):
        self.scroll_on_drop_callback_id = self.content.add_tick_callback(self.scroll_on_drop_callback)

        return Gdk.DragAction.COPY

    def on_drop_hover(self, controller, x, y):
        self.model.set_drop_cursor_position(x, y)

        return Gdk.DragAction.COPY

    def on_drop_leave(self, controller):
        if self.scroll_on_drop_callback_id != None:
            self.content.remove_tick_callback(self.scroll_on_drop_callback_id)
            self.scroll_on_drop_callback_id = None
        self.model.set_drop_cursor_position(-1, -1)

    def scroll_on_drop_callback(self, widget, frame_clock):
        x, y = self.model.drop_cursor_x, self.model.drop_cursor_y

        if y < 56:
            new_x = self.model.scrolling_position_x
            new_y = max(0, self.model.scrolling_position_y + y - 56)
            self.model.application.scrolling.scroll_to_xy(new_x, new_y, animation_type=None)

        if y - self.model.document_view_height > -56:
            height = self.model.document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + self.model.application.document_title.title_buttons_height
            new_x = self.model.scrolling_position_x
            new_y = min(max(0, height - self.model.document_view_height), self.model.scrolling_position_y + y - self.model.document_view_height + 56)
            self.model.application.scrolling.scroll_to_xy(new_x, new_y, animation_type=None)

        return True

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0
        if abs(dy) > 0 and abs(dx / dy) >  1: dy = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            document = self.model.document
            height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + self.model.application.document_title.title_buttons_height

            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= self.model.document_view_width ** (2/3)
                dy *= self.model.document_view_height ** (2/3)
            else:
                dy *= self.model.scrolling_multiplier
                dx *= self.model.scrolling_multiplier
            x = min(0, max(0, self.model.scrolling_position_x + dx))
            y = min(max(0, height - self.model.document_view_height), max(0, self.model.scrolling_position_y + dy))

            self.model.application.scrolling.scroll_to_xy(x, y, animation_type=None)
        return

    def on_decelerate(self, controller, vel_x, vel_y):
        if abs(vel_x) > 0 and abs(vel_y / vel_x) >= 1: vel_x = 0
        if abs(vel_y) > 0 and abs(vel_x / vel_y) >  1: vel_y = 0

        self.model.application.scrolling.decelerate(self.model.scrolling_position_x, self.model.scrolling_position_y, vel_x, vel_y)

    def on_scrollbar_drag(self, widget, new_y):
        self.model.application.scrolling.scroll_to_xy(0, new_y, animation_type=None)

    def on_keypress_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_shift_mask = int(Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)

        self.model.set_ctrl_pressed(int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK or Gdk.keyval_name(keyval).startswith('Control'))

        if self.model.document == None: return False

        document = self.model.document

        if (widget := document.get_selected_widget()) != None:
            if self.model.application.widget_manager.on_keypress(widget, keyval, keycode, keyboard_state):
                return

        match (Gdk.keyval_name(keyval).lower(), int(keyboard_state & modifiers)):
            case ('f2', _):
                self.model.application.actions.actions['rename-document'].activate()
            case ('left', 0):
                UseCases.left()
            case ('right', 0):
                UseCases.right()
            case ('up', 0):
                UseCases.up()
            case ('down', 0):
                UseCases.down()
            case ('home', 0):
                UseCases.paragraph_start()
            case ('end', 0):
                UseCases.paragraph_end()
            case ('page_up', 0):
                UseCases.page(-self.model.document_view_height + 100)
            case ('page_down', 0):
                UseCases.page(self.model.document_view_height - 100)

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
                UseCases.page(-self.model.document_view_height + 100, True)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK):
                UseCases.page(self.model.document_view_height - 100, True)

            case ('up', Gdk.ModifierType.CONTROL_MASK):
                UseCases.move_cursor_to_parent()
            case ('up', 5):
                UseCases.extend_selection()
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
                        tags_at_cursor = self.model.application.toolbars.tags_at_cursor
                        UseCases.add_newline(tags_at_cursor)
                else:
                    tags_at_cursor = self.model.application.toolbars.tags_at_cursor
                    UseCases.add_newline(tags_at_cursor)
            case ('backspace', _):
                UseCases.backspace()
            case ('delete', _):
                UseCases.delete()

            case _: return False
        return True

    def on_keyrelease_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK and not Gdk.keyval_name(keyval).startswith('Control'))

    def on_im_commit(self, im_context, text):
        tags_at_cursor = self.model.application.toolbars.tags_at_cursor
        UseCases.im_commit(text, tags_at_cursor)

    def on_focus_in(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.im_context.focus_in()
        self.model.reset_cursor_blink()
        self.view.content.queue_draw()

    def on_focus_out(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.im_context.focus_out()
        self.view.content.queue_draw()

    def on_focus_change(self, controller, pspec):
        self.view.content.queue_draw()

    def on_enter(self, controller, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.model.set_pointer_position(x, y)

    def on_hover(self, controller, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.model.set_pointer_position(x, y)
        self.view.scrollbar_vertical.ping()

    def on_leave(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.model.set_pointer_position(None, None)


