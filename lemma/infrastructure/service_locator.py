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

import re
import os.path
import time
import datetime
from xdg.BaseDirectory import xdg_config_home

import lemma.infrastructure.settings as settingscontroller


class ServiceLocator():

    settings = None
    workspace = None
    lemma_version = None
    resources_path = None
    app_icons_path = None
    regexes = dict()

    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings(ServiceLocator.get_config_folder())
        return ServiceLocator.settings

    def set_workspace(workspace):
        ServiceLocator.workspace = workspace

    def get_workspace():
        return ServiceLocator.workspace

    def get_regex_matcher(pattern):
        try:
            regex = ServiceLocator.regexes[pattern]
        except KeyError:
            regex = re.compile(pattern)
            ServiceLocator.regexes[pattern] = regex
        return regex

    def get_config_folder():
        return os.path.join(xdg_config_home, 'lemma')

    def get_notes_folder():
        return os.path.expanduser(ServiceLocator.get_config_folder() + '/notes')

    def get_user_themes_folder():
        return os.path.expanduser(ServiceLocator.get_config_folder() + '/themes')

    def init_lemma_version(lemma_version):
        ServiceLocator.lemma_version = lemma_version

    def get_lemma_version():
        return ServiceLocator.lemma_version

    def init_resources_path(resources_path):
        ServiceLocator.resources_path = resources_path

    def get_resources_path():
        return ServiceLocator.resources_path

    def get_datetimes_today_week_year():
        date_today = datetime.date.today()
        datetime_today = datetime.datetime.combine(date_today, datetime.time(0, 0))
        date_this_week = datetime.date.fromtimestamp(time.time() - date_today.weekday() * 86400)
        datetime_this_week = datetime.datetime.combine(date_this_week, datetime.time(0, 0))
        date_this_year = datetime.date(date_today.year, 1, 1)
        datetime_this_year = datetime.datetime.combine(date_this_year, datetime.time(0, 0))
        return (datetime_today, datetime_this_week, datetime_this_year)


