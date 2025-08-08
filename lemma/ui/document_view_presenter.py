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
from gi.repository import Gtk, GObject, Gdk, PangoCairo, Pango

from urllib.parse import urlparse
import datetime
import time
import cairo

from lemma.services.font_manager import FontManager
from lemma.services.color_manager import ColorManager
from lemma.document_repo.document_repo import DocumentRepo
from lemma.application_state.application_state import ApplicationState
import lemma.services.timer as timer


class DocumentViewPresenter():

    def __init__(self, model):
        self.model = model
        self.view = self.model.view
        self.content = self.view.content
        self.scrolling_job = None
        self.render_cache = dict()
        self.last_cache_reset = time.time()

        self.content.set_draw_func(self.draw)

    def update(self):
        if self.model.document == None: return

        self.update_size()
        self.update_scrollbars()
        self.update_pointer()
        if max(self.model.document.last_cursor_movement, self.model.document.last_modified) > self.last_cache_reset:
            self.render_cache = dict()
            self.last_cache_reset = time.time()
        self.view.content.queue_draw()

    def update_size(self):
        document = self.model.document
        height = self.model.document.get_height() + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')
        scrolling_offset_y = document.clipping.offset_y

        self.view.adjustment_x.set_page_size(1)
        self.view.adjustment_y.set_page_size(ApplicationState.get_value('document_view_height'))
        self.view.adjustment_x.set_upper(1)
        self.view.adjustment_y.set_upper(height)

        if scrolling_offset_y > self.view.adjustment_y.get_upper() - ApplicationState.get_value('document_view_height'):
            self.view.adjustment_y.set_value(self.view.adjustment_y.get_upper())

    def update_scrollbars(self):
        document = self.model.document
        height = self.model.document.get_height() + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')

        self.view.scrollbar_x.set_visible(False)
        self.view.scrollbar_y.set_visible(height > ApplicationState.get_value('document_view_height'))
        self.view.adjustment_x.set_value(document.clipping.offset_x)
        self.view.adjustment_y.set_value(document.clipping.offset_y)

        if self.model.cursor_x != None and self.model.cursor_x > self.view.get_allocated_width() - 24:
            self.view.scrollbar_y.add_css_class('hovering')
        else:
            self.view.scrollbar_y.remove_css_class('hovering')
            if self.model.last_cursor_or_scrolling_change < time.time() - 1.5:
                self.view.scrollbar_x.add_css_class('hidden')
                self.view.scrollbar_y.add_css_class('hidden')
            else:
                self.view.scrollbar_x.remove_css_class('hidden')
                self.view.scrollbar_y.remove_css_class('hidden')

        GObject.timeout_add(1750, self.update_scrollbars)
        return False

    def update_pointer(self):
        document = self.model.document
        if document == None:
            self.content.set_cursor_from_name('default')
            return

        x = document.clipping.offset_x + (self.model.cursor_x if self.model.cursor_x != None else 0)
        y = document.clipping.offset_y + (self.model.cursor_y if self.model.cursor_y != None else 0)
        x -= ApplicationState.get_value('document_padding_left')
        y -= ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')

        if y < -ApplicationState.get_value('subtitle_height'):
            self.content.set_cursor_from_name('text')
        elif y > 0:
            leaf_box = document.get_leaf_at_xy(x, y)
            if leaf_box != None:
                node = leaf_box['node']
                if node != None:
                    if node.link != None and not self.model.ctrl_pressed:
                        self.content.set_cursor_from_name('pointer')
                    elif node.type == 'widget':
                        self.content.set_cursor_from_name(node.value.get_cursor_name())
                    elif node.type == 'placeholder':
                        self.content.set_cursor_from_name('default')
                    else:
                        self.content.set_cursor_from_name('text')
                else:
                    self.content.set_cursor_from_name('text')
            else:
                self.content.set_cursor_from_name('text')
        else:
            self.content.set_cursor_from_name('default')

    def scroll_to_position(self, position, animate=False):
        document = self.model.document
        window_width = ApplicationState.get_value('document_view_width')
        yoffset = max(position[1], 0)
        xoffset = max(position[0], 0)
        scrolling_offset_x = document.clipping.offset_x
        scrolling_offset_y = document.clipping.offset_y

        self.scrolling_job = {'from': (scrolling_offset_x, scrolling_offset_y), 'to': (xoffset, yoffset), 'starting_time': time.time(), 'duration': 0.2 if animate else 0}
        self.scroll_now()

    def scroll_now(self):
        if self.scrolling_job == None: return False

        if self.scrolling_job['duration'] == 0:
            fraction_done = 1
        else:
            time_percent = (time.time() - self.scrolling_job['starting_time']) / self.scrolling_job['duration']
            fraction_done = (time_percent - 1)**3 + 1 # easing

        if fraction_done >= 1:
            new_x = self.scrolling_job['to'][0]
            new_y = self.scrolling_job['to'][1]
        else:
            new_x = self.scrolling_job['from'][0] * (1 - fraction_done) + self.scrolling_job['to'][0] * fraction_done
            new_y = self.scrolling_job['from'][1] * (1 - fraction_done) + self.scrolling_job['to'][1] * fraction_done

        self.view.adjustment_x.set_value(new_x)
        self.view.adjustment_y.set_value(new_y)

        if (new_x, new_y) == self.scrolling_job['to']:
            self.scrolling_job = None
        else:
            GObject.timeout_add(15, self.scroll_now)

        return False

    @timer.timer
    def draw(self, widget, ctx, width, height):
        if self.model.document == None: return
        document = self.model.document

        offset_x = ApplicationState.get_value('document_padding_left')
        scrolling_offset_y = document.clipping.offset_y
        offset_y = ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height') - scrolling_offset_y
        self.first_selection_node = document.cursor.get_first_node()
        self.last_selection_node = document.cursor.get_last_node()
        first_selection_line = document.get_ancestors(self.first_selection_node.layout)[-2]
        last_selection_line = document.get_ancestors(self.last_selection_node.layout)[-2]

        self.draw_title(ctx, ApplicationState.get_value('document_padding_left'), ApplicationState.get_value('document_padding_top') - scrolling_offset_y)

        in_selection = False
        for i, paragraph in enumerate(document.ast.lines):
            for j, line_layout in enumerate(paragraph['layout']['children']):
                if offset_y + line_layout['y'] + paragraph['layout']['y'] + line_layout['height'] >= 0 and offset_y + line_layout['y'] + paragraph['layout']['y'] <= height:
                    if (i,j) not in self.render_cache:
                        surface = ctx.get_target().create_similar(cairo.Content.COLOR_ALPHA, int(line_layout['width']), int(line_layout['height']))
                        self.draw_layout(line_layout, cairo.Context(surface), -line_layout['x'], -line_layout['y'], in_selection)
                        self.render_cache[(i,j)] = surface

                    ctx.set_source_surface(self.render_cache[(i,j)], offset_x, offset_y + paragraph['layout']['y'] + line_layout['y'])
                    ctx.rectangle(offset_x, offset_y + paragraph['layout']['y'] + line_layout['y'], line_layout['width'], line_layout['height'])
                    ctx.fill()
                elif (i,j) in self.render_cache:
                    del(self.render_cache[(i,j)])

                if not in_selection and line_layout['y'] + line_layout['parent']['y'] == first_selection_line['y'] + first_selection_line['parent']['y']: in_selection = True
                if in_selection and line_layout['y'] + line_layout['parent']['y'] == last_selection_line['y'] + last_selection_line['parent']['y']: in_selection = False

        self.draw_cursor(ctx, offset_x, offset_y)

    def draw_layout(self, layout, ctx, offset_x, offset_y, in_selection):
        if layout['type'] == 'char':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            fontname = FontManager.get_fontname_from_node(layout['node'])
            fg_color = self.get_fg_color_by_node(layout['node'])
            baseline = FontManager.get_ascend(fontname=fontname)

            surface = FontManager.get_surface(layout['node'].value, fontname=fontname)

            if surface != None:
                if fontname != 'emojis':
                    ctx.set_source_surface(surface, offset_x + layout['x'] + layout['left'], offset_y + baseline + layout['y'] + layout['top'])
                    pattern = ctx.get_source()
                    pattern.set_filter(cairo.Filter.BEST)
                    Gdk.cairo_set_source_rgba(ctx, fg_color)
                    ctx.mask(pattern)
                    ctx.fill()
                else:
                    ctx.set_source_surface(surface, offset_x + layout['x'] + layout['left'], offset_y + baseline + layout['y'] + layout['top'])
                    ctx.mask(ctx.get_source())
                    ctx.fill()

        if layout['type'] == 'widget':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            surface = layout['node'].value.get_cairo_surface()
            fontname = FontManager.get_fontname_from_node(layout['node'])
            top = -FontManager.get_descend(fontname=fontname)
            ctx.set_source_surface(surface, offset_x + layout['x'], offset_y + layout['y'] + top)
            ctx.rectangle(offset_x + layout['x'], offset_y + layout['y'], layout['width'], layout['height'])
            ctx.fill()

        if layout['type'] == 'placeholder':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            fontname = FontManager.get_fontname_from_node(layout['node'])
            baseline = FontManager.get_ascend(fontname=fontname)

            width, height, left, top = FontManager.measure_single('▯', fontname=fontname)
            fg_color = self.get_fg_color_by_node(layout['node'])
            top += baseline

            surface = FontManager.get_surface('▯', fontname=fontname)
            ctx.set_source_surface(surface, offset_x + layout['x'] + left, offset_y + layout['y'] + top)
            pattern = ctx.get_source()
            pattern.set_filter(cairo.Filter.BEST)
            Gdk.cairo_set_source_rgba(ctx, fg_color)
            ctx.mask(pattern)
            ctx.fill()

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
            ctx.move_to(offset_x + layout['x'] + line_offset - 6, offset_y + line_height - 10)
            ctx.line_to(offset_x + layout['x'] + line_offset, offset_y + line_height - 2)
            ctx.stroke()
            ctx.set_line_width(1)
            ctx.move_to(offset_x + layout['x'] + line_offset, offset_y + line_height - 2)
            ctx.line_to(offset_x + layout['x'] + line_offset + 9, offset_y + 1)
            ctx.stroke()
            ctx.rectangle(offset_x + layout['x'] + line_offset + 9, offset_y, line_width, 1)
            ctx.fill()

        if layout['type'] == 'mathfraction':
            fg_color = self.get_fg_color_by_node(layout['node'])
            Gdk.cairo_set_source_rgba(ctx, fg_color)

            line_offset = layout['children'][0]['children'][1]['width']
            line_width = layout['width']

            ctx.rectangle(offset_x + layout['x'] + 1, offset_y + line_offset + 1, line_width - 2, 1)
            ctx.fill()

    def draw_selection(self, layout, ctx, offset_x, offset_y):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('selection_bg'))
        ctx.rectangle(offset_x + layout['x'], offset_y, layout['width'], layout['parent']['height'])
        ctx.fill()

    def get_fg_color_by_node(self, node):
        if node.link != None:
            if urlparse(node.link).scheme in ['http', 'https'] or \
                DocumentRepo.get_by_title(node.link) != None:
                return ColorManager.get_ui_color('links')
            else:
                return ColorManager.get_ui_color('links_page_not_existing')
        else:
            return ColorManager.get_ui_color('text')

    def draw_title(self, ctx, offset_x, offset_y):
        self.view.layout_title.set_width(ApplicationState.get_value('title_width') * Pango.SCALE)
        self.view.layout_title.set_text(self.model.document.title)
        ctx.move_to(offset_x, offset_y)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('title_color'))
        PangoCairo.show_layout(ctx, self.view.layout_title)

        self.view.layout_subtitle.set_width(ApplicationState.get_value('title_width') * Pango.SCALE)
        datetime_last_modified = datetime.datetime.fromtimestamp(self.model.document.last_modified)
        self.view.layout_subtitle.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))
        ctx.move_to(offset_x, offset_y + ApplicationState.get_value('title_height') + 8)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('description_color'))
        PangoCairo.show_layout(ctx, self.view.layout_subtitle)

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('border_1'))
        ctx.rectangle(offset_x, offset_y + ApplicationState.get_value('title_height'), ApplicationState.get_value('title_width'), 1)
        ctx.fill()

    def draw_cursor(self, ctx, offset_x, offset_y):
        if not self.content.is_focus() and ApplicationState.get_value('document_view_hide_cursor_on_unfocus'): return
        if self.model.document.cursor.has_selection(): return

        insert = self.model.document.cursor.get_insert_node()
        layout = insert.layout
        x, y = self.model.document.get_absolute_xy(layout)
        fontname = FontManager.get_fontname_from_node(insert)
        padding_top = FontManager.get_padding_top(fontname)
        padding_bottom = 0#FontManager.get_padding_bottom(fontname)
        cursor_coords = (x + offset_x, y + offset_y + padding_top, 1, layout['height'] - padding_top - padding_bottom)

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('cursor'))
        ctx.rectangle(*cursor_coords)
        ctx.fill()


