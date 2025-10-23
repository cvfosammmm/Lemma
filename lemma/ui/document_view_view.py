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
from gi.repository import Gtk, Gdk, PangoCairo, Pango, Graphene

from urllib.parse import urlparse
import datetime
import time
import cairo
import math

from lemma.services.text_shaper import TextShaper
from lemma.services.text_renderer import TextRenderer
from lemma.services.font_helper import FontHelper
from lemma.services.color_manager import ColorManager
from lemma.document_repo.document_repo import DocumentRepo
from lemma.application_state.application_state import ApplicationState
import lemma.services.timer as timer


class DocumentView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.set_size_request(770, -1)

        self.layout_title = Pango.Layout(self.get_pango_context())
        self.layout_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_title.set_font_description(Pango.FontDescription.from_string('NewComputerModernSans10 Regular 36px'))

        self.layout_subtitle = Pango.Layout(self.get_pango_context())
        self.layout_subtitle.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_subtitle.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.scrollbar_x = Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL)
        self.scrollbar_x.set_valign(Gtk.Align.END)
        self.scrollbar_x.add_css_class('bottom')
        self.scrollbar_x.add_css_class('overlay-indicator')
        self.adjustment_x = self.scrollbar_x.get_adjustment()
        self.add_overlay(self.scrollbar_x)

        self.scrollbar_y = Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL)
        self.scrollbar_y.set_halign(Gtk.Align.END)
        self.scrollbar_y.add_css_class('right')
        self.scrollbar_y.add_css_class('overlay-indicator')
        self.adjustment_y = self.scrollbar_y.get_adjustment()
        self.add_overlay(self.scrollbar_y)

        self.link_overlay = Gtk.Label.new('')
        self.link_overlay.set_valign(Gtk.Align.END)
        self.link_overlay.set_halign(Gtk.Align.END)
        self.link_overlay.add_css_class('link-overlay')
        self.link_overlay.set_visible(False)
        self.add_overlay(self.link_overlay)


