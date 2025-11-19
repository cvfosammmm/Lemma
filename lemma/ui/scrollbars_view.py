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
from gi.repository import Gtk, Gdk, Gsk, Graphene

from lemma.services.color_manager import ColorManager


class ScrollbarViewVertical(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)
        self.add_css_class('scrollbar-vertical')

        self.set_size_request(20, -1)

        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.FILL)

        self.width = 0
        self.height = 0

        self.slider_offset = 0
        self.slider_height = 1
        self.pointer_pos = None
        self.drag_in_progress = False

        self.set_can_target(False)

    def set_attributes(self, total_height, scrolling_offset, pointer_pos, drag_pos):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        slider_height = max(60, min(height, height * height / total_height))
        slider_pos_fraction = scrolling_offset / (total_height - height)
        slider_offset = slider_pos_fraction * (height - slider_height)
        drag_in_progress = (drag_pos != None)

        if slider_offset != self.slider_offset or slider_height != self.slider_height or pointer_pos != self.pointer_pos or width != self.width or height != self.height or drag_in_progress != self.drag_in_progress:
            self.slider_offset = slider_offset
            self.slider_height = slider_height
            self.pointer_pos = pointer_pos
            self.drag_in_progress = drag_in_progress
            self.width = width
            self.height = height

            self.set_can_target(slider_height < height)
            self.queue_draw()

    def do_snapshot(self, snapshot):
        visible_width = 8 if self.pointer_pos != None else 3

        if self.slider_height >= self.height: return

        if self.pointer_pos != None:
            rect = Graphene.Rect().init(self.width - 6 - visible_width, 6, visible_width, self.height - 12)
            rounded_rect = Gsk.RoundedRect()
            rounded_rect.init_from_rect(rect, 20)
            snapshot.push_rounded_clip(rounded_rect)
            snapshot.append_color(ColorManager.get_ui_color('scrollbar_bg'), rect)
            snapshot.pop()

        if self.pointer_pos != None:
            if self.drag_in_progress:
                slider_color = ColorManager.get_ui_color('scrollbar_active')
            elif self.pointer_pos > self.slider_offset and self.pointer_pos < self.slider_offset + self.slider_height:
                slider_color = ColorManager.get_ui_color('scrollbar_hover')
            else:
                slider_color = ColorManager.get_ui_color('scrollbar_default')
        else:
            slider_color = ColorManager.get_ui_color('scrollbar_thin')

        rect = Graphene.Rect().init(self.width - 6 - visible_width, self.slider_offset + 6, visible_width, self.slider_height - 12)
        rounded_rect = Gsk.RoundedRect()
        rounded_rect.init_from_rect(rect, 20)
        snapshot.push_rounded_clip(rounded_rect)
        snapshot.append_color(slider_color, rect)
        snapshot.pop()


