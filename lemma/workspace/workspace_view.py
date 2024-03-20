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

from lemma.welcome.welcome_view import WelcomeView
from lemma.title_widget.title_widget import TitleWidget
from lemma.app.service_locator import ServiceLocator
from lemma.headerbar.headerbar import HeaderBar
from lemma.toolbar.toolbar import ToolBar
from lemma.toolbar.sidebar import ToolsSidebar
from lemma.document_view.document_view_view import DocumentViewView
import lemma.animated_paned.animated_paned as animated_paned


class MainWindow(Adw.ApplicationWindow):

    def __init__(self, app):
        Adw.ApplicationWindow.__init__(self, application=app)

        self.app = app
        self.set_size_request(550, 550)

        self.popoverlay = Gtk.Overlay()
        self.set_content(self.popoverlay)

    def add_widgets(self, workspace):
        self.workspace = workspace
        self.headerbar = HeaderBar()
        self.headerbar.hb_right.history_overlay.set_child(self.workspace.history.view)
        self.toolbar = ToolBar()

        self.content_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.content_paned.get_style_context().add_class('content')
        self.content_paned.set_wide_handle(True)
        self.headerbar.bind_property('position', self.content_paned, 'position', GObject.BindingFlags.BIDIRECTIONAL)

        self.welcome = WelcomeView()
        self.document_view = DocumentViewView()
        self.tools_sidebar = ToolsSidebar()

        self.draft_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.draft_title_widget = TitleWidget(self)
        self.draft_title_widget.view.submit_button.set_label('Create Document')
        self.draft_box.append(self.draft_title_widget.view)

        self.content_stack = Gtk.Stack()
        self.content_stack.get_style_context().add_class('content')
        self.content_stack.add_named(self.welcome, 'welcome')
        self.content_stack.add_named(self.draft_box, 'draft_view')
        self.content_stack.add_named(self.document_view, 'document_view')

        self.document_view_paned = animated_paned.AnimatedHPaned(self.content_stack, self.tools_sidebar, False)
        self.document_view_paned.get_style_context().add_class('document-view')
        self.document_view_paned.set_wide_handle(True)

        self.content_with_toolbar = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content_with_toolbar.append(self.document_view_paned)
        self.content_with_toolbar.append(self.toolbar)

        self.content_paned.set_start_child(self.workspace.documents.view)
        self.content_paned.set_resize_start_child(False)
        self.content_paned.set_shrink_start_child(False)

        self.content_paned.set_end_child(self.content_with_toolbar)
        self.content_paned.set_resize_end_child(True)
        self.content_paned.set_shrink_end_child(False)

        self.main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.main_box.append(self.headerbar)
        self.main_box.append(self.content_paned)
        self.popoverlay.set_child(self.main_box)

        self.css_provider = Gtk.CssProvider()
        resources_path = ServiceLocator.get_resources_path()
        self.css_provider.load_from_path(os.path.join(resources_path, 'style.css'))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.css_provider_colors = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_colors, Gtk.STYLE_PROVIDER_PRIORITY_USER)


