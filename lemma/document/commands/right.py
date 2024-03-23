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

    def __init__(self, offset):
        self.offset = offset
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['offset_moved'] = document.ast.move_insert_by_offset(self.offset)
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        document.ast.move_insert_by_offset(-self.state['offset_moved'])


