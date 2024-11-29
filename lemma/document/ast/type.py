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


class Type():

    def __init__(self, type_str):
        self.type_str = type_str

    def is_eol(self): return self.type_str == 'EOL'
    def is_mathsymbol(self): return self.type_str == 'mathsymbol'
    def is_char(self): return self.type_str == 'char'
    def is_widget(self): return self.type_str == 'widget'

    def to_str(self):
        return self.type_str

    def __eq__(self, other): return isinstance(other, Type) and self.type_str == other.type_str


