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
from gi.repository import Gtk, Gdk

from lemma.ui.views.scrollbars import ScrollbarVertical, ScrollbarHorizontal
from lemma.ui.helpers.observable import Observable


class OverviewView(Gtk.Overlay, Observable):

    def __init__(self):
        Gtk.Overlay.__init__(self)
        Observable.__init__(self)
        self.add_css_class('overview')

        self.set_focusable(True)

        self.content = DrawingArea()
        self.scrollbar_vertical = ScrollbarVertical()
        self.scrollbar_horizontal = ScrollbarHorizontal()

        self.add_overlay(self.scrollbar_vertical)
        self.add_overlay(self.scrollbar_horizontal)
        self.set_child(self.content)

        self.__scrolling_multiplier = 2.5

        self.view_width = 0
        self.view_height = 0
        self.content_width = 0
        self.content_height = 0
        self.scroll_x = 0
        self.scroll_y = 0

        self.__pointer_func = lambda snapshot: None
        self.__setup_signals()

    def set_content_size(self, width, height):
        self.content_width = width
        self.content_height = height

        self.__update_scrollbars()
        self.content.queue_draw()

    def scroll_to(self, x, y):
        self.__set_scroll(x, y)

        self.__update_scrollbars()
        self.content.queue_draw()

    def set_draw_func(self, draw_func):
        self.content.draw_func = draw_func

    def set_pointer_func(self, pointer_func):
        self.__pointer_func = pointer_func

    def __setup_signals(self):
        self.content.allocate_func = self.__size_allocate

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.__on_scroll)
        self.content.add_controller(self.scrolling_controller)

        self.scrollbar_vertical.observe('dragged', self.__on_vertical_scrollbar_drag)
        self.scrollbar_horizontal.observe('dragged', self.__on_horizontal_scrollbar_drag)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.__on_enter)
        self.motion_controller.connect('motion', self.__on_hover)
        self.motion_controller.connect('leave', self.__on_leave)
        self.content.add_controller(self.motion_controller)

    def __size_allocate(self, width, height, baseline):
        self.view_width = width
        self.view_height = height

    def __on_enter(self, controller, x, y):
        self.pointer_x = x
        self.pointer_y = y
        self.__pointer_func()

        self.__update_scrollbars()
        self.content.queue_draw()

    def __on_hover(self, controller, x, y):
        self.pointer_x = x
        self.pointer_y = y
        self.__pointer_func()

        self.__update_scrollbars()
        self.content.queue_draw()

    def __on_leave(self, controller):
        self.pointer_x = None
        self.pointer_y = None
        self.__pointer_func()

        self.__update_scrollbars()
        self.content.queue_draw()

    def __on_scroll(self, controller, dx, dy):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            dy *= self.__scrolling_multiplier
            dx *= self.__scrolling_multiplier

            scroll_x = self.scroll_x + dx
            scroll_y = self.scroll_y + dy
            self.__set_scroll(scroll_x, scroll_y)

            self.__update_scrollbars()
            self.content.queue_draw()

        if controller.get_current_event_state() & modifiers == Gdk.ModifierType.CONTROL_MASK:
            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                zoom_amount = dy * 0.1
            else:
                zoom_amount = (dy + dx) * 0.005
            self.add_change_code('zoom', zoom_amount)

    def __on_horizontal_scrollbar_drag(self, widget, new_x):
        self.__set_scroll(new_x, self.scroll_y)

        self.__update_scrollbars()
        self.content.queue_draw()

    def __on_vertical_scrollbar_drag(self, widget, new_y):
        self.__set_scroll(self.scroll_x, new_y)

        self.__update_scrollbars()
        self.content.queue_draw()

    def __set_scroll(self, x, y):
        if self.content_width < self.view_width:
            self.scroll_x = (self.content_width - self.view_width) / 2
        else:
            self.scroll_x = max(0, min(self.content_width - self.view_width, x))

        if self.content_height < self.view_height:
            self.scroll_y = (self.content_height - self.view_height) / 2
        else:
            self.scroll_y = max(0, min(self.content_height - self.view_height, y))

    def __update_scrollbars(self):
        self.scrollbar_horizontal.set_content_width(self.content_width)
        self.scrollbar_horizontal.set_scrolling_offset(self.scroll_x)
        self.scrollbar_horizontal.ping()
        self.scrollbar_vertical.set_content_height(self.content_height)
        self.scrollbar_vertical.set_scrolling_offset(self.scroll_y)
        self.scrollbar_vertical.ping()


class DrawingArea(Gtk.Widget):

    def __init__(self):
        Gtk.Widget.__init__(self)

        self.set_vexpand(True)

        self.draw_func = lambda snapshot: None
        self.allocate_func = lambda width, height, baseline: None

    def do_snapshot(self, snapshot):
        self.draw_func(snapshot)

    def do_size_allocate(self, width, height, baseline):
        self.allocate_func(width, height, baseline)


