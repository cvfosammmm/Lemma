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


class Settings():

    defaults = dict()
    data = dict()

    def init():
        Settings.defaults = dict()
        Settings.defaults['color_scheme'] = 'default'
        Settings.defaults['update_backlinks'] = True

        Settings.defaults['width'] = 1020
        Settings.defaults['height'] = 550
        Settings.defaults['is_maximized'] = False
        Settings.defaults['sidebar_position'] = 250
        Settings.defaults['show_tools_sidebar'] = False
        Settings.defaults['tools_sidebar_position'] = -1
        Settings.defaults['show_backlinks'] = False
        Settings.defaults['navbar_paned_position'] = -1

        Settings.defaults['last_export_folder'] = None
        Settings.defaults['last_bulk_export_folder'] = None
        Settings.defaults['last_import_folder'] = None

        Settings.data = Settings.defaults

    def get_value(item):
        try: value = Settings.data[item]
        except KeyError:
            value = Settings.defaults[item]
            Settings.set_value(item, value)
        return value

    def set_value(item, value):
        Settings.data[item] = value


