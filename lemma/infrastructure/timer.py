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
        Timer.start(original_function.__module__[6:] + '.' + original_function.__name__)
        return_value = original_function(*args, **kwargs)
        Timer.stop(original_function.__module__[6:] + '.' + original_function.__name__)
        return return_value

    return new_function


class Timer():

    in_progress = []
    times = list()
    times_by_name = dict()
    hierarchy = {'count': 0, 'time': 0, 'children': dict()}

    def start(name):
        Timer.in_progress.append([name, time.time()])

    def stop(name):
        node = Timer.hierarchy
        for ancestor in Timer.in_progress:
            if ancestor[0] not in node['children']:
                node['children'][ancestor[0]] = {'count': 0, 'time': 0, 'children': dict()}
            node = node['children'][ancestor[0]]

        exectime = time.time() - Timer.in_progress.pop()[1]
        node['count'] += 1
        node['time'] += exectime

    def print(only_cumulative=True):
        for (name, time) in Timer.times:
            if not only_cumulative:
                print(name + ': ' + ' '*(25 - len(name)) + '{:.6f}'.format(time) + ' seconds')

        if not only_cumulative:
            print('\n-------------------\nCumulative Times\n-------------------\n')

        Timer.print_hierarchy(Timer.hierarchy, 0)

    def print_hierarchy(hierarchy, spaces):
        for name in sorted(hierarchy['children'], key=lambda name: -hierarchy['children'][name]['time']):
            count = hierarchy['children'][name]['count']
            total = hierarchy['children'][name]['time']
            avg = total / count
            print(' '*spaces + name + ': ' + ' '*(60 - len(name) - spaces) + '{:.6f}{:7} {:.6f}'.format(total, count, avg))
            Timer.print_hierarchy(hierarchy['children'][name], spaces + 2)


