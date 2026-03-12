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


class Helpers():

    def filesize_to_string(filesize):
        if filesize < 1024:
            return str(filesize) + ' bytes'
        elif filesize < 1048576:
            return '{:.1f}'.format(filesize / 1024) + ' kB'
        elif filesize < 1073741824:
            return '{:.1f}'.format(filesize / 1048576) + ' MB'
        else:
            return '{:.1f}'.format(filesize / 1073741824) + ' GB'


