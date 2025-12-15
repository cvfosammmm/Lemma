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


class LayoutInfo():

    def get_max_layout_width():
        return 670

    def get_title_width():
        return 500

    def get_title_height():
        return 54

    def get_subtitle_height():
        return 51

    def get_document_padding_left():
        return 48

    def get_document_padding_bottom():
        return 120

    def get_document_padding_top():
        return 48

    def get_normal_document_offset():
        return 153 # padding + title

    def get_indentation(paragraph_style, indentation_level=0):
        if paragraph_style == 'ul':
            indentation = 36
        elif paragraph_style == 'ol':
            indentation = 36
        elif paragraph_style == 'cl':
            indentation = 36
        else:
            indentation = 0
        indentation += indentation_level * 36

        return indentation

    def get_ul_bullet_padding():
        return 16

    def get_ol_bullet_padding():
        return 12

    def get_min_image_size():
        return 16


