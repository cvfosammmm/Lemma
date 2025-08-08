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
from gi.repository import Gdk, Pango, PangoCairo

from lemma.services.color_manager import ColorManager
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
from lemma.history.history import History
from lemma.ui.cairo import rounded_rectangle
import lemma.services.timer as timer


class DocumentHistory(object):

    def __init__(self, main_window):
        self.view = main_window.history_view

        self.layout = Pango.Layout(self.view.get_pango_context())
        self.layout.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout.set_alignment(Pango.Alignment.CENTER)
        self.font_desc_normal = self.layout.get_context().get_font_description()
        self.font_desc_bold = self.layout.get_context().get_font_description()
        self.font_desc_bold.set_weight(Pango.Weight.BOLD)

        self.items = list()
        self.selected_document = None

        self.view.content.set_draw_func(self.draw)
        self.view.scrolling_widget.connect('primary_button_press', self.on_primary_button_press)
        self.view.scrolling_widget.connect('primary_button_release', self.on_primary_button_release)

    @timer.timer
    def update(self):
        self.update_size()
        self.scroll_active_document_on_screen()
        self.view.content.queue_draw()

    @timer.timer
    def update_size(self):
        mode = ApplicationState.get_value('mode')
        width = 0
        self.items = list()
        for i, document in enumerate(History.documents):
            self.items.append((i, document, width))
            width += self.get_item_extents(document.title).width / Pango.SCALE
            width += 37
            if i == History.active_document_index and mode == 'draft':
                break
        if mode == 'draft':
            width += self.get_item_extents('New Document').width / Pango.SCALE
            width += 37
        width += 72
        self.view.scrolling_widget.set_size(width, 1)

    @timer.timer
    def scroll_active_document_on_screen(self):
        if self.view.scrolling_widget.adjustment_x.get_upper() < self.view.scrolling_widget.scrolling_offset_x + self.view.scrolling_widget.width or History.active_document_index == len(self.items) - 1:
            self.view.scrolling_widget.scroll_to_position((self.view.scrolling_widget.adjustment_x.get_upper(), 0))
            return

        if History.active_document_index != None:
            i, document, document_offset = self.items[History.active_document_index]
            if document_offset < self.view.scrolling_widget.scrolling_offset_x:
                self.view.scrolling_widget.scroll_to_position((document_offset, 0))
                return

            i, document, document_offset = self.items[History.active_document_index + 1]
            if document_offset > self.view.scrolling_widget.scrolling_offset_x + self.view.scrolling_widget.width:
                self.view.scrolling_widget.scroll_to_position((document_offset - self.view.scrolling_widget.width - 1, 0))
                return

    def on_primary_button_press(self, scrolling_widget, data):
        x_offset, y_offset, state = data

        if state == 0:
            document = self.get_document_at_cursor()
            if document != None:
                self.set_selected_document(document)

    def on_primary_button_release(self, scrolling_widget, data):
        x_offset, y_offset, state = data

        document = self.get_document_at_cursor()
        if document != None and document == self.selected_document:
            UseCases.set_active_document(document, update_history=False, scroll_to_top=False)
        self.set_selected_document(None)

    def set_selected_document(self, document):
        if document != self.selected_document:
            self.selected_document = document
            self.view.content.queue_draw()

    def draw(self, widget, ctx, width, height):
        mode = ApplicationState.get_value('mode')
        document_at_cursor = self.get_document_at_cursor()
        offset = -1 - int(self.view.scrolling_widget.scrolling_offset_x)
        hover_color = ColorManager.get_ui_color('history_hover')
        selected_color = ColorManager.get_ui_color('history_active_bg')
        fg_color = ColorManager.get_ui_color('history_fg')

        for i, document, document_offset in self.items:
            is_active = (i == History.active_document_index)
            extents = self.get_item_extents(document.title)
            px_width = extents.width / Pango.SCALE + 37
            font_desc = self.font_desc_bold if (is_active and mode != 'draft') else self.font_desc_normal

            if document == document_at_cursor:
                if document == self.selected_document:
                    Gdk.cairo_set_source_rgba(ctx, selected_color)
                else:
                    Gdk.cairo_set_source_rgba(ctx, hover_color)
                rounded_rectangle(ctx, offset, 6, px_width, 35, 6)
                ctx.fill()

            ctx.move_to(offset + 18, int((height - extents.height / Pango.SCALE) / 2) - 1)
            self.layout.set_font_description(font_desc)
            self.layout.set_width(extents.width)
            self.layout.set_text(document.title)
            Gdk.cairo_set_source_rgba(ctx, fg_color)
            PangoCairo.show_layout(ctx, self.layout)
            self.draw_divider(ctx, offset, height)

            offset += px_width

            if is_active and mode == 'draft':
                break

        if mode == 'draft':
            extents = self.get_item_extents('New Document')
            ctx.move_to(offset + 18, int((height - extents.height / Pango.SCALE) / 2) - 1)
            self.layout.set_font_description(self.font_desc_bold)
            self.layout.set_width(extents.width)
            self.layout.set_text('New Document')
            Gdk.cairo_set_source_rgba(ctx, fg_color)
            PangoCairo.show_layout(ctx, self.layout)
            self.draw_divider(ctx, offset, height)

    def draw_divider(self, ctx, offset, height):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('border_1'))
        ctx.rectangle(offset, 9, 1, height - 18)
        ctx.fill()

    def get_document_at_cursor(self):
        y = self.view.scrolling_widget.cursor_y
        x = self.view.scrolling_widget.cursor_x
        if y == None or x == None: return None
        if y < 6 or y > 41: return None
        x += self.view.scrolling_widget.scrolling_offset_x

        offset = 0
        for i, document, document_offset in self.items:
            extents = self.get_item_extents(document.title)
            offset += extents.width / Pango.SCALE + 37
            if x < offset: return document
        return None

    def get_item_extents(self, text):
        self.layout.set_font_description(self.font_desc_bold)
        self.layout.set_width(-1)
        self.layout.set_text(text)
        return self.layout.get_extents()[1]


