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

import datetime

from lemma.app.service_locator import ServiceLocator
from lemma.app.color_manager import ColorManager
import lemma.helpers.helpers as helpers


class DocumentListPresenter(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.content.set_draw_func(self.draw)

        self.model.connect('changed', self.on_change)
        self.model.connect('selected_item_changed', self.on_selected_item_change)

    def on_change(self, model):
        self.view.scrolling_widget.set_size(1, max(self.model.count() * self.view.line_height, 1))
        self.view.scrolling_widget.queue_draw()

    def on_selected_item_change(self, model):
        self.view.content.queue_draw()

    #@helpers.timer
    def draw(self, widget, ctx, width, height):
        title_color = ColorManager.get_ui_color('sidebar_fg_1')
        teaser_color = ColorManager.get_ui_color('sidebar_fg_1')
        bg_color = ColorManager.get_ui_color('sidebar_bg_1')
        hover_color = ColorManager.get_ui_color('sidebar_hover')
        selected_color = ColorManager.get_ui_color('sidebar_selection')
        active_bg_color = ColorManager.get_ui_color('sidebar_active_bg')
        active_fg_color = ColorManager.get_ui_color('sidebar_active_fg')

        scrolling_offset = self.view.scrolling_widget.adjustment_y.get_value()

        self.view.layout_header.set_width((width - 80) * Pango.SCALE)
        self.view.layout_date.set_width((width - 30) * Pango.SCALE)
        self.view.layout_teaser.set_width((width - 30) * Pango.SCALE)

        Gdk.cairo_set_source_rgba(ctx, bg_color)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        Gdk.cairo_set_source_rgba(ctx, title_color)

        for i, document in enumerate(self.model.documents):
            highlight_active = (document == self.model.workspace.active_document and self.model.workspace.mode == 'documents')
            if highlight_active:
                fg_color_1 = active_fg_color
                fg_color_2 = active_fg_color
            else:
                fg_color_1 = title_color
                fg_color_2 = teaser_color

            if i == self.model.selected_index:
                Gdk.cairo_set_source_rgba(ctx, selected_color)
                ctx.rectangle(0, self.view.line_height * i - scrolling_offset, width, self.view.line_height)
                ctx.fill()
            elif not highlight_active and i == self.view.get_item_at_cursor():
                Gdk.cairo_set_source_rgba(ctx, hover_color)
                ctx.rectangle(0, self.view.line_height * i - scrolling_offset, width, self.view.line_height)
                ctx.fill()
            if highlight_active:
                Gdk.cairo_set_source_rgba(ctx, active_bg_color)
                ctx.rectangle(0, self.view.line_height * i - scrolling_offset, width, self.view.line_height)
                ctx.fill()

            Gdk.cairo_set_source_rgba(ctx, fg_color_1)
            ctx.move_to(15, self.view.line_height * i + 12 - scrolling_offset)
            self.view.layout_header.set_text(document.title)
            PangoCairo.show_layout(ctx, self.view.layout_header)

            Gdk.cairo_set_source_rgba(ctx, fg_color_2)
            ctx.move_to(15, self.view.line_height * i + 12 - scrolling_offset)
            self.view.layout_date.set_text(self.get_last_modified_string(document))
            PangoCairo.show_layout(ctx, self.view.layout_date)

            Gdk.cairo_set_source_rgba(ctx, fg_color_2)
            ctx.move_to(15, self.view.line_height * i + 35 - scrolling_offset)
            self.view.layout_teaser.set_text(' '.join(document.plaintext.splitlines())[:100])
            PangoCairo.show_layout(ctx, self.view.layout_teaser)

    def get_last_modified_string(self, document):
        datetime_today, datetime_this_week, datetime_this_year = ServiceLocator.get_datetimes_today_week_year()
        datetime_last_modified = datetime.datetime.fromtimestamp(document.last_modified)
        if document.last_modified >= datetime_today.timestamp():
            return '{datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified)
        elif document.last_modified >= datetime_this_week.timestamp():
            return '{datetime:%a}'.format(datetime=datetime_last_modified)
        elif document.last_modified >= datetime_this_year.timestamp():
            return '{datetime.day} {datetime:%b}'.format(datetime=datetime_last_modified)
        else:
            return '{datetime.day} {datetime:%b} {datetime.year}'.format(datetime=datetime_last_modified)


