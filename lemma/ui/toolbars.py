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

from lemma.services.message_bus import MessageBus
from lemma.services.layout_info import LayoutInfo
from lemma.application_state.application_state import ApplicationState
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.use_cases.use_cases import UseCases
from lemma.services.settings import Settings
import lemma.services.timer as timer


class ToolBars():

    def __init__(self, main_window):
        self.headerbar = main_window.headerbar
        self.toolbar = main_window.toolbar

        self.toolbar.toolbar_widget_resizable.scale.connect('change-value', self.on_widget_scale_change_value)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'pinned_documents_changed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'app_state_changed')
        MessageBus.subscribe(self, 'settings_changed')

    @timer.timer
    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'document_changed' in messages or 'app_state_changed' in messages or 'settings_changed' in messages:
            self.update()
            self.update_paragraph_style()

    @timer.timer
    def update(self):
        active_document = WorkspaceRepo.get_workspace().get_active_document()
        if active_document == None: return

        cursor_inside_link = active_document.get_insert_node().is_inside_link()
        edit_link_visible = ((not active_document.has_selection()) and cursor_inside_link)

        selected_nodes = active_document.get_selected_nodes()
        if len(selected_nodes) == 1 and selected_nodes[0].type == 'widget' and selected_nodes[0].value.is_resizable():
            widget = selected_nodes[0].value

            self.toolbar.mode_stack.set_visible_child_name('widget_resizable')

            self.toolbar.toolbar_widget_resizable.status_label.set_text(widget.get_status_text())
            layout = Pango.Layout(self.toolbar.toolbar_widget_resizable.status_label.get_pango_context())
            layout.set_text(widget.get_longest_possible_status_text())
            self.toolbar.toolbar_widget_resizable.status_label.set_size_request(layout.get_extents()[0].width / Pango.SCALE + 20, -1)

            self.toolbar.toolbar_widget_resizable.scale.set_range(widget.get_minimum_width(), LayoutInfo.get_max_layout_width())

            self.toolbar.toolbar_widget_resizable.scale.set_value(widget.get_width())
            self.toolbar.toolbar_widget_resizable.scale.clear_marks()

            orig_width = widget.get_original_width()
            if orig_width > widget.get_minimum_width() and orig_width < LayoutInfo.get_max_layout_width():
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

        self.update_button_visibility()

    def update_paragraph_style(self):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        current_node = document.get_first_selection_bound()
        paragraph_style_at_cursor = current_node.paragraph().style

        labels_dict = {'p': _('Normal'), 'h1': _('Heading 2'), 'h2': _('Heading 2'), 'h3': _('Heading 3'), 'h4': _('Heading 4'), 'h5': _('Heading 5'), 'h6': _('Heading 6'), 'ul': _('Bullet List'), 'ol': _('Numbered List'), 'cl': _('Checklist')}
        self.toolbar.toolbar_main.paragraph_style_menu_button_label.set_text(labels_dict[paragraph_style_at_cursor])

    def update_button_visibility(self):
        self.toolbar.toolbar_main.bold_button.set_visible(Settings.get_value('button_visible_bold'))
        self.toolbar.toolbar_main.italic_button.set_visible(Settings.get_value('button_visible_italic'))
        self.toolbar.toolbar_main.indent_less_button.set_visible(Settings.get_value('button_visible_decrease_indent'))
        self.toolbar.toolbar_main.indent_more_button.set_visible(Settings.get_value('button_visible_increase_indent'))
        self.toolbar.toolbar_main.ul_button.set_visible(Settings.get_value('button_visible_ul'))
        self.toolbar.toolbar_main.ol_button.set_visible(Settings.get_value('button_visible_ol'))
        self.toolbar.toolbar_main.cl_button.set_visible(Settings.get_value('button_visible_cl'))
        self.toolbar.toolbar_main.image_button.set_visible(Settings.get_value('button_visible_insert_image'))
        self.toolbar.toolbar_main.insert_link_button.set_visible(Settings.get_value('button_visible_insert_link'))

        tag_buttons_visible = Settings.get_value('button_visible_bold') or Settings.get_value('button_visible_italic')
        self.toolbar.toolbar_main.tag_buttons_separator.set_visible(tag_buttons_visible)

        list_buttons_visible = Settings.get_value('button_visible_ul') or Settings.get_value('button_visible_ol') or Settings.get_value('button_visible_cl')
        self.toolbar.toolbar_main.list_buttons_separator.set_visible(list_buttons_visible)

        indentation_buttons_visible = Settings.get_value('button_visible_decrease_indent') or Settings.get_value('button_visible_increase_indent')
        self.toolbar.toolbar_main.indentation_buttons_separator.set_visible(indentation_buttons_visible)

        insert_buttons_visible = Settings.get_value('button_visible_insert_image')
        self.toolbar.toolbar_main.insert_buttons_separator.set_visible(insert_buttons_visible)

        link_buttons_visible = Settings.get_value('button_visible_insert_link')
        self.toolbar.toolbar_main.link_buttons_separator.set_visible(link_buttons_visible)

    def on_widget_scale_change_value(self, scale, scroll, value):
        UseCases.resize_widget(value)
        return True


