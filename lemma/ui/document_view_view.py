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

from lemma.ui.context_menu import ContextMenu
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

        self.link_overlay = Gtk.Label.new('http://url')
        self.link_overlay.set_valign(Gtk.Align.END)
        self.link_overlay.set_halign(Gtk.Align.END)
        self.link_overlay.add_css_class('link-overlay')
        self.add_overlay(self.link_overlay)

        self.context_menu = ContextMenuDocumentView(self)


class DocumentViewDrawingArea(Gtk.Widget):

    def __init__(self, model):
        Gtk.Widget.__init__(self)
        self.model = model

        self.set_focusable(True)
        self.set_vexpand(True)

        self.colors = dict()

        self.render_cache = dict()
        self.last_rendered_document = None
        self.last_cache_reset = time.time()

    def update(self):
        if self.model.document == None: return

        new_active_document = self.model.document != self.last_rendered_document
        document_changed = max(self.model.document.last_cursor_movement, self.model.document.last_modified) > self.last_cache_reset
        if new_active_document or document_changed:
            self.render_cache = dict()
            self.last_rendered_document = self.model.document
            self.last_cache_reset = time.time()
        self.queue_draw()

    @timer.timer
    def do_snapshot(self, snapshot):
        if self.model.document == None: return
        document = self.model.document

        ctx = snapshot.append_cairo(Graphene.Rect().init(0, 0, self.get_allocated_width(), self.get_allocated_height()))

        self.height = self.get_allocated_height()

        self.layout_title = Pango.Layout(self.get_pango_context())
        self.layout_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_title.set_font_description(Pango.FontDescription.from_string('NewComputerModernSans10 Regular 36px'))

        self.layout_subtitle = Pango.Layout(self.get_pango_context())
        self.layout_subtitle.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_subtitle.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.hidpi_factor = self.get_native().get_surface().get_scale()
        self.hidpi_factor_inverted = 1 / self.hidpi_factor
        self.matrix_default = ctx.get_matrix()
        ctx.scale(self.hidpi_factor_inverted, self.hidpi_factor_inverted)
        self.matrix_scaled = ctx.get_matrix()
        ctx.set_matrix(self.matrix_default)

        self.colors['text'] = ColorManager.get_ui_color('text')
        self.colors['links'] = ColorManager.get_ui_color('links')
        self.colors['links_page_not_existing'] = ColorManager.get_ui_color('links_page_not_existing')
        self.colors['selection_bg'] = ColorManager.get_ui_color('selection_bg')
        self.colors['title_color'] = ColorManager.get_ui_color('title_color')
        self.colors['description_color'] = ColorManager.get_ui_color('description_color')
        self.colors['border_1'] = ColorManager.get_ui_color('border_1')
        self.colors['cursor'] = ColorManager.get_ui_color('cursor')

        offset_x = ApplicationState.get_value('document_padding_left')
        scrolling_offset_y = document.clipping.offset_y
        offset_y = ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height') - scrolling_offset_y
        self.first_selection_node = document.cursor.get_first_node()
        self.last_selection_node = document.cursor.get_last_node()
        first_selection_line = document.get_ancestors(self.first_selection_node.layout)[-2]
        last_selection_line = document.get_ancestors(self.last_selection_node.layout)[-2]

        self.draw_title(ctx, ApplicationState.get_value('document_padding_left'), ApplicationState.get_value('document_padding_top') - scrolling_offset_y)

        Gdk.cairo_set_source_rgba(ctx, self.colors['text'])

        in_selection = False
        for i, paragraph in enumerate(document.ast.lines):
            for j, line_layout in enumerate(paragraph['layout']['children']):
                if offset_y + line_layout['y'] + paragraph['layout']['y'] + line_layout['height'] >= 0 and offset_y + line_layout['y'] + paragraph['layout']['y'] <= self.height:
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

            fontname = FontHelper.get_fontname_from_node(layout['node'])
            baseline = TextShaper.get_ascend(fontname=fontname)

            ctx.set_matrix(self.matrix_scaled)

            if fontname != 'emojis':
                fg_color = self.get_fg_color_by_node(layout['node'])
                surface, left, top = TextRenderer.get_glyph(layout['node'].value, fontname=fontname, scale=self.hidpi_factor)
                if surface != None:
                    ctx.set_source_surface(surface, (offset_x + layout['x']) * self.hidpi_factor + left, (offset_y + baseline + layout['y']) * self.hidpi_factor + top)

                    pattern = ctx.get_source()
                    pattern.set_filter(cairo.Filter.BEST)
                    Gdk.cairo_set_source_rgba(ctx, fg_color)
                    ctx.mask(pattern)
                    ctx.fill()
            else:
                surface, left, top = TextRenderer.get_glyph(layout['node'].value, fontname=fontname, scale=self.hidpi_factor)
                if surface != None:
                    ctx.set_matrix(self.matrix_scaled)

                    ctx.set_source_surface(surface, (offset_x + layout['x']) * self.hidpi_factor + left, (offset_y + baseline + layout['y']) * self.hidpi_factor + top)

                    ctx.mask(ctx.get_source())
                    ctx.fill()

            ctx.set_matrix(self.matrix_default)

        if layout['type'] == 'widget':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            widget = layout['node'].value
            surface = widget.get_cairo_surface()
            fontname = FontHelper.get_fontname_from_node(layout['node'])
            top = -TextShaper.get_descend(fontname=fontname)

            matrix = ctx.get_matrix()
            widget_factor_x = widget.get_width() / widget.get_original_width()
            widget_factor_y = widget.get_height() / widget.get_original_height()
            ctx.scale(widget_factor_x, widget_factor_y)

            ctx.set_source_surface(surface, (offset_x + layout['x']) / widget_factor_x, (offset_y + layout['y'] + top) / widget_factor_y)
            ctx.rectangle((offset_x + layout['x']) / widget_factor_x, (offset_y + layout['y'] + top) / widget_factor_y, layout['width'] / widget_factor_x, layout['height'] / widget_factor_y)
            ctx.fill()

            ctx.set_matrix(self.matrix_default)

        if layout['type'] == 'placeholder':
            if in_selection: self.draw_selection(layout, ctx, offset_x, offset_y)

            fontname = FontHelper.get_fontname_from_node(layout['node'])
            baseline = TextShaper.get_ascend(fontname=fontname)

            fg_color = self.get_fg_color_by_node(layout['node'])
            surface, left, top = TextRenderer.get_glyph('▯', fontname=fontname, scale=self.hidpi_factor)

            ctx.set_matrix(self.matrix_scaled)

            ctx.set_source_surface(surface, (offset_x + layout['x']) * self.hidpi_factor + left, (offset_y + baseline + layout['y']) * self.hidpi_factor + top)
            pattern = ctx.get_source()
            pattern.set_filter(cairo.Filter.BEST)
            Gdk.cairo_set_source_rgba(ctx, fg_color)
            ctx.mask(pattern)
            ctx.fill()

            ctx.set_matrix(self.matrix_default)

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

            line_offset = layout['children'][0]['children'][1]['height']
            line_width = layout['width']

            ctx.rectangle(offset_x + layout['x'] + 1, offset_y + line_offset + 1, line_width - 2, 1)
            ctx.fill()

    def draw_selection(self, layout, ctx, offset_x, offset_y):
        Gdk.cairo_set_source_rgba(ctx, self.colors['selection_bg'])
        ctx.rectangle(offset_x + layout['x'], offset_y, layout['width'], layout['parent']['height'])
        ctx.fill()

    def get_fg_color_by_node(self, node):
        if node.link != None:
            if node.link.startswith('http') or DocumentRepo.get_by_title(node.link) != None:
                return self.colors['links']
            else:
                return self.colors['links_page_not_existing']
        else:
            return self.colors['text']

    @timer.timer
    def draw_title(self, ctx, offset_x, offset_y):
        self.layout_title.set_width(ApplicationState.get_value('title_width') * Pango.SCALE)
        self.layout_title.set_text(self.model.document.title)
        ctx.move_to(offset_x, offset_y)
        Gdk.cairo_set_source_rgba(ctx, self.colors['title_color'])
        PangoCairo.show_layout(ctx, self.layout_title)

        self.layout_subtitle.set_width(ApplicationState.get_value('title_width') * Pango.SCALE)
        datetime_last_modified = datetime.datetime.fromtimestamp(self.model.document.last_modified)
        self.layout_subtitle.set_text('{datetime:%a}, {datetime.day} {datetime:%b} {datetime.year} - {datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified))
        ctx.move_to(offset_x, offset_y + ApplicationState.get_value('title_height') + 8)
        Gdk.cairo_set_source_rgba(ctx, self.colors['description_color'])
        PangoCairo.show_layout(ctx, self.layout_subtitle)

        Gdk.cairo_set_source_rgba(ctx, self.colors['border_1'])
        ctx.rectangle(offset_x, offset_y + ApplicationState.get_value('title_height'), ApplicationState.get_value('title_width'), 1)
        ctx.fill()

    def draw_cursor(self, ctx, offset_x, offset_y):
        if not self.is_focus() and ApplicationState.get_value('document_view_hide_cursor_on_unfocus'): return
        if self.model.document.cursor.has_selection(): return

        insert = self.model.document.cursor.get_insert_node()
        layout = insert.layout
        x, y = self.model.document.get_absolute_xy(layout)
        fontname = FontHelper.get_fontname_from_node(insert)
        padding_top = TextShaper.get_padding_top(fontname)
        padding_bottom = 0#TextShaper.get_padding_bottom(fontname)
        cursor_coords = (x + offset_x, y + offset_y + padding_top, 1, layout['height'] - padding_top - padding_bottom)

        Gdk.cairo_set_source_rgba(ctx, self.colors['cursor'])
        ctx.rectangle(*cursor_coords)
        ctx.fill()

    def do_size_allocate(self, width, height, baseline):
        self.model.set_size(width, height)


class ContextMenuDocumentView(ContextMenu):
    
    def __init__(self, parent):
        ContextMenu.__init__(self)

        self.popover.set_parent(parent)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)

        self.open_link_button = self.create_button(_('Open Link'))
        self.open_link_button.set_action_name('win.open-link')
        self.box.append(self.open_link_button)

        self.open_link_separator = Gtk.Separator()
        self.box.append(self.open_link_separator)

        self.copy_link_button = self.create_button('Copy Link Target')
        self.copy_link_button.set_action_name('win.copy-link')
        self.box.append(self.copy_link_button)

        self.remove_link_button = self.create_button('Remove Link')
        self.remove_link_button.set_action_name('win.remove-link')
        self.box.append(self.remove_link_button)

        self.edit_link_button = self.create_button('Edit Link')
        self.edit_link_button.set_action_name('win.edit-link')
        self.box.append(self.edit_link_button)

        self.link_buttons_separator = Gtk.Separator()
        self.box.append(self.link_buttons_separator)

        self.back_button = self.create_button('Back', _('Alt') + '+Left Arrow')
        self.back_button.set_action_name('win.go-back')
        self.box.append(self.back_button)

        self.forward_button = self.create_button('Forward', _('Alt') + '+Right Arrow')
        self.forward_button.set_action_name('win.go-forward')
        self.box.append(self.forward_button)

        self.back_forward_separator = Gtk.Separator()
        self.box.append(self.back_forward_separator)

        self.cut_button = self.create_button('Cut', _('Ctrl') + '+X')
        self.cut_button.set_action_name('win.cut')
        self.box.append(self.cut_button)

        self.copy_button = self.create_button('Copy', _('Ctrl') + '+C')
        self.copy_button.set_action_name('win.copy')
        self.box.append(self.copy_button)

        self.paste_button = self.create_button('Paste', _('Ctrl') + '+V')
        self.paste_button.set_action_name('win.paste')
        self.box.append(self.paste_button)

        self.delete_button = self.create_button('Delete')
        self.delete_button.set_action_name('win.delete')
        self.box.append(self.delete_button)

        self.box.append(Gtk.Separator())

        self.select_all_button = self.create_button('Select All', _('Ctrl') + '+A')
        self.select_all_button.set_action_name('win.select-all')
        self.box.append(self.select_all_button)


