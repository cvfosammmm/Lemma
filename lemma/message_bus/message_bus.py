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


class MessageBus():

    connected_functions = dict()

    def add_change_code(change_code, parameter=None):
        if change_code in MessageBus.connected_functions:
            for callback in MessageBus.connected_functions[change_code]:
                if parameter != None:
                    callback(parameter)
                else:
                    callback()

    def connect(change_code, callback):
        if change_code in MessageBus.connected_functions:
            MessageBus.connected_functions[change_code].add(callback)
        else:
            MessageBus.connected_functions[change_code] = {callback}

    def disconnect(change_code, callback):
        if change_code in MessageBus.connected_functions:
            MessageBus.connected_functions[change_code].discard(callback)
            if len(MessageBus.connected_functions[change_code]) == 0:
                del(MessageBus.connected_functions[change_code])


