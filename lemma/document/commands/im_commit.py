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


class Command():

    def __init__(self, text):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.text = text

    def run(self, document):
        document.ast.insert_text_at_cursor(self.text)
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for char in reversed(self.text):
            document.ast.move_cursor_by_offset(-1)
            document.ast.delete_char_at_cursor()
        document.set_scroll_insert_on_screen_after_layout_update()


