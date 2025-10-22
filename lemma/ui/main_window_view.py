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

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GObject, Adw

from lemma.services.paths import Paths
from lemma.ui.welcome_view import WelcomeView
from lemma.ui.headerbar_view import HeaderBar
from lemma.ui.history_view import HistoryView
from lemma.ui.document_list_view import DocumentListView
from lemma.ui.backlinks_view import BacklinksView
from lemma.ui.toolbars_view import ToolBarsView
from lemma.ui.tools_sidebar_view import ToolsSidebar
from lemma.ui.document_view_view import DocumentView
from lemma.ui.navigation_sidebar_view import NavigationSidebar
from lemma.ui.document_draft_view import DocumentDraftView
from lemma.ui.animated_paned import AnimatedHPaned


class MainWindow(Adw.ApplicationWindow):

    def __init__(self, app):
        Adw.ApplicationWindow.__init__(self, application=app)

        self.app = app
        self.set_size_request(550, 550)

        self.popoverlay = Gtk.Overlay()
        self.set_content(self.popoverlay)

    def add_widgets(self):
        self.headerbar = HeaderBar()
        self.history_view = HistoryView()
        self.headerbar.hb_right.history_overlay.set_child(self.history_view)
        self.toolbar = ToolBarsView()

        self.document_list = DocumentListView()
        self.backlinks = BacklinksView()
        self.navigation_sidebar = NavigationSidebar(self.document_list, self.backlinks)

        self.content_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.content_paned.add_css_class('content')
        self.content_paned.set_wide_handle(True)
        self.headerbar.bind_property('position', self.content_paned, 'position', GObject.BindingFlags.BIDIRECTIONAL)

        self.welcome = WelcomeView()
        self.document_view = DocumentView()
        self.tools_sidebar = ToolsSidebar()
        self.draft_view = DocumentDraftView()

        self.content_stack = Gtk.Stack()
        self.content_stack.add_css_class('content')
        self.content_stack.add_named(self.welcome, 'welcome')
        self.content_stack.add_named(self.draft_view, 'draft_view')
        self.content_stack.add_named(self.document_view, 'document_view')

        self.document_view_paned = AnimatedHPaned(self.content_stack, self.tools_sidebar, False)
        self.document_view_paned.add_css_class('document-view')
        self.document_view_paned.set_wide_handle(True)

        self.content_with_toolbar = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content_with_toolbar.append(self.document_view_paned)
        self.content_with_toolbar.append(self.toolbar)

        self.content_paned.set_start_child(self.navigation_sidebar)
        self.content_paned.set_resize_start_child(False)
        self.content_paned.set_shrink_start_child(False)

        self.content_paned.set_end_child(self.content_with_toolbar)
        self.content_paned.set_resize_end_child(True)
        self.content_paned.set_shrink_end_child(False)

        self.main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.main_box.append(self.headerbar)
        self.main_box.append(self.content_paned)
        self.inbetween = Gtk.DrawingArea()
        self.popoverlay.add_overlay(self.inbetween)
        self.popoverlay.set_child(self.main_box)

        resources_folder = Paths.get_resources_folder()

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_path(os.path.join(resources_folder, 'style.css'))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.css_provider_colors_default = Gtk.CssProvider()
        self.css_provider_colors_default.load_from_path(os.path.join(resources_folder, 'themes', 'default.css'))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_colors_default, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.css_provider_colors = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_colors, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        resources_folder = Paths.get_resources_folder()
        icon_theme = Gtk.IconTheme.get_for_display(self.get_display())
        icon_theme.add_search_path(os.path.join(resources_folder, 'icons'))


