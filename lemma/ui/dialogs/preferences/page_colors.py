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
from gi.repository import Gtk, Gdk

import os, os.path
import xml.etree.ElementTree as ET
from random import randrange

from lemma.infrastructure.service_locator import ServiceLocator
from lemma.infrastructure.color_manager import ColorManager
from lemma.ui.helpers.helpers import rounded_rectangle


class PageColors(object):

    def __init__(self, preferences, settings, main_window):
        self.view = PageFontColorView()
        self.preferences = preferences
        self.settings = settings
        self.main_window = main_window
        self.style_previews = dict()

    def init(self):
        self.update_switchers()

    def update_switchers(self):
        self.style_previews = dict()
        dirname = os.path.join(ServiceLocator.get_resources_path(), 'themes')

        self.add_theme_choice(os.path.join(dirname, 'default.css'), 'default', 0)

        count = 1
        for name in [file[:-4] for file in os.listdir(dirname) if file != 'default.css']:
            self.add_theme_choice(os.path.join(dirname, name + '.css'), name, count)
            count += 1

        for name in [file[:-4] for file in os.listdir(ServiceLocator.get_user_themes_folder())]:
            self.add_theme_choice(os.path.join(ServiceLocator.get_user_themes_folder(), name + '.css'), name, count)
            count += 1

        active_id = self.settings.get_value('preferences', 'color_scheme')
        if active_id in self.style_previews: self.style_previews[active_id].checkbutton.set_active(True)
        else: self.style_previews['default'].checkbutton.set_active(True)

    def add_theme_choice(self, filename, name, count):
        with open(filename, 'r') as file:
            data = file.read().replace('@define-color ', '@define-color theme_' + str(count) + '_')
            provider = Gtk.CssProvider()
            provider.load_from_string(data)
            Gtk.StyleContext.add_provider_for_display(self.main_window.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        if name == 'default':
            self.style_previews[name] = StylePreview(name, count)
            self.style_previews[name].checkbutton.connect('toggled', self.on_style_switcher_changed, name)
            self.view.style_switcher.append(self.style_previews[name])
        else:
            self.style_previews[filename] = StylePreview(name, count)
            self.style_previews[filename].checkbutton.set_group(self.style_previews['default'].checkbutton)
            self.style_previews[filename].checkbutton.connect('toggled', self.on_style_switcher_changed, filename)
            self.view.style_switcher.append(self.style_previews[filename])

    def on_style_switcher_changed(self, button, name):
        if button.get_active():
            self.settings.set_value('preferences', 'color_scheme', name)
            button.get_parent().add_css_class('selected')
        else:
            button.get_parent().remove_css_class('selected')


class PageFontColorView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preferences-page')

        self.explainer = Gtk.Label()
        self.explainer.set_markup('<b>Note:</b>  If you want to make your own custom color themes, see the instructions on <a href="https://www.cvfosammmm.org/lemma/book/theming/">https://www.cvfosammmm.org/lemma/book/theming/</a>.')
        self.explainer.set_wrap(True)
        self.explainer.set_halign(Gtk.Align.START)
        self.explainer.add_css_class('explainer')

        self.style_switcher = StyleSwitcher()

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.append(self.explainer)
        self.vbox.append(self.style_switcher)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


class StyleSwitcher(Gtk.FlowBox):

    def __init__(self):
        Gtk.FlowBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_homogeneous(True)
        self.set_max_children_per_line(2)
        self.set_row_spacing(0)
        self.set_hexpand(True)
        self.get_style_context().add_class('theme_previews')


class StylePreview(Gtk.Box):

    def __init__(self, name, count):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.name = name
        self.count = count

        self.wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.wrapper.add_css_class('color-preview-wrapper')
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(-1, 84)
        self.drawing_area.set_draw_func(self.draw)
        self.checkbutton = Gtk.CheckButton.new_with_label(' ' + name)

        self.wrapper.append(self.drawing_area)
        self.append(self.wrapper)
        self.append(self.checkbutton)

    def draw(self, widget, ctx, width, height):
        color_prefix = 'theme_' + str(self.count) + '_'
        color_bg_1 = ColorManager.get_ui_color(color_prefix + 'sidebar_bg_1')
        color_bg_2 = ColorManager.get_ui_color(color_prefix + 'sidebar_active_bg')
        color_fg_1 = ColorManager.get_ui_color(color_prefix + 'sidebar_fg_1')

        Gdk.cairo_set_source_rgba(ctx, color_bg_1)
        rounded_rectangle(ctx, 0, 0, width, height, 2)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, color_bg_2)
        ctx.rectangle(0, height / 3, width, height / 3)
        ctx.fill()

        Gdk.cairo_set_source_rgba(ctx, color_fg_1)
        ctx.rectangle(5, 0 * height / 3 + 8, randrange(2, 5) * width / 18, 2)
        ctx.rectangle(5, 0 * height / 3 + 18, randrange(5, 15) * width / 18, 2)
        ctx.rectangle(5, 1 * height / 3 + 8, randrange(2, 5) * width / 18, 2)
        ctx.rectangle(5, 1 * height / 3 + 18, randrange(5, 15) * width / 18, 2)
        ctx.rectangle(5, 2 * height / 3 + 8, randrange(2, 5) * width / 18, 2)
        ctx.rectangle(5, 2 * height / 3 + 18, randrange(5, 15) * width / 18, 2)
        ctx.fill()


