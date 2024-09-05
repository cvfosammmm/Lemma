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

import math


def rounded_rectangle(ctx, x, y, width, height, radius):
    ctx.move_to(x + radius, y)
    ctx.line_to(x + width - radius, y)
    ctx.arc(x + width - radius, y + radius, radius, -math.pi / 2, 0)
    ctx.line_to(x + width, y + height - radius)
    ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi / 2)
    ctx.line_to(x + radius, y + height)
    ctx.arc(x + radius, y + height - radius, radius, math.pi / 2, math.pi)
    ctx.line_to(x, y + radius)
    ctx.arc(x + radius, y + radius, radius, math.pi / 2, -math.pi / 2)


