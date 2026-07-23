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
import time, os.path

import lemma.services.xml_helpers as xml_helpers
from lemma.widgets.factory import WidgetFactory
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.application_state.application_state import ApplicationState
from lemma.services.settings import Settings
from lemma.services.node_type_db import NodeTypeDB
from lemma.services.xml_exporter import XMLExporter
from lemma.services.layout_info import LayoutInfo
from lemma.services.files import Files
from lemma.ui.shortcuts import Shortcuts
from lemma.use_cases.use_cases import UseCases
from lemma.use_cases.queries import Queries
from lemma.services.message_bus import MessageBus
import lemma.services.timer as timer


class Pointer():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.view = main_window.document_view
        self.content = self.view.content

        self.pointer_x, self.pointer_y = None, None
        self.pointer_name = 'default'
        self.drop_cursor_x, self.drop_cursor_y = -1, -1
        self.link_target_at_pointer = None
        self.selected_click_target = None

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.content.add_controller(self.primary_click_controller)

        self.secondary_click_controller = Gtk.GestureClick()
        self.secondary_click_controller.set_button(3)
        self.secondary_click_controller.connect('pressed', self.on_secondary_button_press)
        self.content.add_controller(self.secondary_click_controller)

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

    @timer.timer
    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            self.drop_cursor_x, self.drop_cursor_y = -1, -1

        self.update_pointer()

    def update_pointer(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None:
            self.content.set_cursor_from_name('default')
            return
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()
        x = scrolling_pos_x + (self.pointer_x if self.pointer_x != None else 0)
        y = scrolling_pos_y + (self.pointer_y if self.pointer_y != None else 0)
        x -= LayoutInfo.get_document_padding_left()
        y -= Queries.get_document_offset()

        if y > 0:
            line_layout = document_layout.get_line_layout_at_y(y)
            leaf_layout = document_layout.get_leaf_layout_at_xy(x, y)
            paragraph_layout = line_layout['parent']
            paragraph = paragraph_layout['node']

            link = None
            if leaf_layout != None and leaf_layout['node'] != None and leaf_layout['node'].link != None:
                link = leaf_layout['node'].link
            self.link_target_at_pointer = link

            indentation = LayoutInfo.get_indentation('cl', paragraph.indentation_level)
            x_start = indentation - 35
            x_end = indentation - 16

            if paragraph.style == 'cl' and line_layout == paragraph_layout['children'][0] and y >= paragraph_layout['y'] + line_layout['height'] - 23 and y <= paragraph_layout['y'] + line_layout['height'] - 4 and x >= x_start and x <= x_end:
                pointer_name = 'default'
            elif leaf_layout != None:
                node = leaf_layout['node']
                if node != None:
                    if node.link != None and not ApplicationState.get_ctrl_pressed():
                        pointer_name = 'pointer'
                    elif node.type == 'widget':
                        pointer_name = self.application.widget_manager.get_cursor_name(node.value)
                    elif node.type == 'placeholder':
                        pointer_name = 'default'
                    else:
                        pointer_name = 'text'
                else:
                    pointer_name = 'text'
            else:
                pointer_name = 'text'
        else:
            pointer_name = 'default'
            self.link_target_at_pointer = None

        if pointer_name != self.pointer_name:
            self.pointer_name = pointer_name
            self.content.set_cursor_from_name(pointer_name)

    def on_primary_button_press(self, controller, n_press, x, y):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()
        x += scrolling_pos_x - LayoutInfo.get_document_padding_left()
        y += scrolling_pos_y - Queries.get_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        self.selected_click_target = (x, y)

        if y > 0:
            leaf_layout = document_layout.get_leaf_layout_at_xy(x, y)
            link = leaf_layout['node'].link if leaf_layout != None else None

            if leaf_layout != None and leaf_layout['node'].type == 'widget':
                self.application.widget_manager.on_primary_button_press(leaf_layout['node'].value, n_press, x, y)
                if n_press == 1:
                    UseCases.select_node(leaf_layout['node'])

            elif n_press == 1:
                if int(keyboard_state & modifiers) == Gdk.ModifierType.SHIFT_MASK:
                    UseCases.move_cursor_to_xy(x, y, True)
                    UseCases.update_implicit_x_position()

                elif int(keyboard_state & modifiers) == Gdk.ModifierType.CONTROL_MASK:
                    UseCases.move_cursor_to_xy(x, y, False)
                    UseCases.update_implicit_x_position()

                else:
                    if leaf_layout != None and NodeTypeDB.focus_on_click(leaf_layout['node']):
                        UseCases.select_node(leaf_layout['node'])
                    else:
                        UseCases.move_cursor_to_xy(x, y, False)
                        UseCases.update_implicit_x_position()

            else:
                if link == None or int(keyboard_state & modifiers) != 0:
                    insert = document.get_insert_node()
                    selection = document.get_selection_node()
                    paragraph_start, paragraph_end = insert.paragraph_bounds()
                    if insert == paragraph_start and selection == paragraph_end or insert == paragraph_end and selection == paragraph_start:
                        UseCases.move_cursor_to_xy(x, y, False)
                        UseCases.update_implicit_x_position()
                    else:
                        UseCases.extend_selection()
                        UseCases.update_implicit_x_position()

            self.content.grab_focus()

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press % 3 != 1: return

        modifiers = Gtk.accelerator_get_default_mod_mask()
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()
        x += scrolling_pos_x - LayoutInfo.get_document_padding_left()
        y += scrolling_pos_y - Queries.get_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        if keyboard_state == 0:
            leaf_layout_at_press = document_layout.get_leaf_layout_at_xy(*self.selected_click_target)
            link_at_press = leaf_layout_at_press['node'].link if leaf_layout_at_press != None else None
            leaf_layout_at_release = document_layout.get_leaf_layout_at_xy(x, y)
            link_at_release = leaf_layout_at_release['node'].link if leaf_layout_at_release != None else None

            if link_at_press == link_at_release and link_at_release != None:
                UseCases.open_link(link_at_release)
                return

            x_at_press, y_at_press = self.selected_click_target
            line_layout_at_press = document_layout.get_line_layout_at_y(y_at_press)
            paragraph_layout_at_press = line_layout_at_press['parent']

            line_layout_at_release = document_layout.get_line_layout_at_y(y)
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
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()
        x_offset = scrolling_pos_x + x - LayoutInfo.get_document_padding_left()
        y_offset = scrolling_pos_y + y - Queries.get_document_offset()
        keyboard_state = controller.get_current_event_state() & modifiers

        if y_offset > 0:
            if not document.has_selection():
                leaf_layout = document_layout.get_leaf_layout_at_xy(x_offset, y_offset)
                if keyboard_state == 0 and leaf_layout != None and NodeTypeDB.focus_on_click(leaf_layout['node']):
                    UseCases.select_node(leaf_layout['node'])
                else:
                    UseCases.move_cursor_to_xy(x_offset, y_offset, False)
                    UseCases.update_implicit_x_position()
            self.application.context_menu_document.popup_at_cursor(x, y)

    def on_drag_begin(self, gesture, x, y, data=None):
        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()

        x -= LayoutInfo.get_document_padding_left()
        y -= Queries.get_document_offset()
        y += scrolling_pos_y

        if y <= 0:
            gesture.reset()

    def on_drag_update(self, gesture, x, y, data=None):
        if x == 0 and y == 0: return

        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        start_point = gesture.get_start_point()
        x, y = start_point.x + x, start_point.y + y
        view_width, view_height = ApplicationState.get_view_size()
        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()

        if y < 0:
            new_x = scrolling_pos_x
            new_y = max(0, scrolling_pos_y + y)
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        if y - view_height > 0:
            height = document_layout.get_height() + LayoutInfo.get_document_padding_bottom() + Queries.get_document_offset()
            new_x = scrolling_pos_x
            new_y = min(max(0, height - view_height), scrolling_pos_y + y - view_height)
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        x -= LayoutInfo.get_document_padding_left()
        y -= Queries.get_document_offset()
        y += scrolling_pos_y

        UseCases.move_cursor_to_xy(x, y, True)
        UseCases.update_implicit_x_position()

    def on_drag_end(self, gesture, x, y, data=None):
        pass

    def on_drop(self, controller, value, x, y):
        if self.scroll_on_drop_callback_id != None:
            self.content.remove_tick_callback(self.scroll_on_drop_callback_id)
            self.scroll_on_drop_callback_id = None

        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()
        x -= LayoutInfo.get_document_padding_left()
        y -= Queries.get_document_offset()
        y += scrolling_pos_y

        self.handle_drop(value, x, y)
        controller.reset()

    def handle_drop(self, value, x, y):
        document = WorkspaceRepo.get_workspace().get_active_document()

        self.drop_cursor_x, self.drop_cursor_y = -1, -1

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
                        Files.write_bytes_to_document_file(filename, texture.save_to_png_bytes().unref_to_data())
                        image = WidgetFactory.make_widget('image', {'filename': filename})

                        UseCases.move_cursor_to_xy(x, y)
                        UseCases.add_widget(image)
                        UseCases.update_implicit_x_position()

                        done_with_file = True

                if not done_with_file:
                    if os.path.isfile(path):
                        filename = Files.add_file_to_doc_folder_with_distinct_name(document, path)
                        widget = WidgetFactory.make_widget('attachment', {'filename': filename})

                        UseCases.move_cursor_to_xy(x, y)
                        UseCases.add_widget(widget)
                        UseCases.update_implicit_x_position()

        elif isinstance(value, str):
            text = value

            if len(text) < 2000 and urlparse(text.strip()).scheme in ['http', 'https'] and '.' in urlparse(text.strip()).netloc:
                text = xml_helpers.escape(text.strip())
                xml = xml_helpers.embellish_with_link_and_tags(text, text, set())
            else:
                xml = xml_helpers.escape(text)

            UseCases.move_cursor_to_xy(x, y)
            UseCases.insert_xml(xml)
            UseCases.update_implicit_x_position()

        elif isinstance(value, Gdk.Texture):
            texture = value
            filename = Files.get_distinct_document_file_name(document, '.png')
            Files.write_bytes_to_document_file(filename, texture.save_to_png_bytes().unref_to_data())
            image = WidgetFactory.make_widget('image', {'filename': filename})

            UseCases.move_cursor_to_xy(x, y)
            UseCases.add_widget(image)
            UseCases.update_implicit_x_position()

    def on_drop_enter(self, controller, x, y):
        self.scroll_on_drop_callback_id = self.content.add_tick_callback(self.scroll_on_drop_callback)

        return Gdk.DragAction.COPY

    def on_drop_hover(self, controller, x, y):
        self.drop_cursor_x, self.drop_cursor_y = x, y
        self.view.content.queue_draw()

        return Gdk.DragAction.COPY

    def on_drop_leave(self, controller):
        if self.scroll_on_drop_callback_id != None:
            self.content.remove_tick_callback(self.scroll_on_drop_callback_id)
            self.scroll_on_drop_callback_id = None
        self.drop_cursor_x, self.drop_cursor_y = -1, -1

    def scroll_on_drop_callback(self, widget, frame_clock):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        x, y = self.drop_cursor_x, self.drop_cursor_y
        view_width, view_height = ApplicationState.get_view_size()
        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()

        if y < 56:
            new_x = scrolling_pos_x
            new_y = max(0, scrolling_pos_y + y - 56)
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        if y - view_height > -56:
            height = document_layout.get_height() + LayoutInfo.get_document_padding_bottom() + Queries.get_document_offset()
            new_x = scrolling_pos_x
            new_y = min(max(0, height - view_height), scrolling_pos_y + y - view_height + 56)
            UseCases.scroll_to_xy(new_x, new_y, animation_type=None)

        return True

    def on_enter(self, controller, x, y):
        self.pointer_x, self.pointer_y = x, y

    def on_hover(self, controller, x, y):
        self.pointer_x, self.pointer_y = x, y
        self.view.scrollbar_vertical.ping()

    def on_leave(self, controller):
        self.pointer_x, self.pointer_y = None, None