class TitleWidget(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.add_css_class('document-title')
        self.set_valign(Gtk.Align.FILL)

        self.outer_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.set_size_request(640, -1)

        self.title_entry = Gtk.Entry()

        self.subtext = Gtk.Label()
        self.subtext.set_xalign(0)

        self.submit_button = Gtk.Button.new_with_label('Change Name')
        self.submit_button.set_can_focus(False)
        self.submit_button.add_css_class('suggested-action')
        self.submit_button.add_css_class('submit')

        self.cancel_button = Gtk.Button.new_with_label('Cancel')
        self.cancel_button.set_can_focus(False)

        self.button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.button_box.append(self.submit_button)
        self.button_box.append(self.cancel_button)
        self.button_revealer = Gtk.Revealer()
        self.button_revealer.set_child(self.button_box)

        self.vbox.append(self.title_entry)
        self.vbox.append(self.subtext)
        self.vbox.append(self.button_revealer)

        self.outer_vbox.append(self.vbox)
        self.outer_vbox.append(Gtk.DrawingArea())

        self.append(self.outer_vbox)


class DocumentViewDrawingArea(Gtk.Widget):

    def __init__(self, model):
        Gtk.Widget.__init__(self)
        self.model = model

        self.add_css_class('document-view')
        self.set_focusable(True)
        self.set_vexpand(True)

        self.colors = dict()

        self.window_surface = None

        self.layout_title = Pango.Layout(self.get_pango_context())
        self.layout_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_title.set_font_description(Pango.FontDescription.from_string('NewComputerModernSans10 Regular 36px'))

        self.layout_subtitle = Pango.Layout(self.get_pango_context())
        self.layout_subtitle.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_subtitle.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.render_cache = dict()
        self.do_render_title = True
        self.last_rendered_document = None
        self.last_cache_reset = time.time()

        self.cursor_blink_time = Gtk.Settings.get_default().get_property('gtk_cursor_blink_time') / 1000
        self.cursor_blink_timeout = Gtk.Settings.get_default().get_property('gtk_cursor_blink_timeout')
        self.cursor_blink_reset = time.time()
        self.cursor_visible = True

        self.add_tick_callback(self.animation_callback)

    def update(self):
        if self.model.document == None: return

        new_active_document = self.model.document != self.last_rendered_document
        document_changed = max(self.model.document.last_cursor_movement, self.model.document.last_modified) > self.last_cache_reset
        if new_active_document or document_changed:
            self.render_cache = dict()
            self.do_render_title = True
            self.last_rendered_document = self.model.document
            self.last_cache_reset = time.time()
            self.reset_cursor_blink()
        self.queue_draw()

    def reset_cursor_blink(self):
        self.cursor_blink_reset = time.time()

    def animation_callback(self, widget, frame_clock):
        time_since_blink_start = time.time() - self.cursor_blink_reset
        time_in_cycle = (time_since_blink_start % self.cursor_blink_time) / self.cursor_blink_time

        if time_since_blink_start <= 10 and time_in_cycle > 0.6:
            cursor_visible = False
        else:
            cursor_visible = True

        if time_since_blink_start <= self.cursor_blink_timeout and cursor_visible != self.cursor_visible:
            self.cursor_visible = cursor_visible
            self.queue_draw()

        return True

    @timer.timer
    def do_snapshot(self, snapshot):
        if self.model.document == None: return
        document = self.model.document

        self.height = self.get_allocated_height()
        self.width = self.get_allocated_width()

        self.setup_scaling_offsets()
        self.setup_colors()

        content_offset_x = ApplicationState.get_value('document_padding_left')
        content_offset_y = ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height') - document.clipping.offset_y
        title_offset_y = ApplicationState.get_value('document_padding_top') - document.clipping.offset_y
        self.first_selection_node, self.last_selection_node = document.cursor.get_first_and_last_node()
        first_selection_line = document.get_ancestors(self.first_selection_node.layout)[-2]
        last_selection_line = document.get_ancestors(self.last_selection_node.layout)[-2]

        ctx = snapshot.append_cairo(Graphene.Rect().init(0, 0, self.width, self.height))

        if content_offset_y >= 0:
            self.draw_title(ctx, content_offset_x, title_offset_y)

        ctx.scale(self.hidpi_factor_inverted, self.hidpi_factor_inverted)
        in_selection = False
        for i, paragraph in enumerate(document.ast.paragraphs):
            for j, line_layout in enumerate(paragraph['layout']['children']):
                if content_offset_y + line_layout['y'] + paragraph['layout']['y'] + line_layout['height'] >= 0 and content_offset_y + line_layout['y'] + paragraph['layout']['y'] <= self.height:
                    if (i,j) not in self.render_cache:
                        self.draw_line(ctx, i, j, line_layout, in_selection)

                    ctx.set_source_surface(self.render_cache[(i,j)], self.device_offset_x + int(content_offset_x * self.hidpi_factor), self.device_offset_y + int((content_offset_y + paragraph['layout']['y'] + line_layout['y']) * self.hidpi_factor))
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
        allocation = self.compute_bounds(self.model.main_window).out_bounds
        surface_transform = self.model.main_window.get_surface_transform()
        self.device_offset_x = 1 - ((allocation.get_x() + surface_transform.x) * self.hidpi_factor) % 1
        self.device_offset_y = 1 - ((allocation.get_y() + surface_transform.y) * self.hidpi_factor) % 1

    @timer.timer
    def setup_colors(self):
        self.colors['text'] = ColorManager.get_ui_color('text')
        self.colors['links'] = ColorManager.get_ui_color('links')
        self.colors['links_page_not_existing'] = ColorManager.get_ui_color('links_page_not_existing')
        self.colors['selection_bg'] = ColorManager.get_ui_color('selection_bg')
        self.colors['title_color'] = ColorManager.get_ui_color('title_color')
        self.colors['description_color'] = ColorManager.get_ui_color('description_color')
        self.colors['border_1'] = ColorManager.get_ui_color('border_1')
        self.colors['cursor'] = ColorManager.get_ui_color('cursor')
        self.colors['drop_cursor'] = ColorManager.get_ui_color('drop_color')

        self.colors['text_string'] = self.colors['text'].to_string()
        self.colors['links_string'] = self.colors['links'].to_string()
        self.colors['links_page_not_existing_string'] = self.colors['links_page_not_existing'].to_string()

    @timer.timer
    def draw_line(self, ctx, paragraph_no, line_no, layout, in_selection):
        surface = ctx.get_target().create_similar_image(cairo.Format.ARGB32, int(layout['width'] * self.hidpi_factor), int(layout['height'] * self.hidpi_factor) + 1)
        self.draw_layout(layout, cairo.Context(surface), -layout['x'], -layout['y'], in_selection)
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
    def draw_title(self, ctx, offset_x, offset_y):
        if self.do_render_title:
            self.layout_title.set_width(ApplicationState.get_value('title_width') * Pango.SCALE)
            self.layout_title.set_text(self.model.document.title)
            self.layout_subtitle.set_width(ApplicationState.get_value('title_width') * Pango.SCALE)
            datetime_last_modified = datetime.datetime.fromtimestamp(self.model.document.last_modified)
            self.layout_subtitle.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))
            self.do_render_title = False

        ctx.move_to(offset_x, offset_y)
        Gdk.cairo_set_source_rgba(ctx, self.colors['title_color'])
        PangoCairo.show_layout(ctx, self.layout_title)

        Gdk.cairo_set_source_rgba(ctx, self.colors['border_1'])
        ctx.rectangle(offset_x, offset_y + ApplicationState.get_value('title_height'), ApplicationState.get_value('title_width'), 1)
        ctx.fill()

        ctx.move_to(offset_x, offset_y + ApplicationState.get_value('title_height') + 8)
        Gdk.cairo_set_source_rgba(ctx, self.colors['description_color'])
        PangoCairo.show_layout(ctx, self.layout_subtitle)

    @timer.timer
    def draw_cursor(self, ctx, offset_x, offset_y):
        if ApplicationState.get_value('document_view_hide_cursor_on_unfocus'):
            if not self.has_focus(): return
            if self.model.document.cursor.has_selection(): return
            if not self.cursor_visible: return

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

    def do_size_allocate(self, width, height, baseline):
        self.model.set_size(width, height)


