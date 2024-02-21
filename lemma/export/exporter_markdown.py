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


class ExporterMarkdown(object):

    def __init__(self):
        self.text_buffer = ''

    def export(self, document):
        self.text_buffer = ''
        document.lines.accept(self)

        # remove last EOL
        self.text_buffer = self.text_buffer[:-1]

        return self.text_buffer

    def visit_lines(self, lines):
        for line in lines:
            line.accept(self)

    def visit_line(self, line):
        for char in line:
            char.accept(self)

    def visit_char(self, char):
        if char.is_whitespace:
            if self.text_buffer == '' or self.text_buffer[-1] != ' ':
                self.text_buffer += ' '
        else:
            self.text_buffer += char.content

    def visit_eol(self, node):
        self.text_buffer += '\n'

    def visit_node(self, node):
        pass


