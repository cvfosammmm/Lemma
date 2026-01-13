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
from gi.repository import Gtk, Gsk, Graphene

import time

from lemma.services.color_manager import ColorManager
from lemma.ui.helpers.observable import Observable


class ScrollbarVertical(Gtk.Widget, Observable):

    def __init__(self):
        Gtk.Widget.__init__(self)
        Observable.__init__(self)

        self.add_css_class('scrollbar-vertical')
        self.set_size_request(20, -1)

        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.FILL)
        self.set_can_target(False)

        self.pointer_pos = None
        self.view_width = 20
        self.view_height = 0
        self.total_height = 1
        self.scrolling_offset = 0
        self.drag_in_progress = False
        self.drag_start_x, self.drag_start_y = (None, None)

        self.last_ping = 0
        self.pointer_entry_time = 0
        self.visibility_timeout = False
        self.is_visible = False

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_hover)
        self.add_controller(self.motion_controller)

        self.drag_controller = Gtk.GestureDrag()
        self.drag_controller.connect('drag-begin', self.on_drag_begin)
        self.drag_controller.connect('drag-update', self.on_drag_update)
        self.drag_controller.connect('drag-end', self.on_drag_end)
        self.add_controller(self.drag_controller)

        self.add_tick_callback(self.animate)

    def animate(self, widget, frame_clock):
        self.set_view_height(self.get_allocated_height())
        self.set_visibility_timeout(self.pointer_entry_time != None and (time.time() - self.pointer_entry_time > 0.1))
        self.set_is_visible(self.pointer_pos != None or time.time() - self.last_ping < 2)

        return True

    def on_enter(self, controller, x=None, y=None):
        self.set_pointer_entry_time(time.time())
        self.set_pointer_pos(y)

    def on_hover(self, controller, x=None, y=None):
        self.set_pointer_pos(y)

    def on_drag_begin(self, gesture, x, y, data=None):
        self.set_drag_in_progress(True)

        view_height = self.view_height
        slider_height = max(60, min(view_height, view_height * view_height / self.total_height))
        slider_pos_fraction = self.scrolling_offset / (self.total_height - view_height)
        slider_offset = slider_pos_fraction * (view_height - max(60, min(view_height, view_height * view_height / self.total_height)))

        if y < slider_offset or y > slider_offset + slider_height:
            new_y = self.get_y_offset(y)
            self.add_change_code('dragged', new_y)

            self.drag_start_x, self.drag_start_y = (x, y)
        else:
            self.drag_start_x, self.drag_start_y = (x, slider_offset + slider_height / 2)

    def on_drag_update(self, gesture, x, y, data=None):
        y += self.drag_start_y
        new_y = self.get_y_offset(y)
        self.add_change_code('dragged', new_y)

    def on_drag_end(self, gesture, x, y, data=None):
        self.set_drag_in_progress(False)

    def set_pointer_entry_time(self, pointer_entry_time):
        if pointer_entry_time != self.pointer_entry_time:
            self.pointer_entry_time = pointer_entry_time

    def set_pointer_pos(self, pointer_pos):
        if pointer_pos != self.pointer_pos:
            self.pointer_pos = pointer_pos
            self.queue_draw()

    def set_drag_in_progress(self, drag_in_progress):
        if drag_in_progress != self.drag_in_progress:
            self.drag_in_progress = drag_in_progress
            self.queue_draw()

    def set_view_height(self, view_height):
        if view_height != self.view_height:
            self.view_height = view_height

            slider_height = max(60, min(self.view_height, self.view_height * self.view_height / self.total_height))
            self.set_can_target(slider_height < self.view_height)
            self.queue_draw()

    def set_total_height(self, total_height):
        if total_height != self.total_height:
            self.total_height = total_height

            slider_height = max(60, min(self.view_height, self.view_height * self.view_height / self.total_height))
            self.set_can_target(slider_height < self.view_height)
            self.queue_draw()

    def set_scrolling_offset(self, scrolling_offset):
        if scrolling_offset != self.scrolling_offset:
            self.scrolling_offset = scrolling_offset
            self.queue_draw()

    def set_visibility_timeout(self, visibility_timeout):
        if visibility_timeout != self.visibility_timeout:
            self.visibility_timeout = visibility_timeout
            self.queue_draw()

    def set_is_visible(self, is_visible):
        if is_visible != self.is_visible:
            self.is_visible = is_visible
            self.queue_draw()

    def ping(self):
        self.last_ping = time.time()

    def get_y_offset(self, y):
        slider_height = max(60, min(self.view_height, self.view_height * self.view_height / self.total_height))
        y_in_range = max(slider_height / 2, min(self.view_height - slider_height / 2, y)) - slider_height / 2
        y_fraction = y_in_range / (self.view_height - slider_height)
        return int(y_fraction * (self.total_height - self.view_height))

    def do_snapshot(self, snapshot):
        expand_width = self.pointer_pos != None and self.visibility_timeout == True

        visible_width = 8 if expand_width else 3
        slider_height = max(60, min(self.view_height, self.view_height * self.view_height / self.total_height))
        slider_pos_fraction = self.scrolling_offset / (self.total_height - self.view_height)
        slider_offset = slider_pos_fraction * (self.view_height - max(60, min(self.view_height, self.view_height * self.view_height / self.total_height)))

        if not self.is_visible: return
        if slider_height >= self.view_height: return

        if expand_width:
            rect = Graphene.Rect().init(self.view_width - 6 - visible_width, 6, visible_width, self.view_height - 12)
            rounded_rect = Gsk.RoundedRect()
            rounded_rect.init_from_rect(rect, 20)
            snapshot.push_rounded_clip(rounded_rect)
            snapshot.append_color(ColorManager.get_ui_color('scrollbar_bg'), rect)
            snapshot.pop()

        pointer_hovers_slider = self.pointer_pos != None and self.pointer_pos > slider_offset and self.pointer_pos < slider_offset + slider_height

        if expand_width:
            if self.drag_in_progress:
                slider_color = ColorManager.get_ui_color('scrollbar_active')
            elif pointer_hovers_slider:
                slider_color = ColorManager.get_ui_color('scrollbar_hover')
            else:
                slider_color = ColorManager.get_ui_color('scrollbar_default')
        else:
            slider_color = ColorManager.get_ui_color('scrollbar_thin')

        rect = Graphene.Rect().init(self.view_width - 6 - visible_width, slider_offset + 6, visible_width, slider_height - 12)
        rounded_rect = Gsk.RoundedRect()
        rounded_rect.init_from_rect(rect, 20)
        snapshot.push_rounded_clip(rounded_rect)
        snapshot.append_color(slider_color, rect)
        snapshot.pop()


