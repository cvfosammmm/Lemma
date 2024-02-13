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

from lemma.helpers.observable import Observable


class TeaserScanner(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.teaser = ''

        self.document.connect('changed', self.on_document_change)
        self.update()

    def on_document_change(self, document):
        self.update()

    def update(self):
        self.teaser = ''
        self.document.lines.accept(self)

    def visit_lines(self, lines):
        for line in lines:
            line.accept(self)

            if len(self.teaser) > 100: break

    def visit_line(self, line):
        for char in line:
            char.accept(self)

            if len(self.teaser) > 100: break

    def visit_char(self, char):
        if char.is_whitespace:
            if self.teaser == '' or self.teaser[-1] != ' ':
                self.teaser += ' '
        else:
            self.teaser += char.content

    def visit_eol(self, node):
        if self.teaser == '' or self.teaser[-1] != ' ':
            self.teaser += ' '

    def visit_node(self, node):
        pass


