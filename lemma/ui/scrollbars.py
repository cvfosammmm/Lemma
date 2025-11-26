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

import time

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.application_state.application_state import ApplicationState
from lemma.services.layout_info import LayoutInfo
from lemma.services.color_manager import ColorManager
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class Scrollbars():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.view = self.main_window.document_view.scrollbar_vertical

        self.pointer_x, self.pointer_y = (None, None)
        self.drag_start_x, self.drag_start_y = (None, None)

        self.view_width = 20
        self.view_height = 0
        self.slider_offset = 0
        self.slider_height = 1
        self.pointer_pos = None
        self.pointer_entry_time = None
        self.drag_in_progress = False

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_hover)
        self.view.add_controller(self.motion_controller)

        self.drag_controller = Gtk.GestureDrag()
        self.drag_controller.connect('drag-begin', self.on_drag_begin)
        self.drag_controller.connect('drag-update', self.on_drag_update)
        self.drag_controller.connect('drag-end', self.on_drag_end)
        self.view.add_controller(self.drag_controller)

        self.view.set_draw_func(self.draw)

    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        scrolling_offset = document.get_current_scrolling_offsets()[1]
        total_height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')
        pointer_pos = self.pointer_y
        drag_pos = self.drag_start_y
        height = self.view.get_allocated_height()
        slider_height = max(60, min(height, height * height / total_height))
        slider_pos_fraction = scrolling_offset / (total_height - height)
        slider_offset = slider_pos_fraction * (height - slider_height)
        drag_in_progress = (drag_pos != None)

        if self.slider_offset != slider_offset or self.slider_height != slider_height or self.pointer_pos != pointer_pos or self.drag_in_progress != drag_in_progress or self.view_height != height:
            self.slider_offset = slider_offset
            self.slider_height = slider_height
            self.pointer_pos = pointer_pos
            self.drag_in_progress = drag_in_progress
            self.view_height = height

            self.view.set_can_target(slider_height < height)
            self.view.queue_draw()

    def on_enter(self, controller, x=None, y=None):
        self.pointer_entry_time = time.time()

    def on_hover(self, controller, x=None, y=None):
        self.pointer_x, self.pointer_y = (x, y)

    def on_drag_begin(self, gesture, x, y, data=None):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        view_height = self.view_height
        document_height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

        if y < self.slider_offset or y > self.slider_offset + self.slider_height:
            y_in_range = max(self.slider_height / 2, min(view_height - self.slider_height / 2, y)) - self.slider_height / 2
            y_fraction = y_in_range / (view_height - self.slider_height)
            new_y = int(y_fraction * (document_height - view_height))
            UseCases.scroll_to_xy(0, new_y, animation_type=None)

            self.drag_start_x, self.drag_start_y = (x, y)
        else:
            self.drag_start_x, self.drag_start_y = (x, self.slider_offset + self.slider_height / 2)

    def on_drag_update(self, gesture, x, y, data=None):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        view_height = self.view_height
        document_height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

        y += self.drag_start_y
        y_in_range = max(self.slider_height / 2, min(view_height - self.slider_height / 2, y)) - self.slider_height / 2
        y_fraction = y_in_range / (view_height - self.slider_height)
        new_y = int(y_fraction * (document_height - view_height))
        UseCases.scroll_to_xy(0, new_y, animation_type=None)

    def on_drag_end(self, gesture, x, y, data=None):
        self.drag_start_x, self.drag_start_y = (None, None)

    @timer.timer
    def draw(self, snapshot):
        expand_width = self.pointer_pos != None and time.time() - self.pointer_entry_time > 0.1

        visible_width = 8 if expand_width else 3

        if self.slider_height >= self.view_height: return

        if expand_width:
            rect = Graphene.Rect().init(self.view_width - 6 - visible_width, 6, visible_width, self.view_height - 12)
            rounded_rect = Gsk.RoundedRect()
            rounded_rect.init_from_rect(rect, 20)
            snapshot.push_rounded_clip(rounded_rect)
            snapshot.append_color(ColorManager.get_ui_color('scrollbar_bg'), rect)
            snapshot.pop()

        pointer_hovers_slider = self.pointer_pos != None and self.pointer_pos > self.slider_offset and self.pointer_pos < self.slider_offset + self.slider_height

        if expand_width:
            if self.drag_in_progress:
                slider_color = ColorManager.get_ui_color('scrollbar_active')
            elif pointer_hovers_slider:
                slider_color = ColorManager.get_ui_color('scrollbar_hover')
            else:
                slider_color = ColorManager.get_ui_color('scrollbar_default')
        else:
            slider_color = ColorManager.get_ui_color('scrollbar_thin')

        rect = Graphene.Rect().init(self.view_width - 6 - visible_width, self.slider_offset + 6, visible_width, self.slider_height - 12)
        rounded_rect = Gsk.RoundedRect()
        rounded_rect.init_from_rect(rect, 20)
        snapshot.push_rounded_clip(rounded_rect)
        snapshot.append_color(slider_color, rect)
        snapshot.pop()


