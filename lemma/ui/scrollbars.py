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

from lemma.document_repo.document_repo import DocumentRepo
from lemma.application_state.application_state import ApplicationState
from lemma.services.layout_info import LayoutInfo
from lemma.use_cases.use_cases import UseCases


class Scrollbars():

    def __init__(self, main_window, model_state, application):
        self.main_window = main_window
        self.model_state = model_state
        self.application = application

        self.view = self.main_window.document_scrollbar_vertical

        self.pointer_x, self.pointer_y = (None, None)
        self.drag_start_x, self.drag_start_y = (None, None)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_hover)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_hover)
        self.view.add_controller(self.motion_controller)

        self.drag_controller = Gtk.GestureDrag()
        self.drag_controller.connect('drag-begin', self.on_drag_begin)
        self.drag_controller.connect('drag-update', self.on_drag_update)
        self.drag_controller.connect('drag-end', self.on_drag_end)
        self.view.add_controller(self.drag_controller)

    def animate(self):
        document = DocumentRepo.get_active_document()
        if document == None: return

        offset_y = document.get_current_scrolling_offsets()[1]
        total_height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

        self.view.set_attributes(total_height, offset_y, self.pointer_y, self.drag_start_y)

    def on_hover(self, controller, x=None, y=None):
        self.pointer_x, self.pointer_y = (x, y)

    def on_drag_begin(self, gesture, x, y, data=None):
        document = DocumentRepo.get_active_document()
        if document == None: return

        view_height = self.view.height
        document_height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

        if y < self.view.slider_offset or y > self.view.slider_offset + self.view.slider_height:
            y_in_range = max(self.view.slider_height / 2, min(view_height - self.view.slider_height / 2, y)) - self.view.slider_height / 2
            y_fraction = y_in_range / (view_height - self.view.slider_height)
            new_y = int(y_fraction * (document_height - view_height))
            UseCases.scroll_to_xy(0, new_y, animation_type=None)

            self.drag_start_x, self.drag_start_y = (x, y)
        else:
            self.drag_start_x, self.drag_start_y = (x, self.view.slider_offset + self.view.slider_height / 2)

    def on_drag_update(self, gesture, x, y, data=None):
        document = DocumentRepo.get_active_document()
        if document == None: return

        view_height = self.view.height
        document_height = document.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height')

        y += self.drag_start_y
        y_in_range = max(self.view.slider_height / 2, min(view_height - self.view.slider_height / 2, y)) - self.view.slider_height / 2
        y_fraction = y_in_range / (view_height - self.view.slider_height)
        new_y = int(y_fraction * (document_height - view_height))
        UseCases.scroll_to_xy(0, new_y, animation_type=None)

    def on_drag_end(self, gesture, x, y, data=None):
        self.drag_start_x, self.drag_start_y = (None, None)


