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
from gi.repository import GObject, Gdk, Gtk

import time

from lemma.ui.helpers.observable import Observable


class ScrollingWidget(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.scrolling_offset_x, self.scrolling_offset_y = 0, 0
        self.width, self.height = 0, 0
        self.cursor_x, self.cursor_y = None, None
        self.scrolling_multiplier = 2.5
        self.scrolling_job = None

        self.view = Gtk.Overlay()
        self.content = Gtk.DrawingArea()
        self.view.set_child(self.content)

        self.scrollbar_x = Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL)
        self.adjustment_x = self.scrollbar_x.get_adjustment()

        self.scrollbar_y = Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL)
        self.adjustment_y = self.scrollbar_y.get_adjustment()

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.on_scroll)
        self.scrolling_controller.connect('decelerate', self.on_decelerate)
        self.content.add_controller(self.scrolling_controller)

        self.adjustment_x.connect('changed', self.on_adjustment_changed)
        self.adjustment_x.connect('value-changed', self.on_adjustment_changed)
        self.adjustment_y.connect('changed', self.on_adjustment_changed)
        self.adjustment_y.connect('value-changed', self.on_adjustment_changed)
        self.content.connect('resize', self.on_resize)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_leave)
        self.view.add_controller(self.motion_controller)

    def queue_draw(self):
        self.content.queue_draw()

    def scroll_to_position(self, position, animate=False):
        window_width = self.width
        yoffset = max(position[1], 0)
        xoffset = max(position[0], 0)

        self.scrolling_job = {'from': (self.scrolling_offset_x, self.scrolling_offset_y), 'to': (xoffset, yoffset), 'starting_time': time.time(), 'duration': 0.2 if animate else 0}
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

        self.adjustment_x.set_value(new_x)
        self.adjustment_y.set_value(new_y)

        if (new_x, new_y) == self.scrolling_job['to']:
            self.scrolling_job = None
        else:
            GObject.timeout_add(15, self.scroll_now)

        return False

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0
        if abs(dy) > 0 and abs(dx / dy) >  1: dy = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= self.adjustment_x.get_page_size() ** (2/3)
                dy *= self.adjustment_y.get_page_size() ** (2/3)
            else:
                dy *= self.scrolling_multiplier
                dx *= self.scrolling_multiplier

            self.adjustment_x.set_value(self.adjustment_x.get_value() + dx)
            self.adjustment_y.set_value(self.adjustment_y.get_value() + dy)

    def on_decelerate(self, controller, vel_x, vel_y):
        if abs(vel_x) > 0 and abs(vel_y / vel_x) >= 1: vel_x = 0
        if abs(vel_y) > 0 and abs(vel_x / vel_y) >  1: vel_y = 0

        data = dict()
        data['starting_time'] = time.time()
        data['initial_position'] = (self.scrolling_offset_x, self.scrolling_offset_y)
        data['position'] = (self.scrolling_offset_x, self.scrolling_offset_y)
        data['velocity'] = (vel_x * self.scrolling_multiplier, vel_y * self.scrolling_multiplier)
        self.deceleration(data)

    def deceleration(self, data):
        if data['position'] != (self.scrolling_offset_x, self.scrolling_offset_y): return False

        time_elapsed = time.time() - data['starting_time']

        exponential_factor = 2.71828 ** (-4 * time_elapsed)
        position_x = data['initial_position'][0] + (1 - exponential_factor) * (data['velocity'][0] / 4)
        position_y = data['initial_position'][1] + (1 - exponential_factor) * (data['velocity'][1] / 4)

        if abs(data['velocity'][0] * exponential_factor) < 0.1 and abs(data['velocity'][1] * exponential_factor) < 0.1: return False

        self.scrolling_job = {'from': (self.scrolling_offset_x, self.scrolling_offset_y), 'to': (position_x, position_y), 'starting_time': time.time(), 'duration': 0}
        self.scroll_now()

        data['position'] = (position_x, position_y)
        GObject.timeout_add(15, self.deceleration, data)

        return False

    def on_resize(self, drawing_area, width, height):
        self.width, self.height = width, height

        self.adjustment_x.set_page_size(width)
        self.adjustment_y.set_page_size(height)

        if self.scrolling_offset_x > self.adjustment_x.get_upper() - self.width:
            self.adjustment_x.set_value(self.adjustment_x.get_upper())
        if self.scrolling_offset_y > self.adjustment_y.get_upper() - self.height:
            self.adjustment_y.set_value(self.adjustment_y.get_upper())

        self.content.queue_draw()

    def on_adjustment_changed(self, adjustment):
        self.scrolling_offset_y = self.adjustment_y.get_value()
        self.scrolling_offset_x = self.adjustment_x.get_value()
        self.content.queue_draw()

    def on_enter(self, controller, x, y):
        self.set_cursor_position(x, y)

    def on_hover(self, controller, x, y):
        self.set_cursor_position(x, y)

    def on_leave(self, controller):
        self.set_cursor_position(None, None)

    def set_size(self, x, y):
        self.adjustment_x.set_upper(x)
        self.adjustment_y.set_upper(y)
        if self.scrolling_offset_y > max(0, y - self.height):
            self.scrolling_job = {'from': (self.scrolling_offset_x, self.scrolling_offset_y), 'to': (self.scrolling_offset_x, max(0, y - self.height)), 'starting_time': time.time(), 'duration': 0}
            self.scroll_now()

    def set_cursor_position(self, x, y):
        if x != self.cursor_x or y != self.cursor_y:
            self.cursor_x, self.cursor_y = x, y
            self.content.queue_draw()


