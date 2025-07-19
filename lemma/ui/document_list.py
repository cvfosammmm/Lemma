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

import time, datetime

from lemma.document_repo.document_repo import DocumentRepo
from lemma.history.history import History
from lemma.infrastructure.color_manager import ColorManager
from lemma.ui.shortcuts import ShortcutController
from lemma.application_state.application_state import ApplicationState
from lemma.message_bus.message_bus import MessageBus


class DocumentList(object):

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.use_cases = application.use_cases
        self.view = main_window.document_list

        self.document_ids = DocumentRepo.list()
        self.search_terms = []
        self.selected_index = None

        self.view.scrolling_widget.connect('primary_button_press', self.on_primary_button_press)
        self.view.scrolling_widget.connect('primary_button_release', self.on_primary_button_release)
        self.view.scrolling_widget.connect('secondary_button_press', self.on_secondary_button_press)
        self.main_window.headerbar.hb_left.search_entry.connect('changed', self.on_search_entry_changed)
        self.main_window.headerbar.hb_left.search_entry.connect('icon-release', self.on_search_entry_icon_released)
        self.shortcuts_controller = ShortcutController()
        self.shortcuts_controller.add_with_callback('Escape', self.stop_search)
        self.main_window.headerbar.hb_left.search_entry.add_controller(self.shortcuts_controller)

        self.view.content.set_draw_func(self.draw)

        self.view.context_menu.delete_document_button.connect('clicked', self.on_delete_document_clicked)
        self.view.context_menu.popover.connect('closed', self.on_context_menu_close)

    def update(self):
        self.document_ids = [doc_id for doc_id in DocumentRepo.list() if self.search_terms_in_document(DocumentRepo.get_by_id(doc_id))]
        self.view.scrolling_widget.set_size(1, max(len(self.document_ids) * self.view.line_height, 1))
        self.view.scrolling_widget.queue_draw()

    def set_selected_index(self, index):
        if index != self.selected_index:
            self.selected_index = index
            self.view.content.queue_draw()

    def activate_item(self, index):
        document = DocumentRepo.get_by_id(self.document_ids[index])
        self.use_cases.set_active_document(document)

    def on_primary_button_press(self, scrolling_widget, data):
        x_offset, y_offset, state = data

        if state == 0:
            item_num = self.get_item_at_cursor()
            if item_num != None and item_num < len(self.document_ids):
                self.set_selected_index(item_num)

    def on_primary_button_release(self, scrolling_widget, data):
        x_offset, y_offset, state = data

        item_num = self.get_item_at_cursor()
        if item_num != None and item_num == self.selected_index:
            self.activate_item(item_num)
        self.set_selected_index(None)

    def on_secondary_button_press(self, content, data):
        x, y, state = data

        if state == 0:
            item_num = self.get_item_at_cursor()
            if item_num != None and item_num < len(self.document_ids):
                self.set_selected_index(item_num)
                self.view.context_menu.popup_at_cursor(x - content.scrolling_offset_x, y - content.scrolling_offset_y)

        return True

    def on_context_menu_close(self, popover):
        self.set_selected_index(None)

    def on_delete_document_clicked(self, button):
        document = DocumentRepo.get_by_id(self.document_ids[self.selected_index])
        self.use_cases.delete_document(document)
        self.view.context_menu.popover.popdown()

    def on_search_entry_changed(self, entry, data=None):
        self.search_terms = entry.get_text().split()
        entry = self.main_window.headerbar.hb_left.search_entry

        if len(self.search_terms) > 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'edit-clear-symbolic')
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)

        self.update()

    def on_search_entry_icon_released(self, entry, icon_pos, data=None):
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            self.main_window.headerbar.hb_left.search_entry.set_text('')

    def stop_search(self):
        self.main_window.headerbar.hb_left.search_entry.set_text('')
        self.main_window.document_view.content.grab_focus()

    def draw(self, widget, ctx, width, height):
        sidebar_fg_1 = ColorManager.get_ui_color('sidebar_fg_1')
        sidebar_fg_2 = ColorManager.get_ui_color('sidebar_fg_2')
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
        Gdk.cairo_set_source_rgba(ctx, sidebar_fg_1)

        for i, document_id in enumerate(self.document_ids):
            document = DocumentRepo.get_by_id(document_id)
            mode = ApplicationState.get_value('mode')
            highlight_active = (document == History.get_active_document() and mode == 'documents')
            if highlight_active:
                title_color = active_fg_color
                teaser_color = active_fg_color
                date_color = active_fg_color
            else:
                title_color = sidebar_fg_1
                teaser_color = sidebar_fg_1
                date_color = sidebar_fg_1

            if i == self.selected_index:
                Gdk.cairo_set_source_rgba(ctx, selected_color)
                ctx.rectangle(0, self.view.line_height * i - scrolling_offset, width, self.view.line_height)
                ctx.fill()
            elif not highlight_active and i == self.get_item_at_cursor():
                Gdk.cairo_set_source_rgba(ctx, hover_color)
                ctx.rectangle(0, self.view.line_height * i - scrolling_offset, width, self.view.line_height)
                ctx.fill()
            if highlight_active:
                Gdk.cairo_set_source_rgba(ctx, active_bg_color)
                ctx.rectangle(0, self.view.line_height * i - scrolling_offset, width, self.view.line_height)
                ctx.fill()

            title_text = document.title
            if len(document.plaintext) == 0:
                teaser_text = '(' + _('empty') + ')'
                teaser_color = sidebar_fg_2
            else:
                teaser_text = ' '.join(document.plaintext.splitlines())[:100].strip()
            date_text = self.get_last_modified_string(document)

            Gdk.cairo_set_source_rgba(ctx, title_color)
            ctx.move_to(15, self.view.line_height * i + 14 - scrolling_offset)
            self.view.layout_header.set_text(title_text)
            PangoCairo.show_layout(ctx, self.view.layout_header)

            Gdk.cairo_set_source_rgba(ctx, date_color)
            ctx.move_to(15, self.view.line_height * i + 14 - scrolling_offset)
            self.view.layout_date.set_text(date_text)
            PangoCairo.show_layout(ctx, self.view.layout_date)

            Gdk.cairo_set_source_rgba(ctx, teaser_color)
            ctx.move_to(15, self.view.line_height * i + 37 - scrolling_offset)
            self.view.layout_teaser.set_text(teaser_text)
            PangoCairo.show_layout(ctx, self.view.layout_teaser)

    def get_last_modified_string(self, document):
        datetime_today, datetime_this_week, datetime_this_year = self.get_datetimes_today_week_year()
        datetime_last_modified = datetime.datetime.fromtimestamp(document.last_modified)
        if document.last_modified >= datetime_today.timestamp():
            return '{datetime.hour}:{datetime.minute:02}'.format(datetime=datetime_last_modified)
        elif document.last_modified >= datetime_this_week.timestamp():
            return '{datetime:%a}'.format(datetime=datetime_last_modified)
        elif document.last_modified >= datetime_this_year.timestamp():
            return '{datetime.day} {datetime:%b}'.format(datetime=datetime_last_modified)
        else:
            return '{datetime.day} {datetime:%b} {datetime.year}'.format(datetime=datetime_last_modified)

    def get_datetimes_today_week_year(self):
        date_today = datetime.date.today()
        datetime_today = datetime.datetime.combine(date_today, datetime.time(0, 0))
        date_this_week = datetime.date.fromtimestamp(time.time() - date_today.weekday() * 86400)
        datetime_this_week = datetime.datetime.combine(date_this_week, datetime.time(0, 0))
        date_this_year = datetime.date(date_today.year, 1, 1)
        datetime_this_year = datetime.datetime.combine(date_this_year, datetime.time(0, 0))
        return (datetime_today, datetime_this_week, datetime_this_year)

    def search_terms_in_document(self, document):
        if len(self.search_terms) == 0: return True
        return min(map(lambda x: x in document.plaintext or x in document.title, self.search_terms))

    def get_item_at_cursor(self):
        y = self.view.scrolling_widget.cursor_y
        x = self.view.scrolling_widget.cursor_x

        if y == None or x == None or x > self.view.scrolling_widget.width - 12: return None
        return int((y + self.view.scrolling_widget.adjustment_y.get_value()) // self.view.line_height)


