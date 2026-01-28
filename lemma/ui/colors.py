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

import os.path

from lemma.services.color_manager import ColorManager
from lemma.services.message_bus import MessageBus
from lemma.services.paths import Paths
from lemma.services.settings import Settings
import lemma.services.timer as timer


class Colors(object):

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application

        self.color_scheme = None
        self.dark_mode_active = False
        self.style_manager = Adw.StyleManager.get_default()
        self.css_provider_dark = Gtk.CssProvider()
        self.css_provider_dark.load_from_path(os.path.join(Paths.get_resources_folder(), 'themes', 'default-dark.css'))

        self.update_dark_mode()
        self.update_color_scheme()

    def animate(self):
        self.update_dark_mode()
        self.update_color_scheme()

    def update_color_scheme(self):
        if self.dark_mode_active:
            color_scheme = Settings.get_value('color_scheme_dark')
        else:
            color_scheme = Settings.get_value('color_scheme')

        if color_scheme != self.color_scheme:
            self.color_scheme = color_scheme
            self.update_colors()

    def update_dark_mode(self):
        dark_mode_active = Settings.get_value('separate_dark_color_scheme') and self.style_manager.get_dark()

        if dark_mode_active != self.dark_mode_active:
            self.dark_mode_active = dark_mode_active

            if dark_mode_active:
                Gtk.StyleContext.add_provider_for_display(self.main_window.get_display(), self.css_provider_dark, 600)
            else:
                Gtk.StyleContext.remove_provider_for_display(self.main_window.get_display(), self.css_provider_dark)

    @timer.timer
    def update_colors(self):
        if self.color_scheme == 'default':
            path = os.path.join(Paths.get_resources_folder(), 'themes', 'default.css')
        else:
            path = self.color_scheme

        self.main_window.css_provider_colors.load_from_path(path)
        ColorManager.invalidate_cache()
        self.application.document_view.presenter.clear_render_cache()

        self.main_window.main_box.queue_draw()
        self.main_window.document_view.content.queue_draw()
        self.main_window.document_list.content.queue_draw()


