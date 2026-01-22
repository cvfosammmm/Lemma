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

from lemma.services.paths import Paths
from lemma.services.settings import Settings
from lemma.services.color_manager import ColorManager
from lemma.use_cases.use_cases import UseCases
from lemma.ui.helpers.cairo import rounded_rectangle


class PageColors(object):

    def __init__(self, settings, main_window):
        self.view = PageFontColorView()
        self.settings = settings
        self.main_window = main_window
        self.style_previews_single = dict()
        self.style_previews_light = dict()
        self.style_previews_dark = dict()

    def init(self):
        self.update_switchers()

        self.view.checkbox_darkmode.set_active(Settings.get_value('separate_dark_color_scheme'))
        self.view.checkbox_darkmode.connect('toggled', self.on_dm_checkbutton_toggled, 'separate_dark_color_scheme')

        stack_child = 'double' if Settings.get_value('separate_dark_color_scheme') else 'single'
        self.view.style_switcher_stack.set_visible_child_name(stack_child)

    def update_switchers(self):
        self.style_previews_single = dict()
        self.style_previews_light = dict()
        self.style_previews_dark = dict()

        dirname = os.path.join(Paths.get_resources_folder(), 'themes')

        self.add_theme_choice(os.path.join(dirname, 'default.css'), 0)
        self.add_chooser('default', 'default', 0, False)

        count = 1
        for name in [file[:-4] for file in os.listdir(dirname) if file != 'default.css']:
            self.add_theme_choice(os.path.join(dirname, name + '.css'), count)
            self.add_chooser(os.path.join(dirname, name + '.css'), name, count, True)
            count += 1

        for name in [file[:-4] for file in os.listdir(Paths.get_user_themes_folder())]:
            self.add_theme_choice(os.path.join(Paths.get_user_themes_folder(), name + '.css'), count)
            self.add_chooser(os.path.join(Paths.get_user_themes_folder(), name + '.css'), name, count, True)
            count += 1

        active_id = Settings.get_value('color_scheme')
        if active_id in self.style_previews_single: self.style_previews_single[active_id].checkbutton.set_active(True)
        else: self.style_previews_single['default'].checkbutton.set_active(True)

        active_id = Settings.get_value('color_scheme')
        if active_id in self.style_previews_light: self.style_previews_light[active_id].checkbutton.set_active(True)
        else: self.style_previews_light['default'].checkbutton.set_active(True)

        active_id = Settings.get_value('color_scheme_dark')
        if active_id in self.style_previews_dark: self.style_previews_dark[active_id].checkbutton.set_active(True)
        else: self.style_previews_dark['default'].checkbutton.set_active(True)

    def add_theme_choice(self, filename, count):
        with open(filename, 'r') as file:
            data = file.read().replace('@define-color ', '@define-color theme_' + str(count) + '_')
            provider = Gtk.CssProvider()
            provider.load_from_string(data)
            Gtk.StyleContext.add_provider_for_display(self.main_window.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def add_chooser(self, identifier, name, count, link_to_default = False):
        self.style_previews_single[identifier] = StylePreview(name, count)
        self.style_previews_single[identifier].wrapperbutton.connect('clicked', self.on_wrapperbutton_clicked, identifier)
        self.view.style_switcher_single.append(self.style_previews_single[identifier])
        if link_to_default:
            self.style_previews_single[identifier].checkbutton.set_group(self.style_previews_single['default'].checkbutton)

        self.style_previews_light[identifier] = StylePreview(name, count)
        self.style_previews_light[identifier].wrapperbutton.connect('clicked', self.on_wrapperbutton_clicked, identifier)
        self.view.style_switcher_light.append(self.style_previews_light[identifier])
        if link_to_default:
            self.style_previews_light[identifier].checkbutton.set_group(self.style_previews_light['default'].checkbutton)

        self.style_previews_dark[identifier] = StylePreview(name, count)
        self.style_previews_dark[identifier].wrapperbutton.connect('clicked', self.on_dark_wrapperbutton_clicked, identifier)
        self.view.style_switcher_dark.append(self.style_previews_dark[identifier])
        if link_to_default:
            self.style_previews_dark[identifier].checkbutton.set_group(self.style_previews_dark['default'].checkbutton)

    def on_dm_checkbutton_toggled(self, button, key):
        UseCases.settings_set_value(key, button.get_active())

        stack_child = 'double' if button.get_active() else 'single'
        self.view.style_switcher_stack.set_visible_child_name(stack_child)

    def on_wrapperbutton_clicked(self, button, name):
        self.set_light_theme(name)

    def on_dark_wrapperbutton_clicked(self, button, name):
        self.set_dark_theme(name)

    def set_light_theme(self, name):
        UseCases.settings_set_value('color_scheme', name)

        self.style_previews_light[name].checkbutton.set_active(True)
        self.style_previews_single[name].checkbutton.set_active(True)

    def set_dark_theme(self, name):
        UseCases.settings_set_value('color_scheme_dark', name)

        self.style_previews_dark[name].checkbutton.set_active(True)


class PageFontColorView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('settings-page')

        self.options_header = Gtk.Label.new(_('Options'))
        self.options_header.add_css_class('settings-header')
        self.options_header.set_xalign(0)
        self.options_header.set_margin_top(21)

        self.checkbox_darkmode = Gtk.CheckButton.new_with_label(_('Change color theme when dark mode is activated in the operating system'))
        self.checkbox_darkmode.add_css_class('single')
        self.checkbox_darkmode.set_margin_top(18)

        self.color_theme_header = Gtk.Label.new(_('Color Theme'))
        self.color_theme_header.add_css_class('settings-header')
        self.color_theme_header.set_xalign(0)
        self.color_theme_header.set_margin_top(36)

        self.style_switcher_single = StyleSwitcher()
        self.style_switcher_single.set_max_children_per_line(2)

        self.switcher_box_single = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.switcher_box_single.append(self.color_theme_header)
        self.switcher_box_single.append(self.style_switcher_single)

        self.light_theme_header = Gtk.Label.new(_('Light Theme'))
        self.light_theme_header.add_css_class('settings-header')
        self.light_theme_header.set_xalign(0)
        self.light_theme_header.set_margin_top(36)

        self.style_switcher_light = StyleSwitcher()
        self.style_switcher_light.set_max_children_per_line(1)

        self.light_theme_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.light_theme_box.append(self.light_theme_header)
        self.light_theme_box.append(self.style_switcher_light)

        self.dark_theme_header = Gtk.Label.new(_('Dark Theme'))
        self.dark_theme_header.add_css_class('settings-header')
        self.dark_theme_header.set_xalign(0)
        self.dark_theme_header.set_margin_top(36)

        self.style_switcher_dark = StyleSwitcher()
        self.style_switcher_dark.set_max_children_per_line(1)

        self.dark_theme_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.dark_theme_box.append(self.dark_theme_header)
        self.dark_theme_box.append(self.style_switcher_dark)

        self.switcher_box_double = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.switcher_box_double.append(self.light_theme_box)
        self.switcher_box_double.append(self.dark_theme_box)

        self.style_switcher_stack = Gtk.Stack()
        self.style_switcher_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.style_switcher_stack.set_interpolate_size(True)
        self.style_switcher_stack.set_vhomogeneous(False)
        self.style_switcher_stack.add_named(self.switcher_box_single, 'single')
        self.style_switcher_stack.add_named(self.switcher_box_double, 'double')

        self.custom_themes_header = Gtk.Label.new(_('Adding Custom Themes'))
        self.custom_themes_header.add_css_class('settings-header')
        self.custom_themes_header.set_xalign(0)
        self.custom_themes_header.set_margin_top(21)

        self.explainer = Gtk.Label()
        self.explainer.set_markup('If you want to make your own custom color themes, see the instructions on <a href="https://www.cvfosammmm.org/lemma/book/theming.html">https://www.cvfosammmm.org/lemma/book/theming.html</a>.')
        self.explainer.set_wrap(True)
        self.explainer.set_xalign(0)
        self.explainer.set_margin_top(18)
        self.explainer.set_margin_bottom(18)
        self.explainer.add_css_class('settings-info')

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.append(self.options_header)
        self.vbox.append(self.checkbox_darkmode)
        self.vbox.append(self.style_switcher_stack)
        self.vbox.append(self.custom_themes_header)
        self.vbox.append(self.explainer)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


class StyleSwitcher(Gtk.FlowBox):

    def __init__(self):
        Gtk.FlowBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.set_homogeneous(True)
        self.set_row_spacing(0)
        self.set_hexpand(True)
        self.get_style_context().add_class('theme_previews')


class StylePreview(Gtk.Box):

    def __init__(self, name, count):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.name = name
        self.count = count

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(-1, 84)
        self.drawing_area.set_draw_func(self.draw)

        self.wrapperbutton = Gtk.Button()
        self.wrapperbutton.add_css_class('color-preview-wrapper')
        self.wrapperbutton.set_child(self.drawing_area)
        self.checkbutton = Gtk.CheckButton.new_with_label(' ' + name)

        self.append(self.wrapperbutton)
        self.append(self.checkbutton)

    def draw(self, widget, ctx, width, height):
        color_prefix = 'theme_' + str(self.count) + '_'
        color_bg_1 = ColorManager.get_ui_color(color_prefix + 'sidebar_bg_1')
        color_bg_2 = ColorManager.get_ui_color(color_prefix + 'sidebar_active_bg')
        color_fg_1 = ColorManager.get_ui_color(color_prefix + 'sidebar_fg_1')

        Gdk.cairo_set_source_rgba(ctx, color_bg_1)
        rounded_rectangle(ctx, 0, 0, width, height, 4)
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


