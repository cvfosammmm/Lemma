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
from gi.repository import Gtk, GObject, Gdk, PangoCairo

from urllib.parse import urlparse
import datetime
import time
import cairo

from lemma.infrastructure.font_manager import FontManager
from lemma.infrastructure.color_manager import ColorManager


class DocumentViewPresenter():

    def __init__(self, model):
        self.model = model
        self.view = self.model.view
        self.content = self.view.content
        self.scrolling_job = None

        self.content.set_draw_func(self.draw)

        self.model.connect('changed', self.on_change)

    def on_change(self, model):
        if self.model.document == None: return

        self.update_size()
        self.update_scrolling_destination()
        self.update_scrollbars()
        self.update_pointer()
        self.view.content.queue_draw()

    def update_size(self):
        document = self.model.document
        height = self.model.document.layout.height + self.view.padding_bottom + self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height
        scrolling_offset_y = document.clipping.offset_y

        self.view.adjustment_x.set_page_size(1)
        self.view.adjustment_y.set_page_size(self.model.height)
        self.view.adjustment_x.set_upper(1)
        self.view.adjustment_y.set_upper(height)

        if scrolling_offset_y > self.view.adjustment_y.get_upper() - self.model.height:
            self.view.adjustment_y.set_value(self.view.adjustment_y.get_upper())

    def update_scrolling_destination(self):
        if self.model.document.scroll_insert_on_screen_after_layout_update:
            self.model.document.scroll_insert_on_screen_after_layout_update = False
            self.scroll_insert_on_screen()

    def update_scrollbars(self):
        document = self.model.document
        height = self.model.document.layout.height + self.view.padding_bottom + self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height

        self.view.scrollbar_x.set_visible(False)
        self.view.scrollbar_y.set_visible(height > self.model.height)
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
        x -= self.view.padding_left
        y -= self.view.padding_top + self.view.title_height + self.view.subtitle_height
        link = None

        if y < -self.view.subtitle_height:
            self.content.set_cursor_from_name('text')
        elif y > 0:
            self.content.set_cursor_from_name('text')
            leaf_box = document.layout.get_leaf_at_xy(x, y)
            if leaf_box != None:
                node = leaf_box.node
                if node != None:
                    if node.link != None:
                        self.content.set_cursor_from_name('pointer')
                        link = node.link
                    elif node.is_widget():
                        self.content.set_cursor_from_name(node.value.get_cursor_name())
                    elif node.is_placeholder():
                        self.content.set_cursor_from_name('default')
                    else:
                        self.content.set_cursor_from_name('text')
        else:
            self.content.set_cursor_from_name('default')

        if link != None:
            self.model.set_link_target_at_pointer(link.target)
        else:
            self.model.set_link_target_at_pointer(None)

    def scroll_insert_on_screen(self, animate=False):
        document = self.model.document
        insert_node = document.cursor.get_insert_node()
        insert_position = insert_node.layout.get_absolute_xy()
        content_offset = self.view.padding_top + self.view.title_height + self.view.subtitle_height
        insert_y = insert_position[1] + content_offset
        insert_height = insert_node.layout.height
        window_height = self.model.height
        scrolling_offset_y = document.clipping.offset_y

        if window_height <= 0: return

        if insert_y == content_offset:
            self.scroll_to_position((0, 0), animate)
        elif insert_y < scrolling_offset_y:
            if insert_height > window_height:
                self.scroll_to_position((0, insert_y - window_height + insert_height), animate)
            else:
                self.scroll_to_position((0, insert_y), animate)
        elif insert_position[1] == self.model.document.layout.height - self.model.document.layout.children[-1].height:
            self.scroll_to_position((0, self.model.document.layout.height + content_offset + self.view.padding_bottom - window_height), animate)
        elif insert_y > scrolling_offset_y - insert_height + window_height:
            self.scroll_to_position((0, insert_y - window_height + insert_height), animate)

    def scroll_to_position(self, position, animate=False):
        document = self.model.document
        window_width = self.model.width
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

    def draw(self, widget, ctx, width, height):
        if self.model.document == None: return

        document = self.model.document
        offset_x = self.view.padding_left
        scrolling_offset_y = document.clipping.offset_y
        offset_y = self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height - scrolling_offset_y

        self.ctx = ctx
        self.drawing_state = {'in_selection': False}
        self.offset_x, self.offset_y = offset_x, offset_y

        self.draw_title(ctx, self.view.padding_left, self.view.padding_top - scrolling_offset_y)
        document.layout.accept_presenter(self)
        self.draw_cursor(ctx, self.offset_x, self.offset_y)

    def draw_layout_block(self, layout):
        self.update_selection_state(layout)
        self.draw_children(layout)

    def draw_layout_char(self, layout):
        self.update_selection_state(layout)
        self.draw_selection(layout)

        fontname = FontManager.get_fontname_from_node(layout.node)
        fg_color = self.get_fg_color_by_node(layout.node)
        baseline = FontManager.get_ascend(fontname=fontname)

        surface = FontManager.get_surface(layout.node.value, fontname=fontname)
        if surface != None:
            self.ctx.set_source_surface(surface, self.offset_x + layout.x + layout.left, self.offset_y + baseline + layout.y + layout.top)
            pattern = self.ctx.get_source()
            pattern.set_filter(cairo.Filter.BEST)
            Gdk.cairo_set_source_rgba(self.ctx, fg_color)
            self.ctx.mask(pattern)
            self.ctx.fill()

    def draw_layout_widget(self, layout):
        self.update_selection_state(layout)
        self.draw_selection(layout)

        surface = layout.node.value.get_cairo_surface()
        fontname = FontManager.get_fontname_from_node(layout.node)
        top = -FontManager.get_descend(fontname=fontname)
        self.ctx.set_source_surface(surface, self.offset_x + layout.x, self.offset_y + layout.y + top)
        self.ctx.rectangle(self.offset_x + layout.x, self.offset_y + layout.y, layout.width, layout.height)
        self.ctx.fill()

    def draw_layout_placeholder(self, layout):
        self.update_selection_state(layout)
        self.draw_selection(layout)

        fontname = FontManager.get_fontname_from_node(layout.node)
        baseline = FontManager.get_ascend(fontname=fontname)

        width, height, left, top = FontManager.measure_single('▯', fontname=fontname)
        fg_color = self.get_fg_color_by_node(layout.node)
        top += baseline

        surface = FontManager.get_surface('▯', fontname=fontname)
        self.ctx.set_source_surface(surface, self.offset_x + layout.x + left, self.offset_y + layout.y + top)
        pattern = self.ctx.get_source()
        pattern.set_filter(cairo.Filter.BEST)
        Gdk.cairo_set_source_rgba(self.ctx, fg_color)
        self.ctx.mask(pattern)
        self.ctx.fill()

    def draw_layout_mathatom(self, layout):
        self.update_selection_state(layout)

        if self.drawing_state['in_selection']:
            Gdk.cairo_set_source_rgba(self.ctx, ColorManager.get_ui_color('selection_bg'))
            self.ctx.rectangle(self.offset_x + layout.x, self.offset_y, layout.width, layout.parent.height)
            self.ctx.fill()

        self.draw_children(layout)

    def draw_layout_mathroot(self, layout):
        self.update_selection_state(layout)

        if self.drawing_state['in_selection']:
            Gdk.cairo_set_source_rgba(self.ctx, ColorManager.get_ui_color('selection_bg'))
            self.ctx.rectangle(self.offset_x + layout.x, self.offset_y, layout.width, layout.parent.height)
            self.ctx.fill()

        self.draw_children(layout)

        fg_color = self.get_fg_color_by_node(layout.node)
        Gdk.cairo_set_source_rgba(self.ctx, fg_color)

        line_offset = max(7, layout.children[1].width)
        line_width = layout.children[0].width
        line_height = layout.children[0].height

        self.ctx.set_line_width(2)
        self.ctx.move_to(self.offset_x + layout.x + line_offset - 6, self.offset_y + line_height - 10)
        self.ctx.line_to(self.offset_x + layout.x + line_offset, self.offset_y + line_height - 2)
        self.ctx.stroke()
        self.ctx.set_line_width(1)
        self.ctx.move_to(self.offset_x + layout.x + line_offset, self.offset_y + line_height - 2)
        self.ctx.line_to(self.offset_x + layout.x + line_offset + 9, self.offset_y + 1)
        self.ctx.line_to(self.offset_x + layout.x + line_offset + 10 + line_width, self.offset_y + 1)
        self.ctx.stroke()

    def draw_layout(self, layout):
        self.update_selection_state(layout)
        self.draw_children(layout)

    def draw_selection(self, layout):
        if self.drawing_state['in_selection']:
            Gdk.cairo_set_source_rgba(self.ctx, ColorManager.get_ui_color('selection_bg'))
            self.ctx.rectangle(self.offset_x + layout.x, self.offset_y, layout.width, layout.parent.height)
            self.ctx.fill()

    def draw_children(self, layout):
        self.offset_x += layout.x
        self.offset_y += layout.y
        for child in layout.children:
            child.accept_presenter(self)
        self.offset_x -= layout.x
        self.offset_y -= layout.y

    def update_selection_state(self, layout):
        document = self.model.document
        self.first_selection_node = document.cursor.get_first_node()
        self.last_selection_node = document.cursor.get_last_node()

        if layout.node != None and layout.node == self.first_selection_node:
            self.drawing_state['in_selection'] = True
        if layout.node != None and layout.node == self.last_selection_node:
            self.drawing_state['in_selection'] = False

    def get_fg_color_by_node(self, node):
        if node.link != None:
            if urlparse(node.link.target).scheme in ['http', 'https'] or \
                self.model.workspace.get_by_title(node.link.target) != None:
                return ColorManager.get_ui_color('links')
            else:
                return ColorManager.get_ui_color('links_page_not_existing')
        elif node.is_mathsymbol():
            return ColorManager.get_ui_color('math')
        else:
            return ColorManager.get_ui_color('text')

    def draw_title(self, ctx, offset_x, offset_y):
        ctx.move_to(offset_x, offset_y)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('title_color'))
        self.view.layout_title.set_text(self.model.document.title)
        PangoCairo.show_layout(ctx, self.view.layout_title)

        ctx.move_to(offset_x, offset_y + self.view.title_height + 8)
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('description_color'))

        datetime_last_modified = datetime.datetime.fromtimestamp(self.model.document.last_modified)
        self.view.layout_subtitle.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))
        PangoCairo.show_layout(ctx, self.view.layout_subtitle)

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('border_1'))
        ctx.rectangle(offset_x, offset_y + self.view.title_height, self.view.title_width, 1)
        ctx.fill()

    def draw_cursor(self, ctx, offset_x, offset_y):
        if not self.content.has_focus(): return
        if self.model.document.cursor.has_selection(): return

        insert = self.model.document.cursor.get_insert_node()
        layout = insert.layout
        x, y = insert.layout.get_absolute_xy()
        fontname = FontManager.get_fontname_from_node(insert)
        padding_top = FontManager.get_padding_top(fontname)
        padding_bottom = FontManager.get_padding_bottom(fontname)
        cursor_coords = (x + offset_x, y + offset_y + padding_top, 1, layout.height - padding_top - padding_bottom)

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('cursor'))
        ctx.rectangle(*cursor_coords)
        ctx.fill()


