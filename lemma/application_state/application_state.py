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


class ApplicationState():

    frame_time = 0

    implicit_x_position = 0
    preedit_string = ''
    tags_at_cursor = set()

    view_width = 0
    view_height = 0
    title_buttons_height = 0
    ctrl_pressed = False
    is_dark_mode = False

    prev_scrolling_target_x = 0
    prev_scrolling_target_y = 0
    scrolling_target_x = 0
    scrolling_target_y = 0
    last_scroll_scheduled = 0
    last_scroll_animation_type = None
    scrolling_positions = dict()
    dialog_display_schedule = None
    popover = None

    def set_frame_time(time):
        ApplicationState.frame_time = time

    def get_frame_time():
        return ApplicationState.frame_time

    def set_preedit(preedit_string):
        ApplicationState.preedit_string = preedit_string

    def get_preedit():
        return ApplicationState.preedit_string

    def set_implicit_x_position(value):
        ApplicationState.implicit_x_position = value

    def get_implicit_x_position():
        return ApplicationState.implicit_x_position

    def toggle_tag_at_cursor(tagname):
        ApplicationState.tags_at_cursor ^= {tagname}

    def set_tags_at_cursor(tags_at_cursor):
        ApplicationState.tags_at_cursor = tags_at_cursor

    def get_tags_at_cursor():
        return ApplicationState.tags_at_cursor

    def set_view_size(width, height):
        ApplicationState.view_width = width
        ApplicationState.view_height = height

    def get_view_size():
        return (ApplicationState.view_width, ApplicationState.view_height)

    def set_title_buttons_height(height):
        ApplicationState.title_buttons_height = height

    def get_title_buttons_height():
        return ApplicationState.title_buttons_height

    def set_dark_mode(is_dark):
        ApplicationState.is_dark_mode = is_dark

    def get_dark_mode():
        return ApplicationState.is_dark_mode

    def set_ctrl_pressed(is_pressed):
        ApplicationState.ctrl_pressed = is_pressed

    def get_ctrl_pressed():
        return ApplicationState.ctrl_pressed

    def set_scrolling_target(document_id, x, y, animation_type=None):
        ApplicationState.prev_scrolling_target_x = ApplicationState.scrolling_target_x
        ApplicationState.prev_scrolling_target_y = ApplicationState.scrolling_target_y

        ApplicationState.scrolling_target_x = x
        ApplicationState.scrolling_target_y = y

        ApplicationState.scrolling_positions[document_id] = (x, y)

        ApplicationState.last_scroll_scheduled = ApplicationState.frame_time
        ApplicationState.last_scroll_animation_type = animation_type

    def get_scrolling_position(document_id):
        if document_id in ApplicationState.scrolling_positions:
            return ApplicationState.scrolling_positions[document_id]
        return None

    def set_popover(name, x=None, y=None, orientation=None):
        if name != None:
            ApplicationState.popover = (name, x, y, orientation)
        else:
            ApplicationState.popover = None

    def get_popover():
        return ApplicationState.popover

    def schedule_dialog_display(name, argument):
        ApplicationState.dialog_display_schedule = (name, argument)

    def get_dialog_display_schedule():
        schedule = ApplicationState.dialog_display_schedule
        ApplicationState.dialog_display_schedule = None

        return schedule


