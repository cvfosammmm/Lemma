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

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.layout_info import LayoutInfo
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
from lemma.use_cases.queries import Queries
from lemma.services.settings import Settings


class DocumentScrolling():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.view = main_window.document_view

        self.scrolling_multiplier = 2.5

        self.scrolling_controller = Gtk.EventControllerScroll()
        self.scrolling_controller.set_flags(Gtk.EventControllerScrollFlags.BOTH_AXES | Gtk.EventControllerScrollFlags.KINETIC)
        self.scrolling_controller.connect('scroll', self.on_scroll)
        self.scrolling_controller.connect('decelerate', self.on_decelerate)
        self.view.add_controller(self.scrolling_controller)

        self.view.scrollbar_vertical.observe('dragged', self.on_scrollbar_drag)

    def on_scroll(self, controller, dx, dy):
        if abs(dx) > 0 and abs(dy / dx) >= 1: dx = 0
        if abs(dy) > 0 and abs(dx / dy) >  1: dy = 0

        modifiers = Gtk.accelerator_get_default_mod_mask()
        view_width, view_height = ApplicationState.get_view_size()
        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()

        if controller.get_current_event_state() & modifiers == 0:
            document = WorkspaceRepo.get_workspace().get_active_document()
            document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
            height = document_layout.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_title_buttons_height()

            if controller.get_unit() == Gdk.ScrollUnit.WHEEL:
                dx *= view_width ** (2/3)
                dy *= view_height ** (2/3)
            else:
                dy *= self.scrolling_multiplier
                dx *= self.scrolling_multiplier
            x = min(0, max(0, scrolling_pos_x + dx))
            y = min(max(0, height - view_height), max(0, scrolling_pos_y + dy))

            UseCases.scroll_to_xy(x, y, animation_type=None)

    def on_decelerate(self, controller, vel_x, vel_y):
        if abs(vel_x) > 0 and abs(vel_y / vel_x) >= 1: vel_x = 0
        if abs(vel_y) > 0 and abs(vel_x / vel_y) >  1: vel_y = 0

        UseCases.decelerate(vel_x, vel_y)

    def on_scrollbar_drag(self, widget, new_y):
        UseCases.scroll_to_xy(0, new_y, animation_type=None)


