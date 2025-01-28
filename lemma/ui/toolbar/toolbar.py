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
from gi.repository import Gtk, Pango

from lemma.helpers.observable import Observable
from lemma.infrastructure.layout_info import LayoutInfo


class ToolBar(Observable):

    def __init__(self, workspace, main_window, application):
        Observable.__init__(self)
        self.toolbar = main_window.toolbar
        self.workspace = workspace
        self.application = application

        self.toolbar.toolbar_widget_resizable.scale.connect('change-value', self.on_widget_scale_change_value)

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('document_changed', self.on_document_change)

    def on_new_active_document(self, workspace, document=None): self.update()
    def on_document_change(self, workspace, document): self.update()

    def update(self):
        self.update_toolbar()

    def update_toolbar(self):
        document = self.workspace.active_document
        if self.workspace.mode != 'documents' or document == None: return

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        if len(selected_nodes) == 1 and selected_nodes[0].is_widget() and selected_nodes[0].value.is_resizable():
            widget = selected_nodes[0].value

            self.toolbar.mode_stack.set_visible_child_name('widget_resizable')

            self.toolbar.toolbar_widget_resizable.status_label.set_text(widget.get_status_text())
            layout = Pango.Layout(self.toolbar.toolbar_widget_resizable.status_label.get_pango_context())
            layout.set_text(widget.get_longest_possible_status_text())
            self.toolbar.toolbar_widget_resizable.status_label.set_size_request(layout.get_extents()[0].width / Pango.SCALE + 20, -1)

            self.toolbar.toolbar_widget_resizable.scale.set_range(widget.get_minimum_width(), LayoutInfo.get_layout_width())

            self.toolbar.toolbar_widget_resizable.scale.set_value(widget.get_width())
            self.toolbar.toolbar_widget_resizable.scale.clear_marks()

            orig_width = widget.get_original_width()
            if orig_width > widget.get_minimum_width() and orig_width < LayoutInfo.get_layout_width():
                self.toolbar.toolbar_widget_resizable.scale.add_mark(orig_width, Gtk.PositionType.TOP)
        else:
            self.toolbar.mode_stack.set_visible_child_name('main')

    def on_widget_scale_change_value(self, scale, scroll, value):
        self.application.use_cases.resize_widget(value)
        return True


