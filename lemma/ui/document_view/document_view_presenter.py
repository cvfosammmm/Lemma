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
        self.cursor_coords = None
        self.current_node_in_selection = False
        self.scrolling_job = None
        self.fontname = None
        self.fg_color = None

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
            leaf_box = document.layout.get_leaf_at_xy(x, y)
            if leaf_box != None:
                node = leaf_box.get_node()
                if node.link != None:
                    self.content.set_cursor_from_name('pointer')
                    link = node.link
                elif node.type.is_widget():
                    self.content.set_cursor_from_name(node.value.get_cursor_name())
                else:
                    self.content.set_cursor_from_name('text')
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
        insert_position = insert_node.get_xy()
        content_offset = self.view.padding_top + self.view.title_height + self.view.subtitle_height
        insert_y = insert_position[1] + content_offset
        insert_height = insert_node.box.parent.height
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

        self.cursor_coords = None
        self.current_node_in_selection = False
        self.first_cursor_node = self.model.document.cursor.get_first_node()
        self.last_cursor_node = self.model.document.cursor.get_last_node()
        scrolling_offset_y = self.model.document.clipping.offset_y

        self.draw_title(ctx, self.view.padding_left, self.view.padding_top - scrolling_offset_y)

        self.draw_box(ctx, self.model.document.layout, self.view.padding_left, self.view.padding_top + self.view.title_height + self.view.subtitle_height + self.view.title_buttons_height - scrolling_offset_y)

        self.draw_cursor(ctx)

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

    def draw_box(self, ctx, box, offset_x, offset_y):
        if box.type == 'vcontainer':
            for child in box.children:
                self.draw_box(ctx, child, offset_x, offset_y)
                offset_y += child.height

        if box.type == 'hcontainer':
            for child in box.children:
                self.draw_box(ctx, child, offset_x, offset_y)
                offset_x += child.width

        if box == self.model.document.cursor.get_insert_node().box and not self.model.document.cursor.has_selection():
            self.cursor_coords = (offset_x, offset_y + box.parent.height - box.height, 1, box.height)
        if box.node == self.first_cursor_node:
            self.current_node_in_selection = True
        if box.node == self.last_cursor_node:
            self.current_node_in_selection = False

        if box.type in ['glyph', 'empty']:
            self.update_fontname(box.node)
            self.update_fg_color(box.node)

        if box.type in ['glyph', 'widget']:
            if self.current_node_in_selection:
                Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('selection_bg'))
                ctx.rectangle(offset_x, offset_y, box.width, box.parent.height)
                ctx.fill()

        if box.type == 'glyph':
            surface = FontManager.get_surface(box.node.value, fontname=self.fontname)

            if surface != None:
                ctx.set_source_surface(surface, offset_x + box.left, offset_y + box.parent.height + box.top)
                pattern = ctx.get_source()
                pattern.set_filter(cairo.Filter.BEST)
                Gdk.cairo_set_source_rgba(ctx, self.fg_color)
                ctx.mask(pattern)
                ctx.fill()

        if box.type == 'widget':
            surface = box.node.value.get_cairo_surface()
            ctx.set_source_surface(surface, offset_x + box.left, offset_y + box.parent.height - box.height + box.top)
            ctx.rectangle(offset_x + box.left, offset_y + box.parent.height - box.height + box.top, box.width, box.height)
            ctx.fill()

    def draw_cursor(self, ctx):
        if self.cursor_coords == None: return
        if not self.content.has_focus(): return

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('cursor'))
        ctx.rectangle(*self.cursor_coords)
        ctx.fill()

    def update_fontname(self, node):
        if node.type.is_mathsymbol():
            self.fontname = 'math'
        elif node.paragraph_style.startswith('h'):
            self.fontname = node.paragraph_style
        elif 'bold' in node.tags and 'italic' not in node.tags:
            self.fontname = 'bold'
        elif 'bold' in node.tags and 'italic' in node.tags:
            self.fontname = 'bolditalic'
        elif 'bold' not in node.tags and 'italic' in node.tags:
            self.fontname = 'italic'
        else:
            self.fontname = 'book'

    def update_fg_color(self, node):
        if node.type.is_mathsymbol():
            self.fg_color = ColorManager.get_ui_color('math')
        elif node.link != None:
            if urlparse(node.link.target).scheme in ['http', 'https'] or self.model.workspace.get_by_title(node.link.target) != None:
                self.fg_color = ColorManager.get_ui_color('links')
            else:
                self.fg_color = ColorManager.get_ui_color('links_page_not_existing')
        else:
            self.fg_color = ColorManager.get_ui_color('text')


