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
from gi.repository import Gtk, Adw, Pango

from lemma.ui.scrolling_widget import ScrollingWidget
from lemma.ui.context_menu import ContextMenu


class DocumentListView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.add_css_class('document-list')
        self.set_focusable(True)
        self.set_size_request(266, 280)

        self.page_size = 1
        self.line_height = 70

        self.layout_header = Pango.Layout(self.get_pango_context())
        self.layout_header.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_header.set_font_description(Pango.FontDescription.from_string('Cantarell Bold 11'))

        self.layout_date = Pango.Layout(self.get_pango_context())
        self.layout_date.set_alignment(Pango.Alignment.RIGHT)
        self.layout_date.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.layout_teaser = Pango.Layout(self.get_pango_context())
        self.layout_teaser.set_ellipsize(Pango.EllipsizeMode.END)
        self.layout_teaser.set_font_description(Pango.FontDescription.from_string('NewComputerModern08 Book 13px'))

        self.layout_no_results = Pango.Layout(self.get_pango_context())
        self.layout_no_results.set_alignment(Pango.Alignment.CENTER)
        self.layout_no_results.set_font_description(Pango.FontDescription.from_string('Cantarell Black 14'))

        self.layout_no_results_details = Pango.Layout(self.get_pango_context())
        self.layout_no_results_details.set_alignment(Pango.Alignment.CENTER)
        self.layout_no_results_details.set_line_spacing(1.2)
        self.layout_no_results_details.set_font_description(Pango.FontDescription.from_string('Cantarell 11'))

        self.scrolling_widget = ScrollingWidget()
        self.content = self.scrolling_widget.content
        self.set_child(self.scrolling_widget.view)

        self.context_menu = ContextMenuDocumentList(self.content)


class ContextMenuDocumentList(ContextMenu):

    def __init__(self, parent):
        ContextMenu.__init__(self)

        self.popover.set_parent(parent)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)

        self.delete_document_button = self.create_button('Delete document', popdown=False)
        self.box.append(self.delete_document_button)


