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

from lemma.services.files import Files
from lemma.ui.views.welcome_view import WelcomeView
from lemma.ui.views.headerbar_view import HeaderBar
from lemma.ui.views.history_view import HistoryView
from lemma.ui.views.document_list_view import DocumentListView
from lemma.ui.views.backlinks_view import BacklinksView
from lemma.ui.views.graph_panel_view import GraphPanelView
from lemma.ui.views.toolbars_view import ToolbarsView
from lemma.ui.views.document_view_view import DocumentView
from lemma.ui.views.document_draft_view import DocumentDraftView
from lemma.ui.views.animated_paned import AnimatedHPaned
from lemma.ui.views.animated_paned import AnimatedVPaned


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
        self.toolbar = ToolbarsView()

        self.document_list = DocumentListView()

        self.backlinks = BacklinksView()
        self.graph_panel = GraphPanelView()

        self.navigation_sidebar_stack = Gtk.Stack()
        self.navigation_sidebar_stack.add_named(self.backlinks, 'backlinks')
        self.navigation_sidebar_stack.add_named(self.graph_panel, 'graph_panel')

        self.navigation_sidebar_paned = AnimatedVPaned(self.document_list, self.navigation_sidebar_stack, False)
        self.navigation_sidebar_paned.set_vexpand(True)
        self.navigation_sidebar_paned.set_wide_handle(False)

        self.backlinks_toggle = Gtk.Button()
        self.backlinks_toggle.set_tooltip_text(_('Backlinks'))
        self.backlinks_toggle.set_icon_name('backlinks-symbolic')
        self.backlinks_toggle.set_can_focus(False)
        self.backlinks_toggle.add_css_class('flat')

        self.graph_panel_toggle = Gtk.Button()
        self.graph_panel_toggle.set_tooltip_text(_('Graph View'))
        self.graph_panel_toggle.set_icon_name('graph-view-symbolic')
        self.graph_panel_toggle.set_can_focus(False)
        self.graph_panel_toggle.add_css_class('flat')

        self.navigation_sidebar_toolbar = Gtk.ActionBar()
        self.navigation_sidebar_toolbar.add_css_class('nav-toolbar')
        self.navigation_sidebar_toolbar.pack_start(self.backlinks_toggle)
        self.navigation_sidebar_toolbar.pack_start(self.graph_panel_toggle)

        self.navigation_sidebar = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.navigation_sidebar.add_css_class('navbar')
        self.navigation_sidebar.append(self.navigation_sidebar_paned)
        self.navigation_sidebar.append(self.navigation_sidebar_toolbar)

        self.content_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.content_paned.add_css_class('content')
        self.content_paned.set_wide_handle(True)
        self.headerbar.bind_property('position', self.content_paned, 'position', GObject.BindingFlags.BIDIRECTIONAL)

        self.welcome = WelcomeView()
        self.document_view = DocumentView()
        self.draft_view = DocumentDraftView()

        self.tools_sidebar = Gtk.Stack()
        self.tools_sidebar.set_size_request(266, 280)
        self.tools_sidebar.add_css_class('tools-sidebar')

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

        resources_folder = Files.get_resources_folder()

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_path(os.path.join(resources_folder, 'style.css'))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.css_provider_colors_default = Gtk.CssProvider()
        self.css_provider_colors_default.load_from_path(os.path.join(resources_folder, 'themes', 'default.css'))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_colors_default, 400)
        self.css_provider_colors = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_colors, 800)
        self.css_provider_fonts = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_fonts, 800)

        resources_folder = Files.get_resources_folder()
        icon_theme = Gtk.IconTheme.get_for_display(self.get_display())
        icon_theme.add_search_path(os.path.join(resources_folder, 'icons'))


