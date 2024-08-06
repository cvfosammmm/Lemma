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


class Clipping(object):

    def __init__(self, document):
        self.document = document

        self.offset_x, self.offset_y = 0, 0

    def update(self):
        pass

    def set_scrolling_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def get_state(self):
        return self.offset_x, self.offset_y

    def set_state(self, state):
        self.offset_x, self.offset_y = state


