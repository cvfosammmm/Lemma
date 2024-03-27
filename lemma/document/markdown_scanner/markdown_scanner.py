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


class MarkdownScanner(object):

    def __init__(self, document):
        self.document = document

        self.markdown = ''

    def update(self):
        self.markdown = '# ' + self.document.title + '\n'
        self.document.ast.root.accept(self)
        self.markdown = self.markdown[:-1] # remove last EOL
        self.document.markdown = self.markdown

    def visit_root(self, root):
        for child in root.children:
            child.accept(self)

    def visit_placeholder(self, placeholder):
        if placeholder.name == 'EOL':
            self.markdown += '\n'

    def visit_matharea(self, mathlist):
        self.markdown += '$`'
        for symbol in mathlist.children:
            symbol.accept(self)
        self.markdown += '`$'

    def visit_mathsymbol(self, symbol):
        self.markdown += symbol.content

    def visit_char(self, char):
        self.markdown += char.content


