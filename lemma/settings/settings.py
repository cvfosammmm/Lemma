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
        Settings.defaults['window_state'] = dict()
        Settings.defaults['window_state']['width'] = 1020
        Settings.defaults['window_state']['height'] = 550
        Settings.defaults['window_state']['is_maximized'] = False
        Settings.defaults['window_state']['sidebar_position'] = 250
        Settings.defaults['window_state']['show_tools_sidebar'] = False
        Settings.defaults['window_state']['tools_sidebar_position'] = -1
        Settings.defaults['window_state']['show_backlinks'] = False
        Settings.defaults['window_state']['navbar_paned_position'] = -1
        Settings.defaults['window_state']['mode'] = 'documents'

        Settings.defaults['app_state'] = dict()
        Settings.defaults['app_state']['last_export_folder'] = None
        Settings.defaults['app_state']['last_bulk_export_folder'] = None
        Settings.defaults['app_state']['last_import_folder'] = None

        Settings.defaults['preferences'] = dict()
        Settings.defaults['preferences']['color_scheme'] = 'default'
        Settings.defaults['preferences']['update_backlinks'] = True

        Settings.data = Settings.defaults

    def get_value(section, item):
        try: value = Settings.data[section][item]
        except KeyError:
            value = Settings.defaults[section][item]
            Settings.set_value(section, item, value)
        return value

    def set_value(section, item, value):
        try: section_dict = Settings.data[section]
        except KeyError:
            section_dict = dict()
            Settings.data[section] = section_dict
        section_dict[item] = value


