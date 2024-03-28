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

import time


def timer(original_function):
    
    def new_function(*args, **kwargs):
        start_time = time.time()
        return_value = original_function(*args, **kwargs)
        print(original_function.__name__ + ': ' + str(time.time() - start_time) + ' seconds')
        return return_value
    
    return  new_function


def position_less_than(position_1, position_2):
    if len(position_1) < len(position_2):
        for i in range(len(position_1)):
            if position_1[i] < position_2[i]: return True
            if position_1[i] > position_2[i]: return False
        return True
    if len(position_1) > len(position_2):
        for i in range(len(position_2)):
            if position_1[i] < position_2[i]: return True
            if position_1[i] > position_2[i]: return False
        return False
    else:
        for i in range(len(position_1)):
            if position_1[i] < position_2[i]: return True
            if position_1[i] > position_2[i]: return False
        return False


