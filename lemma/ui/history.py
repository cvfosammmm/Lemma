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
from gi.repository import Gtk, Gdk, Pango, PangoCairo

from lemma.services.message_bus import MessageBus
from lemma.services.color_manager import ColorManager
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.ui.helpers.cairo import rounded_rectangle
import lemma.services.timer as timer


class History(object):

    def __init__(self, main_window):
        self.view = main_window.history_view

        self.layout = Pango.Layout(self.view.get_pango_context())
        self.layout.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout.set_alignment(Pango.Alignment.CENTER)
        self.font_desc_normal = self.layout.get_context().get_font_description()
        self.font_desc_bold = self.layout.get_context().get_font_description()
        self.font_desc_bold.set_weight(Pango.Weight.BOLD)

        self.items = list()
        self.active_document_index = None
        self.selected_index = None

        self.size_cache = dict()

        self.view.content.set_draw_func(self.draw)
        self.view.scrolling_widget.observe('primary_button_press', self.on_primary_button_press)
        self.view.scrolling_widget.observe('primary_button_release', self.on_primary_button_release)

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.view.content.add_controller(self.primary_click_controller)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'document_title_changed')
        MessageBus.subscribe(self, 'mode_set')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'document_title_changed' in messages or 'mode_set' in messages:
            self.update()

    @timer.timer
    def update(self):
        self.update_size()
        self.scroll_active_document_on_screen()
        self.view.content.queue_draw()

    @timer.timer
    def update_size(self):
        workspace = WorkspaceRepo.get_workspace()
        history = [DocumentRepo.get_stub_by_id(doc_id) for doc_id in workspace.get_history()]
        mode = workspace.get_mode()

        total_width = 0
        self.items = list()

        for i, document_stub in enumerate(history):
            if document_stub['title'] not in self.size_cache:
                self.size_cache[document_stub['title']] = self.get_item_extents(document_stub['title']).width / Pango.SCALE + 37
            document_width = self.size_cache[document_stub['title']]
            self.items.append((i, document_stub, total_width, document_width))
            total_width += document_width
            if document_stub['id'] == workspace.get_active_document_id():
                self.active_document_index = i
                if mode == 'draft':
                    break
        if mode == 'draft':
            total_width += self.get_item_extents('New Document').width / Pango.SCALE + 37
        total_width += 72

        self.view.scrolling_widget.set_size(total_width, 1)

    @timer.timer
    def scroll_active_document_on_screen(self):
        if self.view.scrolling_widget.adjustment_x.get_upper() < self.view.scrolling_widget.scrolling_offset_x + self.view.scrolling_widget.width or self.active_document_index == len(self.items) - 1:
            self.view.scrolling_widget.scroll_to_position((self.view.scrolling_widget.adjustment_x.get_upper(), 0))
            return

        if self.active_document_index != None:
            i, document_stub, document_offset, document_width = self.items[self.active_document_index]
            if document_offset < self.view.scrolling_widget.scrolling_offset_x:
                self.view.scrolling_widget.scroll_to_position((document_offset, 0))
                return

            i, document_stub, document_offset, document_width = self.items[self.active_document_index + 1]
            if document_offset > self.view.scrolling_widget.scrolling_offset_x + self.view.scrolling_widget.width:
                self.view.scrolling_widget.scroll_to_position((document_offset - self.view.scrolling_widget.width - 1, 0))
                return

    def on_primary_button_press(self, controller, n_press, x, y):
        if n_press != 1: return

        hover_index = self.get_hover_index()
        if hover_index != None:
            self.set_selected_index(hover_index)

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press != 1: return

        hover_index = self.get_hover_index()
        if hover_index != None and hover_index == self.selected_index:
            UseCases.set_active_document(self.items[hover_index][1]['id'], update_history=False)
        self.set_selected_index(None)

    def set_selected_index(self, index):
        if index != self.selected_index:
            self.selected_index = index
            self.view.content.queue_draw()

    @timer.timer
    def draw(self, widget, ctx, width, height):
        workspace = WorkspaceRepo.get_workspace()
        mode = workspace.get_mode()

        hover_index = self.get_hover_index()
        scrolling_offset = int(self.view.scrolling_widget.scrolling_offset_x) + 1

        draft_offset = 0

        if self.active_document_index != None or mode != 'draft':
            for i, document_stub, document_offset, document_width in self.items:
                is_active = (i == self.active_document_index)
                if document_offset + document_width >= self.view.scrolling_widget.scrolling_offset_x and document_offset <= self.view.scrolling_widget.scrolling_offset_x + width:
                    font_desc = self.font_desc_bold if (is_active and mode != 'draft') else self.font_desc_normal

                    if i == hover_index:
                        if i == self.selected_index:
                            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('history_active_bg'))
                        else:
                            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('history_hover'))
                        rounded_rectangle(ctx, document_offset - scrolling_offset, 6, document_width, 35, 6)
                        ctx.fill()

                    ctx.move_to(document_offset - scrolling_offset, 13)
                    self.layout.set_font_description(font_desc)
                    self.layout.set_width(document_width * Pango.SCALE)
                    self.layout.set_text(str(document_stub['title']))
                    Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('headerbar_fg_2'))
                    PangoCairo.show_layout(ctx, self.layout)
                    self.draw_divider(ctx, document_offset - scrolling_offset, height)

                if is_active and mode == 'draft':
                    draft_offset = document_offset + document_width + 1 - scrolling_offset
                    break

        if mode == 'draft':
            extents = self.get_item_extents('New Document')
            ctx.move_to(draft_offset, 13)
            self.layout.set_font_description(self.font_desc_bold)
            self.layout.set_width(extents.width + 37 * Pango.SCALE)
            self.layout.set_text('New Document')
            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('headerbar_fg_2'))
            PangoCairo.show_layout(ctx, self.layout)

            if draft_offset > 0:
                self.draw_divider(ctx, draft_offset, height)

    def draw_divider(self, ctx, offset, height):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('border_1'))
        ctx.rectangle(offset, 9, 1, height - 18)
        ctx.fill()

    def get_hover_index(self):
        y = self.view.scrolling_widget.cursor_y
        x = self.view.scrolling_widget.cursor_x
        if y == None or x == None: return None
        if y < 6 or y > 41: return None
        x += self.view.scrolling_widget.scrolling_offset_x

        offset = 0
        for i, document_stub, document_offset, document_width in self.items:
            if x >= document_offset and x < document_offset + document_width:
                return i
        return None

    @timer.timer
    def get_item_extents(self, text):
        self.layout.set_font_description(self.font_desc_bold)
        self.layout.set_width(-1)
        self.layout.set_text(text)
        return self.layout.get_extents()[1]


