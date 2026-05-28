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
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

import os.path, json

from lemma.services.files import Files
from lemma.services.text_shaper import TextShaper
from lemma.services.text_renderer import TextRenderer
from lemma.services.settings import Settings
import lemma.services.timer as timer


class Fonts(object):

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application

        self.theme_name = None
        self.update_font_theme()

    def animate(self):
        self.update_font_theme()

    def update_font_theme(self):
        if self.theme_name == Settings.get_value('font_theme'): return

        self.theme_name = Settings.get_value('font_theme')
        font_path = os.path.join(Files.get_resources_folder(), 'fonts')

        with open(os.path.join(font_path, self.theme_name + '.json'), 'r') as file:
            for data in json.load(file):
                TextShaper.set_font(data['name'], os.path.join(font_path, data['path']), data['size'], data['ascend'], data['descend'], data['padding_top'], data['padding_bottom'])
                TextRenderer.set_font(data['name'], os.path.join(font_path, data['path']), data['size'], data['ascend'], data['descend'])

        self.application.document_view.presenter.clear_render_cache()

        self.main_window.main_box.queue_draw()
        self.main_window.document_view.content.queue_draw()
        self.main_window.document_list.content.queue_draw()


