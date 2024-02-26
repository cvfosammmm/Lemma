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
from gi.repository import Gtk, Gdk, cairo, PangoCairo

import datetime

from lemma.app.font_manager import FontManager
from lemma.app.color_manager import ColorManager
from lemma.layout.layout import *


class DocumentViewPresenter():

    def __init__(self, model):
        self.model = model
        self.view = self.model.view
        self.content = self.view.content
        self.cursor_coords = None

        self.content.set_draw_func(self.draw)

        self.model.connect('changed', self.on_change)

    def on_change(self, model):
        if self.model.document == None: return

        height = self.model.document.layout.height + self.view.padding_bottom + self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height

        self.view.scrolling_widget.adjustment_x.set_upper(1)
        self.view.scrolling_widget.adjustment_y.set_upper(height)
        self.view.scrolling_widget.queue_draw()

    def draw(self, widget, ctx, width, height):
        if self.model.document == None: return

        self.cursor_coords = None
        scrolling_offset = self.view.scrolling_widget.adjustment_y.get_value()

        self.draw_title(ctx, self.view.padding_left, self.view.padding_top - scrolling_offset)

        self.draw_box(ctx, self.model.document.layout, self.view.padding_left, self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height - scrolling_offset)

        self.draw_cursor(ctx)

    def draw_title(self, ctx, offset_x, offset_y):
        ctx.move_to(offset_x, offset_y)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('title_color'))
        self.view.layout_title.set_text(self.model.document.title)
        PangoCairo.show_layout(ctx, self.view.layout_title)

        ctx.move_to(offset_x, offset_y + self.view.title_height + 8)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('description'))

        datetime_last_modified = datetime.datetime.fromtimestamp(self.model.document.last_modified)
        self.view.layout_subtitle.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))
        PangoCairo.show_layout(ctx, self.view.layout_subtitle)

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('border_1'))
        ctx.rectangle(offset_x, offset_y + self.view.title_height, self.view.title_width, 1)
        ctx.fill()

    def draw_box(self, ctx, box, offset_x, offset_y):
        if isinstance(box, BoxVContainer):
            for child in box.children:
                self.draw_box(ctx, child, offset_x, offset_y)
                offset_y += child.height

        elif isinstance(box, BoxHContainer):
            for child in box.children:
                self.draw_box(ctx, child, offset_x, offset_y)
                offset_x += child.width

        elif isinstance(box, BoxGlyph):
            if box.is_selected:
                ctx.set_source_rgb(0, 0, 1)
                ctx.rectangle(offset_x, offset_y, box.width, box.height)
                ctx.fill()

            surface = FontManager.get_surface(box.char)
            if surface != None:
                ctx.set_source_surface(surface, offset_x + box.left, offset_y + box.height + box.top)
                pattern = ctx.get_source()
                pattern.set_filter(cairo.Filter.BEST)
                Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('text'))
                ctx.mask(pattern)
                ctx.fill()

        elif isinstance(box, BoxInsert):
            self.cursor_coords = (offset_x + box.left, offset_y + box.top, 1, box.height)

    def draw_cursor(self, ctx):
        if self.cursor_coords == None: return
        if not self.content.has_focus(): return

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('cursor'))
        ctx.rectangle(*self.cursor_coords)
        ctx.fill()


