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
import webbrowser

from lemma.document.ast.services import node_inside_link
from lemma.document.document import Document


class DocumentViewController():

    def __init__(self, document_view):
        self.document_view = document_view
        self.view = self.document_view.view
        self.content = self.view.content

        self.view.scrolling_widget.connect('primary_button_press', self.on_primary_button_press)
        self.view.scrolling_widget.connect('primary_button_release', self.on_primary_button_release)

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

        self.view.scrolling_widget.connect('size_changed', self.on_size_change)
        self.view.scrolling_widget.connect('scrolling_offset_changed', self.on_scrolling_offset_change)
        self.view.scrolling_widget.connect('hover_state_changed', self.on_hover_state_changed)
        self.update_cursor()

    def on_primary_button_press(self, content, data):
        x, y, state = data

        self.document_view.selected_link_target = None

        x -= self.view.padding_left
        y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height

        if y < -self.view.subtitle_height:
            self.document_view.init_renaming()
        elif y > 0:
            document = self.document_view.document

            link = document.get_link_at_xy(x, y)
            if state == 0 and link != None:
                self.document_view.selected_link_target = link.target
            else:
                document.add_command('move_cursor_to_xy', x, y)
            self.content.grab_focus()

    def on_primary_button_release(self, content, data):
        x, y, state = data

        if state == 0:
            x -= self.view.padding_left
            y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height

            if y >= -self.view.subtitle_height:
                document = self.document_view.document

                link = document.get_link_at_xy(x, y)
                if link != None and link.target == self.document_view.selected_link_target:
                    self.open_link(link.target)

    def on_modifiers_change(self, controller, state):
        self.update_cursor()

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

            case ('return', _):
                if not document.ast.has_selection() and node_inside_link(document.ast.get_insert_node()):
                    self.open_link(document.ast.get_insert_node().link.target)
                else:
                    document.add_command('newline')
            case ('backspace', _): document.add_command('backspace')
            case ('delete', _): document.add_command('delete')

            case _: return False
        return True

    def on_im_commit(self, im_context, text):
        if self.document_view.document == None: return False

        self.document_view.document.add_command('insert_text', text)

    def on_focus_in(self, controller):
        self.im_context.focus_in()
        self.view.scrolling_widget.queue_draw()
        self.update_cursor()

    def on_focus_out(self, controller):
        self.im_context.focus_out()
        self.view.scrolling_widget.queue_draw()
        self.update_cursor()

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
        x -= self.view.padding_left
        y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height
        link = None

        if y < -self.view.subtitle_height:
            self.content.set_cursor_from_name('text')
        elif y > 0:
            document = self.document_view.document
            link = document.get_link_at_xy(x, y)
            if link != None:
                self.content.set_cursor_from_name('pointer')
            else:
                self.content.set_cursor_from_name('text')
        else:
            self.content.set_cursor_from_name('default')

        if link != None:
            self.view.link_overlay.set_text(link.target)
            self.view.link_overlay.set_visible(True)
        else:
            self.view.link_overlay.set_visible(False)
        self.view.link_overlay.queue_draw()

    def open_link(self, link_target):
        workspace = self.document_view.workspace

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


