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
from lemma.widgets.image import Image
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.application_state.application_state import ApplicationState
from lemma.services.node_type_db import NodeTypeDB
from lemma.services.xml_exporter import XMLExporter
from lemma.services.layout_info import LayoutInfo
from lemma.use_cases.use_cases import UseCases


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
        self.drop_cursor_x, self.drop_cursor_y = None, None
        self.drop_target = Gtk.DropTarget.new(GObject.TYPE_NONE, Gdk.DragAction.COPY)
        self.drop_target.set_gtypes([Gdk.FileList, str, Gdk.Texture])
        self.drop_target.connect('drop', self.on_drop)
        self.drop_target.connect('enter', self.on_drop_enter)
        self.drop_target.connect('motion', self.on_drop_hover)
        self.drop_target.connect('leave', self.on_drop_leave)
        self.content.add_controller(self.drop_target)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_leave)
        self.content.add_controller(self.motion_controller)

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.on_scroll)
        self.scrolling_controller.connect('decelerate', self.on_decelerate)
        self.content.add_controller(self.scrolling_controller)

    def on_realize(self, content, data=None):
        self.model.reset_cursor_blink()

    def on_primary_button_press(self, controller, n_press, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x = self.model.scrolling_position_x + x
        y = self.model.scrolling_position_y + y
        keyboard_state = controller.get_current_event_state() & modifiers

        self.model.selected_click_target = None

        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()

        if y > 0:
            link = document.get_link_at_xy(x, y)
            leaf_layout = document.get_leaf_layout_at_xy(x, y)
            line_layout = document.get_line_layout_at_y(y)
            paragraph_layout = line_layout['parent']
            paragraph = paragraph_layout['node']

            if n_press == 1:
                if int(keyboard_state & modifiers) == Gdk.ModifierType.SHIFT_MASK:
                    UseCases.move_cursor_to_xy(x, y, True)

                elif int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK:
                    UseCases.move_cursor_to_xy(x, y, False)

                else:
                    if leaf_layout != None and NodeTypeDB.focus_on_click(leaf_layout['node']):
                        UseCases.select_node(leaf_layout['node'])
                    else:
                        UseCases.move_cursor_to_xy(x, y, False)
                    if paragraph.style == 'cl' and line_layout == paragraph_layout['children'][0] and y >= paragraph_layout['y'] + 6 and y <= paragraph_layout['y'] + 23 and x >= 1 and x <= 18:
                        UseCases.toggle_checkbox_at_cursor()
                    elif link != None:
                        self.model.selected_click_target = link

            else:
                if link == None or int(keyboard_state & modifiers) != 0:
                    insert = document.cursor.get_insert_node()
                    selection = document.cursor.get_selection_node()
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
        x = self.model.scrolling_position_x + x
        y = self.model.scrolling_position_y + y
        keyboard_state = controller.get_current_event_state() & modifiers

        if keyboard_state == 0:
            x -= LayoutInfo.get_document_padding_left()
            y -= LayoutInfo.get_normal_document_offset()

            if y >= -LayoutInfo.get_subtitle_height():
                document = self.model.document

                link = document.get_link_at_xy(x, y)
                if link == self.model.selected_click_target:
                    UseCases.open_link(link)

    def on_secondary_button_press(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = self.model.document
        x_offset = self.model.scrolling_position_x + x - LayoutInfo.get_document_padding_left()
        y_offset = self.model.scrolling_position_y + y - LayoutInfo.get_normal_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        if y_offset > 0:
            if not document.cursor.has_selection():
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
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        if y - ApplicationState.get_value('document_view_height') > 0:
            height = self.model.document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')
            new_x = self.model.scrolling_position_x
            new_y = min(max(0, height - ApplicationState.get_value('document_view_height')), self.model.scrolling_position_y + y - ApplicationState.get_value('document_view_height'))
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

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

    def handle_drop(self, value, x, y):
        document = WorkspaceRepo.get_workspace().get_active_document()

        ApplicationState.set_value('drop_cursor_position', None)

        if isinstance(value, Gdk.FileList):
            for file in value.get_files():
                file_info = file.query_info('standard::content-type', 0, None)
                path = file.get_parse_name()
                content_type = file_info.get_content_type()

                if content_type.startswith('image/'):
                    texture = Gdk.Texture.new_from_file(file)
                    data = texture.save_to_png_bytes().unref_to_data()
                    image = Image(data)

                    UseCases.move_cursor_to_xy(x, y)
                    UseCases.add_image(image)

        elif isinstance(value, str):
            tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
            link_at_cursor = ApplicationState.get_value('link_at_cursor')
            text = value

            if len(text) < 2000 and urlparse(text.strip()).scheme in ['http', 'https'] and '.' in urlparse(text.strip()).netloc:
                text = xml_helpers.escape(text.strip())
                xml = xml_helpers.embellish_with_link_and_tags(text, text, tags_at_cursor)
            else:
                text = xml_helpers.escape(text)
                xml = xml_helpers.embellish_with_link_and_tags(text, link_at_cursor, tags_at_cursor)

            UseCases.move_cursor_to_xy(x, y)
            UseCases.insert_xml(xml)
            UseCases.scroll_insert_on_screen(animation_type='default')

        elif isinstance(value, Gdk.Texture):
            data = value.save_to_png_bytes().unref_to_data()
            image = Image(data)

            UseCases.move_cursor_to_xy(x, y)
            UseCases.add_image(image)

    def on_drop_enter(self, controller, x, y):
        self.scroll_on_drop_callback_id = self.content.add_tick_callback(self.scroll_on_drop_callback)

        return Gdk.DragAction.COPY

    def on_drop_hover(self, controller, x, y):
        self.drop_cursor_x, self.drop_cursor_y = x, y

        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()
        y += self.model.scrolling_position_y

        UseCases.move_drop_cursor_to_xy(x, y)

        return Gdk.DragAction.COPY

    def on_drop_leave(self, controller):
        if self.scroll_on_drop_callback_id != None:
            self.content.remove_tick_callback(self.scroll_on_drop_callback_id)
            self.scroll_on_drop_callback_id = None

        UseCases.reset_drop_cursor()

    def scroll_on_drop_callback(self, widget, frame_clock):
        x, y = self.drop_cursor_x, self.drop_cursor_y

        if y < 56:
            new_x = self.model.scrolling_position_x
            new_y = max(0, self.model.scrolling_position_y + y - 56)
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        if y - ApplicationState.get_value('document_view_height') > -56:
            height = self.model.document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')
            new_x = self.model.scrolling_position_x
            new_y = min(max(0, height - ApplicationState.get_value('document_view_height')), self.model.scrolling_position_y + y - ApplicationState.get_value('document_view_height') + 56)
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        return True

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0
        if abs(dy) > 0 and abs(dx / dy) >  1: dy = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            document = self.model.document
            height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= ApplicationState.get_value('document_view_width') ** (2/3)
                dy *= ApplicationState.get_value('document_view_height') ** (2/3)
            else:
                dy *= self.model.scrolling_multiplier
                dx *= self.model.scrolling_multiplier
            x = min(0, max(0, self.model.scrolling_position_x + dx))
            y = min(max(0, height - ApplicationState.get_value('document_view_height')), max(0, self.model.scrolling_position_y + dy))

            UseCases.scroll_to_xy(x, y, animation_type=None)
        return

    def on_decelerate(self, controller, vel_x, vel_y):
        if abs(vel_x) > 0 and abs(vel_y / vel_x) >= 1: vel_x = 0
        if abs(vel_y) > 0 and abs(vel_x / vel_y) >  1: vel_y = 0

        UseCases.decelerate_scrolling(self.model.scrolling_position_x, self.model.scrolling_position_y, vel_x, vel_y)

    def on_keypress_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        ctrl_shift_mask = int(Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)

        self.model.set_ctrl_pressed(int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK or Gdk.keyval_name(keyval).startswith('Control'))

        if self.model.document == None: return False

        document = self.model.document
        match (Gdk.keyval_name(keyval).lower(), int(keyboard_state & modifiers)):
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
                UseCases.page(-ApplicationState.get_value('document_view_height') + 100)
            case ('page_down', 0):
                UseCases.page(ApplicationState.get_value('document_view_height') - 100)

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
                UseCases.page(-ApplicationState.get_value('document_view_height') + 100, True)
            case ('page_down', Gdk.ModifierType.SHIFT_MASK):
                UseCases.page(ApplicationState.get_value('document_view_height') - 100, True)

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
                if self.model.application.model_state.multiple_lines_selected:
                    UseCases.change_indentation_level(1)
                elif not document.cursor.has_selection() and self.model.application.model_state.cursor_starts_paragraph:
                    UseCases.change_indentation_level(1)
                else:
                    UseCases.select_next_placeholder()
            case ('iso_left_tab', Gdk.ModifierType.SHIFT_MASK):
                if self.model.application.model_state.multiple_lines_selected:
                    UseCases.change_indentation_level(-1)
                elif not document.cursor.has_selection() and self.model.application.model_state.cursor_starts_paragraph:
                    UseCases.change_indentation_level(-1)
                else:
                    UseCases.select_prev_placeholder()
            case ('escape', _):
                if document.cursor.has_selection():
                    selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
                    if len(selected_nodes) == 1 and selected_nodes[0].type == 'widget':
                        UseCases.remove_selection()
            case ('return', _):
                if not document.cursor.has_selection() and document.cursor.get_insert_node().is_inside_link():
                    UseCases.open_link(document.cursor.get_insert_node().link)
                elif not document.cursor.has_selection():
                    insert_paragraph = document.cursor.get_insert_node().paragraph()
                    paragraph_style = insert_paragraph.style
                    indentation_level = insert_paragraph.indentation_level

                    if paragraph_style in ['ul', 'ol', 'cl']:
                        if len(insert_paragraph.nodes) == 1:
                            UseCases.set_paragraph_style('p')
                            if indentation_level != 0:
                                UseCases.set_indentation_level(0)
                        else:
                            UseCases.insert_xml('\n')
                            UseCases.set_paragraph_style(paragraph_style)
                            if indentation_level != 0:
                                UseCases.set_indentation_level(indentation_level)
                    elif paragraph_style.startswith('h'):
                        UseCases.insert_xml('\n')
                        if len(document.cursor.get_insert_node().paragraph().nodes) == 1:
                            UseCases.set_paragraph_style('p')
                    else:
                        UseCases.insert_xml('\n')

                    UseCases.replace_max_string_before_cursor()
                    UseCases.scroll_insert_on_screen(animation_type='default')
                else:
                    UseCases.insert_xml('\n')
                    UseCases.scroll_insert_on_screen(animation_type='default')
            case ('backspace', _):
                UseCases.backspace()
                UseCases.scroll_insert_on_screen(animation_type='default')
            case ('delete', _):
                UseCases.delete()
                UseCases.scroll_insert_on_screen(animation_type='default')

            case _: return False
        return True

    def on_keyrelease_content(self, controller, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK and not Gdk.keyval_name(keyval).startswith('Control'))

    def on_im_commit(self, im_context, text):
        document = self.model.document

        tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
        link_at_cursor = ApplicationState.get_value('link_at_cursor')
        xml = xml_helpers.embellish_with_link_and_tags(xml_helpers.escape(text), link_at_cursor, tags_at_cursor)

        UseCases.insert_xml(xml)
        if not document.cursor.has_selection() and text.isspace():
            UseCases.replace_max_string_before_cursor()
        UseCases.scroll_insert_on_screen(animation_type='default')
        UseCases.signal_keyboard_input()

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

        self.model.set_cursor_position(x, y)

    def on_hover(self, controller, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.model.set_cursor_position(x, y)

    def on_leave(self, controller):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        self.model.set_ctrl_pressed(int(controller.get_current_event_state() & modifiers) == Gdk.ModifierType.CONTROL_MASK)

        self.model.set_cursor_position(None, None)


