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

from lemma.infrastructure.font_manager import FontManager
from lemma.infrastructure.color_manager import ColorManager


class AutocompleteWidget(object):

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.document_view = main_window.document_view
        self.view = self.document_view.autocomplete

        self.line_height = None
        self.height = None
        self.shortcutsbar_height = None
        self.x_position, self.y_position = (None, None)
        self.document = None
        self.search_terms = []
        self.suggested_documents = list()

        self.view.list.set_draw_func(self.draw)
        self.view.entry.connect('changed', self.on_entry_changed)

        self.set_document(workspace.get_active_document())
        self.workspace.connect('new_active_document', self.on_new_active_document)

        self.update()

    def on_new_active_document(self, workspace, document=None):
        self.set_document(document)

    def set_document(self, document):
        if self.document != None:
            self.document.disconnect('changed', self.on_change)

        self.document = document
        self.update()

        if document != None:
            self.document.connect('changed', self.on_change)

    def on_change(self, document):
        self.update()

    def on_entry_changed(self, entry, data=None):
        self.search_terms = entry.get_text().split()
        self.update()

    def update(self):
        self.suggested_documents = []
        for document in self.workspace.documents:
            if self.is_match(document):
                self.suggested_documents.append(document)

        self.update_size()
        self.update_position()
        self.update_margins()

        self.view.set_visible(self.position_is_visible()) #TODO self.model.is_active and 
        self.view.queue_draw()

    def update_size(self):
        self.line_height = 30 #TODO
        self.char_width = 10 #TODO
        self.height = len(self.suggested_documents) * self.line_height
        self.width = 50 * self.char_width
        self.view.scrolled_window.set_size_request(self.width, min(5 * self.line_height, self.height))
        self.view.list.set_size_request(self.width, self.height)

    def update_position(self):
        self.x_position, self.y_position = self.document.ast.get_insert_node().get_xy()

    def update_margins(self):
        padding_top = self.document_view.padding_top + self.document_view.title_height + self.document_view.subtitle_height + self.document_view.title_buttons_height
        scrolling_offset_y = self.document.clipping.offset_y
        y_position = self.y_position + padding_top - scrolling_offset_y + FontManager.get_cursor_height() + FontManager.get_cursor_offset()
        vertical_cutoff = self.document_view.get_allocated_height() - self.height
        horizontal_cutoff = self.document_view.get_allocated_width() - self.view.get_allocated_width()

        if y_position >= 0 and y_position <= vertical_cutoff:
            self.view.set_margin_top(y_position)
        else:
            self.view.set_margin_top(y_position - self.height - FontManager.get_cursor_height())

        if self.x_position >= 0 and self.x_position <= horizontal_cutoff:
            self.view.set_margin_start(self.x_position + self.document_view.padding_left)
        else:
            self.view.set_margin_start(self.document_view.get_allocated_width() - self.view.get_allocated_width())

    def position_is_visible(self):
        padding_top = self.document_view.padding_top + self.document_view.title_height + self.document_view.subtitle_height + self.document_view.title_buttons_height
        scrolling_offset_y = self.document.clipping.offset_y
        y_position = self.y_position + padding_top - scrolling_offset_y + FontManager.get_cursor_offset()
        vertical_cutoff = self.document_view.get_allocated_height() - self.height
        horizontal_cutoff = self.document_view.get_allocated_width() - self.view.get_allocated_width()

        return ((y_position >= 0) and (y_position <= self.document_view.get_allocated_height() - FontManager.get_cursor_height()))

    def draw(self, drawing_area, ctx, width, height):
        sidebar_fg_1 = ColorManager.get_ui_color('sidebar_fg_1')
        sidebar_fg_2 = ColorManager.get_ui_color('sidebar_fg_2')
        bg_color = ColorManager.get_ui_color('sidebar_bg_1')
        hover_color = ColorManager.get_ui_color('sidebar_hover')
        selected_color = ColorManager.get_ui_color('sidebar_selection')
        active_bg_color = ColorManager.get_ui_color('sidebar_active_bg')
        active_fg_color = ColorManager.get_ui_color('sidebar_active_fg')

        self.view.layout.set_width((width - 80) * Pango.SCALE)

        Gdk.cairo_set_source_rgba(ctx, bg_color)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        Gdk.cairo_set_source_rgba(ctx, sidebar_fg_1)

        for i, document in enumerate(self.suggested_documents):
            highlight_active = (document == self.workspace.active_document and self.workspace.mode == 'documents')
            if highlight_active:
                title_color = active_fg_color
                teaser_color = active_fg_color
                date_color = active_fg_color
            else:
                title_color = sidebar_fg_1
                teaser_color = sidebar_fg_1
                date_color = sidebar_fg_1

            '''if i == self.selected_index:
                Gdk.cairo_set_source_rgba(ctx, selected_color)
                ctx.rectangle(0, self.view.line_height * i, width, self.view.line_height)
                ctx.fill()
            elif not highlight_active and i == self.get_item_at_cursor():
                Gdk.cairo_set_source_rgba(ctx, hover_color)
                ctx.rectangle(0, self.view.line_height * i, width, self.view.line_height)
                ctx.fill()
            if highlight_active:
                Gdk.cairo_set_source_rgba(ctx, active_bg_color)
                ctx.rectangle(0, self.view.line_height * i, width, self.view.line_height)
                ctx.fill()'''#TODO

            title_text = document.title

            Gdk.cairo_set_source_rgba(ctx, title_color)
            ctx.move_to(15, self.line_height * i + 12)
            self.view.layout.set_text(title_text)
            PangoCairo.show_layout(ctx, self.view.layout)

        '''def draw(self, drawing_area, ctx, width, height):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('ac_bg'))
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        return #TODO

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('ac_selection_bg'))
        ctx.rectangle(0, self.line_height * (si - fi), width, self.line_height)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('ac_text'))
        for i, item in enumerate(self.items[fi:fi + 5]):
            ctx.move_to(0, i * self.line_height)
            self.draw_item(ctx, item)'''

    def draw_item(self, ctx, item):
        offset = len(self.model.model.current_word)
        command_text = '<b>' + GLib.markup_escape_text(item['command'][:offset]) + '</b>'
        command_text += GLib.markup_escape_text(item['command'][offset:])

        self.dotlabels = filter(None, item['dotlabels'].split('###'))
        for dotlabel in self.dotlabels:
            command_text = command_text.replace('•', '<span alpha="60%">' + GLib.markup_escape_text(dotlabel) + '</span>', 1)

        self.layout.set_markup(command_text)
        PangoCairo.show_layout(ctx, self.layout)

    def is_match(self, document):
        if len(self.search_terms) == 0: return True
        return min(map(lambda x: x in document.title, self.search_terms))


