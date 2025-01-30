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
import datetime


class Timer():

    in_progress = dict()
    times = list()

    def start(name):
        Timer.in_progress[name] = time.time()

    def stop(name):
        Timer.times.append((name, time.time() - Timer.in_progress[name]))

    def print(only_cumulative=True):
        cumulative = dict()

        for (name, time) in Timer.times:
            if not only_cumulative:
                print(name + ': ' + ' '*(25 - len(name)) + '{:.6f}'.format(time) + ' seconds')

            if name not in cumulative:
                cumulative[name] = 0
            cumulative[name] += time

        if not only_cumulative:
            print('\n-------------------\nCumulative Times\n-------------------\n')

        for name, time in cumulative.items():
            print(name + ': ' + ' '*(25 - len(name)) + '{:.6f}'.format(time) + ' seconds')


