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

from lemma.services.layout_info import LayoutInfo
from lemma.history.history import History
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases


class ToolBars():

    def __init__(self, main_window):
        self.headerbar = main_window.headerbar
        self.toolbar = main_window.toolbar

        self.toolbar.toolbar_widget_resizable.scale.connect('change-value', self.on_widget_scale_change_value)

    def update(self):
        active_document = History.get_active_document()
        if active_document == None: return

        has_active_doc = active_document != None
        has_selection = has_active_doc and active_document.cursor.has_selection()
        cursor_inside_link = has_active_doc and active_document.cursor.get_insert_node().is_inside_link()
        edit_link_visible = has_active_doc and ((not has_selection) and cursor_inside_link)

        selected_nodes = active_document.ast.get_subtree(*active_document.cursor.get_state())
        if len(selected_nodes) == 1 and selected_nodes[0].type == 'widget' and selected_nodes[0].value.is_resizable():
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
            if edit_link_visible:
                self.toolbar.toolbar_main.insert_link_button.set_tooltip_text(_('Edit Link') + ' (Ctrl+L)')
            else:
                self.toolbar.toolbar_main.insert_link_button.set_tooltip_text(_('Insert Link') + ' (Ctrl+L)')

            self.toolbar.mode_stack.set_visible_child_name('main')

        button_popover_rel = list()
        button_popover_rel.append([self.headerbar.hb_left.hamburger_menu_button, 'hamburger_menu'])
        button_popover_rel.append([self.headerbar.hb_right.document_menu_button, 'document_menu'])
        button_popover_rel.append([self.toolbar.toolbar_main.paragraph_style_menu_button, 'paragraph_style'])
        button_popover_rel.append([self.toolbar.toolbar_right.edit_menu_button, 'edit_menu'])

        for button, popover_name in button_popover_rel:
            if ApplicationState.get_value('active_popover') == popover_name:
                button.add_css_class('active')
            else:
                button.remove_css_class('active')

    def on_widget_scale_change_value(self, scale, scroll, value):
        UseCases.resize_widget(value)
        return True


