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

    def __init__(self, x, y, animation_type):
        self.x = x
        self.y = y
        self.animation_type = animation_type
        self.state = dict()

    def run(self, document):
        self.state['clipping_state_before'] = document.clipping.get_state()

        document.clipping.set_target(int(self.x), int(self.y), self.animation_type)

        document.update_last_cursor_movement()

    def undo(self, document):
        document.clipping.set_state(self.state['clipping_state_before'])

        document.update_last_cursor_movement()


