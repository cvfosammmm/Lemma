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


class Position(object):

    def __init__(self, *level_positions):
        self.level_positions = list(level_positions)

    def __str__(self): return self.level_positions.__str__()
    def __len__(self): return len(self.level_positions)
    def __iter__(self): return self.level_positions.__iter__()
    def __getitem__(self, key): return self.level_positions.__getitem__(key)
    def __eq__(self, other): return not self.__ne__(other)
    def __ne__(self, other): return other == None or self.__lt__(other) or self.__gt__(other)
    def __le__(self, other): return not self.__gt__(other)
    def __gt__(self, other): return other.__lt__(self)
    def __ge__(self, other): return not self.__lt__(other)

    def __lt__(self, other):
        if len(self) < len(other):
            for i in range(len(self)):
                if self[i] < other[i]: return True
                if self[i] > other[i]: return False
            return True
        if len(self) > len(other):
            for i in range(len(other)):
                if self[i] < other[i]: return True
                if self[i] > other[i]: return False
            return False
        else:
            for i in range(len(self)):
                if self[i] < other[i]: return True
                if self[i] > other[i]: return False
            return False


