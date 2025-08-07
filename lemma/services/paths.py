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

import os.path
from xdg.BaseDirectory import xdg_config_home


class Paths():

    resources_folder = None

    def get_config_folder():
        return os.path.join(xdg_config_home, 'lemma')

    def get_notes_folder():
        return os.path.expanduser(Paths.get_config_folder() + '/notes')

    def get_user_themes_folder():
        return os.path.expanduser(Paths.get_config_folder() + '/themes')

    def init_resources_folder(resources_folder):
        Paths.resources_folder = resources_folder

    def get_resources_folder():
        return Paths.resources_folder


