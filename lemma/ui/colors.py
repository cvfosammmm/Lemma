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
gi.require_version('Adw', '1')
from gi.repository import Adw

import os.path

from lemma.services.color_manager import ColorManager
from lemma.services.message_bus import MessageBus
from lemma.services.paths import Paths
from lemma.services.settings import Settings
import lemma.services.timer as timer


class Colors(object):

    def __init__(self, main_window):
        self.main_window = main_window

        self.color_scheme = None
        self.style_manager = Adw.StyleManager.get_default()
        self.is_dark = self.style_manager.get_dark()

        self.update_color_scheme()

    def animate(self):
        self.update_color_scheme()

    def update_color_scheme(self):
        if Settings.get_value('separate_dark_color_scheme') and self.style_manager.get_dark():
            color_scheme = Settings.get_value('color_scheme_dark')
        else:
            color_scheme = Settings.get_value('color_scheme')

        if color_scheme != self.color_scheme:
            self.color_scheme = color_scheme
            self.update_colors()

    @timer.timer
    def update_colors(self):
        if self.color_scheme == 'default':
            path = os.path.join(Paths.get_resources_folder(), 'themes', 'default.css')
        else:
            path = self.color_scheme

        self.main_window.css_provider_colors.load_from_path(path)
        self.main_window.main_box.queue_draw()
        self.main_window.document_view.content.queue_draw()
        self.main_window.document_list.content.queue_draw()

        ColorManager.invalidate_cache()


