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
from lemma.application_state.application_state import ApplicationState


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
        self.prev_scroll_x = 0
        self.prev_scroll_y = 0
        self.current_scroll_x = 0
        self.current_scroll_y = 0
        self.last_scroll_scheduled = 0
        self.last_scroll_animation_type = None

        self.__pointer_func = lambda snapshot: None
        self.__setup_signals()

    def set_content_size(self, width, height):
        self.content_width = width
        self.content_height = height

        self.__update_scrollbars()
        self.content.queue_draw()

    def scroll_to(self, x, y):
        self.__set_scrolling_target(x, y)

        self.__update_scrollbars()
        self.content.queue_draw()

    def get_current_scrolling_offsets(self):
        return self.current_scroll_x, self.current_scroll_y

    def set_draw_func(self, draw_func):
        self.content.draw_func = draw_func

    def set_pointer_func(self, pointer_func):
        self.__pointer_func = pointer_func

    def animate(self):
        prev_x, prev_y = self.get_current_scrolling_offsets()
        self.__update_current_scrolling_offsets()

        if prev_x != self.current_scroll_x or prev_y != self.current_scroll_y:
            self.queue_draw()

    def queue_draw(self):
        self.__update_scrollbars()
        self.content.queue_draw()

    def __setup_signals(self):
        self.content.allocate_func = self.__size_allocate

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.__on_scroll)
        self.scrolling_controller.connect('decelerate', self.__on_decelerate)
        self.add_controller(self.scrolling_controller)

        self.scrollbar_vertical.observe('dragged', self.__on_vertical_scrollbar_drag)
        self.scrollbar_horizontal.observe('dragged', self.__on_horizontal_scrollbar_drag)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.__on_enter)
        self.motion_controller.connect('motion', self.__on_hover)
        self.motion_controller.connect('leave', self.__on_leave)
        self.add_controller(self.motion_controller)

    def __size_allocate(self, width, height, baseline):
        self.view_width = width
        self.view_height = height

    def __on_enter(self, controller, x, y):
        self.pointer_x = x
        self.pointer_y = y
        self.__pointer_func()

        self.queue_draw()

    def __on_hover(self, controller, x, y):
        self.pointer_x = x
        self.pointer_y = y
        self.__pointer_func()

        self.queue_draw()

    def __on_leave(self, controller):
        self.pointer_x = None
        self.pointer_y = None
        self.__pointer_func()

        self.queue_draw()

    def __on_scroll(self, controller, dx, dy):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if controller.get_current_event_state() & modifiers == 0:
            dy *= self.__scrolling_multiplier
            dx *= self.__scrolling_multiplier

            scroll_x, scroll_y = self.get_current_scrolling_offsets()
            scroll_x += dx
            scroll_y += dy
            self.__set_scrolling_target(scroll_x, scroll_y)

            self.queue_draw()

        if controller.get_current_event_state() & modifiers == Gdk.ModifierType.CONTROL_MASK:
            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                zoom_amount = dy * 0.1
            else:
                zoom_amount = (dy + dx) * 0.005
            self.add_change_code('zoom', zoom_amount)

    def __on_decelerate(self, controller, vel_x, vel_y):
        scroll_x, scroll_y = self.get_current_scrolling_offsets()
        x = scroll_x + 15.13 / 16 * vel_x / self.__scrolling_multiplier
        y = scroll_y + 15.13 / 16 * vel_y / self.__scrolling_multiplier

        self.__set_scrolling_target(x, y, 'decelerate')

    def __on_horizontal_scrollbar_drag(self, widget, new_x):
        self.__set_scrolling_target(new_x, self.scroll_y)

        self.queue_draw()

    def __on_vertical_scrollbar_drag(self, widget, new_y):
        scroll_x, scroll_y = self.get_current_scrolling_offsets()
        self.__set_scrolling_target(scroll_x, new_y)

        self.queue_draw()

    def __set_scrolling_target(self, x, y, animation_type=None):
        if self.content_width < self.view_width:
            scroll_x = (self.content_width - self.view_width) / 2
        else:
            scroll_x = x

        if self.content_height < self.view_height:
            scroll_y = (self.content_height - self.view_height) / 2
        else:
            scroll_y = y

        self.prev_scroll_x = self.scroll_x
        self.prev_scroll_y = self.scroll_y

        self.scroll_x = scroll_x
        self.scroll_y = scroll_y

        self.last_scroll_scheduled = ApplicationState.get_frame_time()
        self.last_scroll_animation_type = animation_type

        if animation_type == None:
            self.__update_current_scrolling_offsets()

    def __update_current_scrolling_offsets(self):
        # these factors correspond to a spring animation with damping factor of 1, mass of 0.2 and stiffness of 350.
        # values are measured every 16 milliseconds.
        animation_factors_default = [0.14521632886418778, 0.38680949651114804, 0.5961508878602289, 0.7471932740676479, 0.8469876969721808, 0.9095846909702064, 0.9475247122520112, 0.9699664865615893, 0.9830014314472356, 0.9904664008194531, 0.9946935799717825, 0.9970653570501354, 0.9983859489194434, 0.9991164990228094, 0.9995184028082745, 1]

        animation_factors_decelerate = [0.0, 0.06199636747598371, 0.12014927262467011, 0.17469699073964112, 0.2258630252471631, 0.27385702348751123, 0.31887563572246785, 0.36110332088868463, 0.40071310239839775, 0.4378672770843073, 0.4727180801934477, 0.5054083091547894, 0.5360719086763932, 0.5648345195694895, 0.591813993548231, 0.6171208761144554, 0.6408588595060257, 0.6631252075646573, 0.6840111542640804, 0.7036022775314649, 0.7219788498938017, 0.7392161673859745, 0.7553848580681896, 0.7705511714168795, 0.7847772497748297, 0.7981213829727649, 0.8106382471656801, 0.8223791288625243, 0.8333921350671701, 0.8437223903917062, 0.8534122219496949, 0.8625013327869832, 0.871026964560675, 0.8790240501328287, 0.8865253567041134, 0.8935616200739007, 0.9001616705769069, 0.9063525512123981, 0.91215962844998, 0.917606696165988, 0.9227160731363435, 0.9275086944853453, 0.9320041974650973, 0.9362210019170423, 0.9401763857452885, 0.9438865557109685, 0.947366713837705, 0.9506311197002733, 0.9536931488516794, 0.9565653476280548, 0.9592594845559228, 0.9617865985724751, 0.9641570442564326, 0.9663805342548213, 0.9684661790795032, 0.9704225244365203, 0.9722575862412101, 0.9739788834625586, 0.9755934689313691, 0.9771079582384816, 0.9785285568414455, 0.979861085490717, 0.9811110040795602, 0.9822834340153744, 0.9833831792041116, 0.9844147457337654, 0.9853823603375849, 0.9862899877126596, 0.9871413467648417, 0.9879399258465626, 0.988688997049985, 0.9893916296140478, 0.9900507025003449, 0.9906689161893605, 0.9912488037453996, 0.9917927411955463, 0.9923029572651805, 0.9927815425099413, 0.9932304578815544, 0.9936515427626212, 0.9940465225032924, 0.994417015490705, 0.9947645397801501, 0.9950905193151411, 0.9953962897618709, 0.9956831039819594, 0.9959521371659206, 0.9962044916483798, 0.9964412014247709, 0.9966632363880219, 0.9968715063025881, 0.9970668645321131, 0.9972501115359957, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        time_since_last_scroll = ApplicationState.get_frame_time() - self.last_scroll_scheduled

        if self.last_scroll_animation_type == 'decelerate' and time_since_last_scroll < 1800000:
            proximity = animation_factors_decelerate[int(time_since_last_scroll * 0.000064)]
            x = self.prev_scroll_x + proximity * (self.scroll_x - self.prev_scroll_x)
            y = self.prev_scroll_y + proximity * (self.scroll_y - self.prev_scroll_y)

        else:
            x = self.scroll_x
            y = self.scroll_y

        x = min(self.content_width - self.view_width, max(0, x))
        y = min(self.content_height - self.view_height, max(0, y))

        self.current_scroll_x = x
        self.current_scroll_y = y

    def __update_scrollbars(self):
        scroll_x, scroll_y = self.get_current_scrolling_offsets()

        self.scrollbar_horizontal.set_content_width(self.content_width)
        self.scrollbar_horizontal.set_scrolling_offset(scroll_x)
        self.scrollbar_horizontal.ping()
        self.scrollbar_vertical.set_content_height(self.content_height)
        self.scrollbar_vertical.set_scrolling_offset(scroll_y)
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


