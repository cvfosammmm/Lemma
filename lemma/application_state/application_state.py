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

    defaults = dict()
    data = dict()

    def init():
        ApplicationState.defaults = dict()

        ApplicationState.defaults['mode'] = 'documents'
        ApplicationState.defaults['active_popover'] = None
        ApplicationState.defaults['popover_position'] = (0, 0)
        ApplicationState.defaults['popover_orientation'] = 'bottom'

        ApplicationState.defaults['document_view_width'] = 0
        ApplicationState.defaults['document_view_height'] = 0
        ApplicationState.defaults['title_width'] = 500
        ApplicationState.defaults['title_height'] = 54
        ApplicationState.defaults['subtitle_height'] = 51
        ApplicationState.defaults['document_padding_left'] = 48
        ApplicationState.defaults['document_padding_bottom'] = 120
        ApplicationState.defaults['document_padding_top'] = 48
        ApplicationState.defaults['document_view_hide_cursor_on_unfocus'] = True

        ApplicationState.defaults['tags_at_cursor'] = set()

        ApplicationState.data = ApplicationState.defaults

    def get_value(item):
        try: value = ApplicationState.data[item]
        except KeyError:
            value = ApplicationState.defaults[item]
            ApplicationState.set_value(item, value)
        return value

    def set_value(item, value):
        ApplicationState.data[item] = value


