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


class ColorManager(object):

    main_window = None
    rgba_cache = dict()
    string_cache = dict()

    def init(main_window):
        ColorManager.main_window = main_window

    def invalidate_cache():
        ColorManager.rgba_cache = dict()
        ColorManager.string_cache = dict()

    def get_ui_color(name):
        if not name in ColorManager.rgba_cache:
            ColorManager.rgba_cache[name] = ColorManager.main_window.get_style_context().lookup_color(name)[1]
        return ColorManager.rgba_cache[name]

    def get_ui_color_string(name):
        if not name in ColorManager.string_cache:
            ColorManager.string_cache[name] = ColorManager.main_window.get_style_context().lookup_color(name)[1].to_string()
        return ColorManager.string_cache[name]


