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
from xdg.BaseDirectory import xdg_config_home


class ServiceLocator():

    lemma_version = None
    resources_path = None
    app_icons_path = None
    regexes = dict()

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


