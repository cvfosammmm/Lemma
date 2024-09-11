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

from lemma.infrastructure.service_locator import ServiceLocator


class Colors(object):

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.main_window = main_window

        self.update()
        ServiceLocator.get_settings().connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter
        if item == 'color_scheme':
            self.update()

    def update(self):
        color_scheme = ServiceLocator.get_settings().get_value('preferences', 'color_scheme')

        if color_scheme == 'default':
            path = os.path.join(ServiceLocator.get_resources_path(), 'themes', 'default.css')
        else:
            path = ServiceLocator.get_settings().get_value('preferences', 'color_scheme')

        self.main_window.css_provider_colors.load_from_path(path)
        self.main_window.main_box.queue_draw()
        self.main_window.document_view.content.queue_draw()
        self.main_window.document_list.content.queue_draw()


