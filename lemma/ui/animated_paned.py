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
from gi.repository import Gtk


class AnimatedPaned(object):

    def __init__(self, widget1, widget2, animate_first_widget=True):
        self.animate_first_widget = animate_first_widget
        if animate_first_widget:
            self.set_start_child(widget1)
            self.set_end_child(widget2)

            self.set_resize_start_child(False)
            self.set_resize_end_child(True)

            self.set_shrink_start_child(True)
            self.set_shrink_end_child(False)

            self.animated_widget = widget1
            self.fixed_widget = widget2
        else:
            self.set_start_child(widget1)
            self.set_end_child(widget2)

            self.set_resize_start_child(True)
            self.set_resize_end_child(False)

            self.set_shrink_start_child(False)
            self.set_shrink_end_child(True)

            self.animated_widget = widget2
            self.fixed_widget = widget1

        self.is_initialized = False
        self.animation_id = None
        self.visible_before = False
        self.show_widget = False
        self.target_position = None
        self.center_on_first_show = False
        self.end_on_first_show = False
        self.start_on_first_show = False

        self.connect('notify::position', self.on_position_changed)

    def on_position_changed(self, widget, position):
        if self.animation_id != None: return
        if not self.show_widget: return

        if not self.is_initialized:
            self.is_initialized = True
            self.animate(False)

        self.set_target_position(self.get_position())

    def set_target_position(self, position):
        self.target_position = position

    def first_set_show_widget(self, show_widget):
        self.set_show_widget(show_widget)
        self.animated_widget.set_visible(show_widget)

    def set_show_widget(self, show_widget):
        self.show_widget = show_widget

    def set_center_on_first_show(self):
        self.center_on_first_show = True
        self.end_on_first_show = False
        self.start_on_first_show = False

    def set_end_on_first_show(self):
        self.center_on_first_show = False
        self.end_on_first_show = True
        self.start_on_first_show = False

    def set_start_on_first_show(self):
        self.center_on_first_show = False
        self.end_on_first_show = False
        self.start_on_first_show = True

    def set_shrink_animated_widget(self, shrink):
        if self.animate_first_widget:
            self.set_shrink_start_child(shrink)
        else:
            self.set_shrink_end_child(shrink)

    def animate(self, animate=False):
        if not self.is_initialized and self.get_paned_extent() <= 0: return
        if self.animation_id != None: self.remove_tick_callback(self.animation_id)

        frame_clock = self.get_frame_clock()
        duration = 200

        if not self.visible_before:
            self.visible_before = True

            if self.center_on_first_show:
                self.set_target_position(self.get_paned_extent() / 2)
            elif self.end_on_first_show:
                self.set_target_position(self.get_paned_extent() - self.original_size_request)
            elif self.start_on_first_show:
                self.set_target_position(self.original_size_request)

        if self.show_widget:
            end = self.target_position
        else:
            if self.animate_first_widget:
                end = 0
            else:
                end = self.get_paned_extent()

        if frame_clock != None and animate:
            if self.get_position() != end:
                if self.show_widget:
                    self.animated_widget.set_visible(True)

                start = self.get_position()
                if start == 0: start = self.get_paned_extent()
                start_time = frame_clock.get_frame_time()
                end_time = start_time + 1000 * duration
                self.set_shrink_animated_widget(True)
                self.fix_animated_widget_size()
                self.animation_id = self.add_tick_callback(self.set_position_on_tick, (self.show_widget, start_time, end_time, start, end))
        else:
            if self.show_widget:
                self.animated_widget.set_visible(self.show_widget)
                self.set_shrink_animated_widget(False)
            else:
                self.set_shrink_animated_widget(True)
                self.animated_widget.set_visible(self.show_widget)
            self.set_position(end)

    def set_position_on_tick(self, paned, frame_clock_cb, user_data):
        show_widget, start_time, end_time, start, end = user_data
        now = frame_clock_cb.get_frame_time()
        if now < end_time and self.get_position() != end:
            t = self.ease((now - start_time) / (end_time - start_time))
            self.set_position(int(start + t * (end - start)))
            return True
        else:
            self.set_position(end)
            if not show_widget:
                self.animated_widget.set_visible(False)
            else:
                self.reset_animated_widget_size_request()
                self.set_shrink_animated_widget(False)
            self.animation_id = None
            return False

    def ease(self, time):
        return (time - 1)**3 + 1;


class AnimatedHPaned(Gtk.Paned, AnimatedPaned):

    def __init__(self, widget1, widget2, animate_first_widget=True):
        Gtk.Paned.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        AnimatedPaned.__init__(self, widget1, widget2, animate_first_widget)

        self.original_size_request = self.animated_widget.get_size_request()[0]

    def reset_animated_widget_size_request(self):
        self.animated_widget.set_size_request(self.original_size_request, -1)

    def fix_animated_widget_size(self):
        if self.animate_first_widget:
            size = self.target_position
        else:
            size = self.get_paned_extent() - self.target_position - 3 # 3 is the width of the handle
        self.animated_widget.set_size_request(size, -1)

    def get_animated_widget_extent(self):
        return self.animated_widget.get_allocated_width()

    def get_paned_extent(self):
        return self.get_allocated_width()


class AnimatedVPaned(Gtk.Paned, AnimatedPaned):

    def __init__(self, widget1, widget2, animate_first_widget=True):
        Gtk.Paned.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        AnimatedPaned.__init__(self, widget1, widget2, animate_first_widget)

        self.original_size_request = self.animated_widget.get_size_request()[1]

    def reset_animated_widget_size_request(self):
        self.animated_widget.set_size_request(-1, self.original_size_request)

    def fix_animated_widget_size(self):
        if self.animate_first_widget:
            size = self.target_position
        else:
            size = self.get_paned_extent() - self.target_position
        self.animated_widget.set_size_request(-1, size)

    def get_animated_widget_extent(self):
        return self.animated_widget.get_allocated_height()

    def get_paned_extent(self):
        return self.get_allocated_height()


