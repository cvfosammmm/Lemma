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


class PlaintextScanner(object):

    def __init__(self, document):
        self.document = document

        self.text = ''
        self.current_line = ''

    def update(self):
        self.text = ''
        self.current_line = ''
        self.document.ast.root.accept(self)
        self.text = self.text[:-1] # remove last EOL
        self.document.plaintext = self.text

    def visit_root(self, root):
        for line in root.children:
            line.accept(self)

    def visit_line(self, line):
        for char in line.children:
            char.accept(self)

    def visit_beforemath(self, beforemath):
        pass

    def visit_matharea(self, mathlist):
        if self.current_line == '' or self.current_line[-1] != ' ':
            self.current_line += ' '

    def visit_mathsymbol(self, symbol):
        pass

    def visit_aftermath(self, aftermath):
        pass

    def visit_char(self, char):
        if char.is_whitespace:
            if self.current_line == '' or self.current_line[-1] != ' ':
                self.current_line += ' '
        else:
            self.current_line += char.content

    def visit_eol(self, node):
        self.current_line = self.current_line.strip()
        if self.current_line != '':
            self.text += self.current_line + '\n'
            self.current_line = ''


