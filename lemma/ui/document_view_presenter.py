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
from gi.repository import Gtk, Gdk, Graphene

from urllib.parse import urlparse
import datetime
import time
import cairo
import math

from lemma.services.text_shaper import TextShaper
from lemma.services.text_renderer import TextRenderer
from lemma.services.color_manager import ColorManager
from lemma.services.layout_info import LayoutInfo
from lemma.repos.document_repo import DocumentRepo
from lemma.application_state.application_state import ApplicationState
import lemma.services.timer as timer


class DocumentViewPresenter():

    def __init__(self, model):
        self.model = model
        self.view = self.model.view.content
        self.view.set_draw_func(self.draw)

        self.colors = dict()

        self.window_surface = None

        self.render_cache = dict()

    def update_pointer(self):
        if self.model.document == None: return

        document = self.model.document
        if document == None:
            self.view.set_cursor_from_name('default')
            return

        x = self.model.scrolling_position_x + (self.model.cursor_x if self.model.cursor_x != None else 0)
        y = self.model.scrolling_position_y + (self.model.cursor_y if self.model.cursor_y != None else 0)
        x -= LayoutInfo.get_document_padding_left()
        y -= LayoutInfo.get_normal_document_offset()
        y -= ApplicationState.get_value('title_buttons_height')

        if y > 0:
            leaf_box = document.get_leaf_at_xy(x, y)
            if leaf_box != None:
                node = leaf_box['node']
                if node != None:
                    if node.link != None and not self.model.ctrl_pressed:
                        self.view.set_cursor_from_name('pointer')
                    elif node.type == 'widget':
                        self.view.set_cursor_from_name(node.value.get_cursor_name())
                    elif node.type == 'placeholder':
                        self.view.set_cursor_from_name('default')
                    else:
                        self.view.set_cursor_from_name('text')
                else:
                    self.view.set_cursor_from_name('text')
            else:
                self.view.set_cursor_from_name('text')
        else:
            self.view.set_cursor_from_name('default')

    @timer.timer
    def draw(self, snapshot):
        if self.model.document == None: return
        document = self.model.document

        self.height = self.view.get_allocated_height()
        self.width = self.view.get_allocated_width()

        self.setup_scaling_offsets()
        self.setup_colors()

        content_offset_x = LayoutInfo.get_document_padding_left()
        content_offset_y = LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height') - self.model.scrolling_position_y
        title_offset_y = LayoutInfo.get_document_padding_top() - self.model.scrolling_position_y
        self.first_selection_node, self.last_selection_node = document.cursor.get_first_and_last_node()
        first_selection_line = document.get_ancestors(self.first_selection_node.layout)[-2]
        last_selection_line = document.get_ancestors(self.last_selection_node.layout)[-2]

        ctx = snapshot.append_cairo(Graphene.Rect().init(0, 0, self.width, self.height))

        ctx.scale(self.hidpi_factor_inverted, self.hidpi_factor_inverted)
        in_selection = False
        for i, paragraph in enumerate(document.ast.paragraphs):
            if content_offset_y + paragraph.layout['y'] + paragraph.layout['height'] >= 0 and content_offset_y + paragraph.layout['y'] <= self.height:
                self.draw_bullet(ctx, content_offset_x, content_offset_y, paragraph)

            for j, line_layout in enumerate(paragraph.layout['children']):
                if content_offset_y + line_layout['y'] + paragraph.layout['y'] + line_layout['height'] >= 0 and content_offset_y + line_layout['y'] + paragraph.layout['y'] <= self.height:
                    if (i,j) not in self.render_cache:
                        self.draw_line(ctx, i, j, line_layout, in_selection)

                    ctx.set_source_surface(self.render_cache[(i,j)], self.device_offset_x + int(content_offset_x * self.hidpi_factor), self.device_offset_y + int((content_offset_y + paragraph.layout['y'] + line_layout['y']) * self.hidpi_factor))
                    ctx.paint()
                elif (i,j) in self.render_cache:
                    del(self.render_cache[(i,j)])

                if not in_selection and line_layout['y'] + line_layout['parent']['y'] == first_selection_line['y'] + first_selection_line['parent']['y']: in_selection = True
                if in_selection and line_layout['y'] + line_layout['parent']['y'] == last_selection_line['y'] + last_selection_line['parent']['y']: in_selection = False

        if ApplicationState.get_value('drop_cursor_position') != None:
            self.draw_drop_cursor(ctx, content_offset_x, content_offset_y)
        else:
            self.draw_cursor(ctx, content_offset_x, content_offset_y)

    @timer.timer
    def setup_scaling_offsets(self):
        if self.window_surface == None:
            self.window_surface = self.model.main_window.get_surface()

        self.hidpi_factor = self.window_surface.get_scale()
        self.hidpi_factor_inverted = 1 / self.hidpi_factor
        allocation = self.view.compute_bounds(self.model.main_window).out_bounds
        surface_transform = self.model.main_window.get_surface_transform()
        self.device_offset_x = 1 - ((allocation.get_x() + surface_transform.x) * self.hidpi_factor) % 1
        self.device_offset_y = 1 - ((allocation.get_y() + surface_transform.y) * self.hidpi_factor) % 1

    @timer.timer
    def setup_colors(self):
        self.colors['text'] = ColorManager.get_ui_color('text')
        self.colors['links'] = ColorManager.get_ui_color('links')
        self.colors['links_page_not_existing'] = ColorManager.get_ui_color('links_page_not_existing')
        self.colors['selection_bg'] = ColorManager.get_ui_color('selection_bg')
        self.colors['description_color'] = ColorManager.get_ui_color('description_color')
        self.colors['border_1'] = ColorManager.get_ui_color('border_1')
        self.colors['cursor'] = ColorManager.get_ui_color('cursor')
        self.colors['drop_cursor'] = ColorManager.get_ui_color('drop_color')

        self.colors['text_string'] = self.colors['text'].to_string()
        self.colors['links_string'] = self.colors['links'].to_string()
        self.colors['links_page_not_existing_string'] = self.colors['links_page_not_existing'].to_string()
        self.colors['bullets_string'] = ColorManager.get_ui_color('bullets').to_string()

    @timer.timer
    def draw_bullet(self, ctx, offset_x, offset_y, paragraph):
        if paragraph.style == 'ul':
            layout = paragraph.layout
            line_layout = layout['children'][0]
            first_char_layout = line_layout['children'][0]
            fontname = first_char_layout['fontname']
            baseline = TextShaper.get_ascend(fontname=fontname)
            fg_color = self.colors['bullets_string']

            surface, left, top = TextRenderer.get_glyph('-', fontname, fg_color, self.hidpi_factor)
            bullet_indent = LayoutInfo.get_indentation('ul', paragraph.indentation_level) - LayoutInfo.get_bullet_padding() - surface.get_width()
            bullet_measurement = TextShaper.measure_single('-')
            if surface != None:
                ctx.set_source_surface(surface, self.device_offset_x + int((offset_x + bullet_indent) * self.hidpi_factor + left), self.device_offset_y + int((offset_y + baseline + layout['y'] + line_layout['height'] - bullet_measurement[1]) * self.hidpi_factor + top))
                ctx.paint()

    @timer.timer
    def draw_line(self, ctx, paragraph_no, line_no, layout, in_selection):
        surface = ctx.get_target().create_similar_image(cairo.Format.ARGB32, int((layout['x'] + layout['width']) * self.hidpi_factor), int(layout['height'] * self.hidpi_factor) + 1)
        self.draw_layout(layout, cairo.Context(surface), 0, -layout['y'], in_selection)
        self.render_cache[(paragraph_no, line_no)] = surface

    def draw_layout(self, layout, ctx, offset_x, offset_y, in_selection):
        if layout['type'] == 'char':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            fontname = layout['fontname']
            baseline = TextShaper.get_ascend(fontname=fontname)

            if fontname != 'emojis':
                fg_color = self.get_fg_color_string_by_node(layout['node'])
                surface, left, top = TextRenderer.get_glyph(layout['node'].value, fontname, fg_color, self.hidpi_factor)
                if surface != None:
                    ctx.set_source_surface(surface, int((offset_x + layout['x']) * self.hidpi_factor + left), int((offset_y + baseline + layout['y']) * self.hidpi_factor + top))
                    ctx.paint()
            else:
                surface, left, top = TextRenderer.get_glyph(layout['node'].value, fontname, None, self.hidpi_factor)
                if surface != None:
                    ctx.set_source_surface(surface, int((offset_x + layout['x']) * self.hidpi_factor + left), int((offset_y + baseline + layout['y']) * self.hidpi_factor + top))
                    ctx.paint()

        if layout['type'] == 'widget':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            widget = layout['node'].value
            surface = widget.get_cairo_surface()
            fontname = layout['fontname']
            top = -TextShaper.get_descend(fontname=fontname)

            matrix = ctx.get_matrix()
            widget_factor_x = widget.get_width() * self.hidpi_factor / widget.get_original_width()
            widget_factor_y = widget.get_height() * self.hidpi_factor / widget.get_original_height()
            ctx.scale(widget_factor_x, widget_factor_y)

            ctx.set_source_surface(surface, (offset_x + layout['x']) * self.hidpi_factor / widget_factor_x, (offset_y + layout['y'] + top) * self.hidpi_factor / widget_factor_y)
            ctx.paint()

            ctx.set_matrix(matrix)

        if layout['type'] == 'placeholder':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            fontname = layout['fontname']
            baseline = TextShaper.get_ascend(fontname=fontname)

            fg_color = self.get_fg_color_string_by_node(layout['node'])
            surface, left, top = TextRenderer.get_glyph('▯', fontname, fg_color, self.hidpi_factor)

            ctx.set_source_surface(surface, int((offset_x + layout['x']) * self.hidpi_factor + left), int((offset_y + baseline + layout['y']) * self.hidpi_factor + top))
            ctx.paint()

        if layout['type'] == 'mathroot':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

        if layout['type'] == 'mathfraction':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

        if layout['type'] == 'mathscript':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

        for child in layout['children']:
            if not in_selection and child['node'] != None and child['node'] == self.first_selection_node:
                in_selection = True
            if in_selection and child['node'] != None and child['node'] == self.last_selection_node:
                in_selection = False
            self.draw_layout(child, ctx, offset_x + layout['x'], offset_y + layout['y'], in_selection)

        if layout['type'] == 'mathroot':
            fg_color = self.get_fg_color_by_node(layout['node'])
            Gdk.cairo_set_source_rgba(ctx, fg_color)

            line_offset = max(7, layout['children'][1]['width'])
            line_width = layout['children'][0]['width']
            line_height = layout['children'][0]['height']

            ctx.set_line_width(2)
            ctx.move_to((offset_x + layout['x'] + line_offset - 6) * self.hidpi_factor, (offset_y + layout['y'] + line_height - 10) * self.hidpi_factor)
            ctx.line_to((offset_x + layout['x'] + line_offset) * self.hidpi_factor, (offset_y + layout['y'] + line_height - 2) * self.hidpi_factor)
            ctx.stroke()
            ctx.set_line_width(1)
            ctx.move_to((offset_x + layout['x'] + line_offset) * self.hidpi_factor, (offset_y + layout['y'] + line_height - 2) * self.hidpi_factor)
            ctx.line_to((offset_x + layout['x'] + line_offset + 9) * self.hidpi_factor, (offset_y + layout['y'] + 1) * self.hidpi_factor)
            ctx.stroke()
            ctx.rectangle((offset_x + layout['x'] + line_offset + 9) * self.hidpi_factor, int((offset_y + layout['y']) * self.hidpi_factor), line_width, 1)
            ctx.fill()

        if layout['type'] == 'mathfraction':
            fg_color = self.get_fg_color_by_node(layout['node'])
            Gdk.cairo_set_source_rgba(ctx, fg_color)

            line_offset = layout['children'][0]['children'][1]['height']
            line_width = layout['width']

            ctx.rectangle((offset_x + layout['x']) * self.hidpi_factor, int((offset_y + layout['y'] + line_offset) * self.hidpi_factor), (line_width - 2) * self.hidpi_factor, 1)
            ctx.fill()

    def draw_selection(self, layout, ctx, offset_x, offset_y):
        Gdk.cairo_set_source_rgba(ctx, self.colors['selection_bg'])
        ctx.rectangle(math.floor((offset_x + layout['x']) * self.hidpi_factor), math.floor(offset_y * self.hidpi_factor), math.ceil(layout['width'] * self.hidpi_factor), math.ceil(layout['parent']['height'] * self.hidpi_factor))
        ctx.fill()

    @timer.timer
    def get_fg_color_string_by_node(self, node):
        if node.link == None:
            return self.colors['text_string']
        if node.link.startswith('http') or len(DocumentRepo.list_by_title(node.link)) > 0:
            return self.colors['links_string']
        return self.colors['links_page_not_existing_string']

    @timer.timer
    def get_fg_color_by_node(self, node):
        if node.link == None:
            return self.colors['text']
        if node.link.startswith('http') or len(DocumentRepo.list_by_title(node.link)) > 0:
            return self.colors['links']
        return self.colors['links_page_not_existing']

    @timer.timer
    def draw_cursor(self, ctx, offset_x, offset_y):
        if not self.model.cursor_visible: return

        insert = self.model.document.cursor.get_insert_node()
        layout = insert.layout
        x, y = self.model.document.get_absolute_xy(layout)
        padding_top = TextShaper.get_padding_top(layout['fontname'])
        padding_bottom = 0#TextShaper.get_padding_bottom(fontname)
        cursor_coords = (self.device_offset_x + int((x + offset_x) * self.hidpi_factor), self.device_offset_y + int((y + offset_y + padding_top) * self.hidpi_factor), 1, int((layout['height'] - padding_top - padding_bottom) * self.hidpi_factor))

        Gdk.cairo_set_source_rgba(ctx, self.colors['cursor'])
        ctx.rectangle(*cursor_coords)
        ctx.fill()

    @timer.timer
    def draw_drop_cursor(self, ctx, offset_x, offset_y):
        x, y = ApplicationState.get_value('drop_cursor_position')
        layout = self.model.document.get_cursor_holding_layout_close_to_xy(x, y)

        x, y = self.model.document.get_absolute_xy(layout)
        padding_top = TextShaper.get_padding_top(layout['fontname'])
        padding_bottom = 0
        cursor_coords = (self.device_offset_x + int((x + offset_x) * self.hidpi_factor), self.device_offset_y + int((y + offset_y + padding_top) * self.hidpi_factor), 1, int((layout['height'] - padding_top - padding_bottom) * self.hidpi_factor))

        Gdk.cairo_set_source_rgba(ctx, self.colors['drop_cursor'])
        ctx.rectangle(*cursor_coords)
        ctx.fill()


