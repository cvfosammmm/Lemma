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

from lemma.ui.context_menus.context_menu import ContextMenu


class ContextMenuDocumentList(ContextMenu):
    
    def __init__(self, document_list):
        ContextMenu.__init__(self)
        self.document_list = document_list
        self.parent = document_list.view.scrolling_widget

        self.popup_offset_x, self.popup_offset_y = 0, 0

        self.popover.set_parent(self.parent.content)
        self.popover.set_size_request(260, -1)
        self.popover.set_offset(130, 0)
        self.popover.connect('closed', self.on_popover_close)

        self.delete_document_button = self.create_button('Delete document')
        self.delete_document_button.connect('clicked', self.on_delete_document_clicked)
        self.box.append(self.delete_document_button)

        self.parent.connect('secondary_button_press', self.on_secondary_button_press)

    def on_secondary_button_press(self, content, data):
        x_offset, y_offset, state = data
        self.popup_offset_x, self.popup_offset_y = x_offset, y_offset

        if state == 0:
            item_num = self.document_list.view.get_item_at_cursor()
            if item_num != None and item_num < len(self.document_list.workspace.documents):
                self.document_list.set_selected_index(item_num)
                self.popup_at_cursor(x_offset - content.scrolling_offset_x, y_offset - content.scrolling_offset_y)

        return True

    def on_delete_document_clicked(self, button):
        index = self.document_list.selected_index
        self.popover.popdown()
        self.document_list.workspace.delete_document(self.document_list.workspace.documents[index])

    def on_popover_close(self, popover):
        self.document_list.set_selected_index(None)


