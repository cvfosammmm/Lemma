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

from lemma.app.latex_db import LaTeXDB


class Housekeeper():

    def __init__(self, document):
        self.document = document

    def update(self):
        self.document.ast.root.accept(self)

    def visit_root(self, root):
        for line in root.children:
            line.accept(self)

    def visit_line(self, line):
        for char in line.children:
            char.accept(self)

    def visit_beforemath(self, beforemath):
        pass

    def visit_matharea(self, matharea):
        for char in matharea.children:
            char.accept(self)

    def visit_mathsymbol(self, symbol):
        if LaTeXDB.is_ordinary_symbol(symbol.content):
            symbol.layout_mode = 'ord'
        elif LaTeXDB.is_binary_operation(symbol.content):
            symbol.layout_mode = 'bin'
        elif LaTeXDB.is_relation(symbol.content):
            symbol.layout_mode = 'rel'
        elif LaTeXDB.is_punctuation_mark(symbol.content):
            symbol.layout_mode = 'punct'

    def visit_aftermath(self, aftermath):
        pass

    def visit_char(self, char):
        pass

    def visit_eol(self, node):
        pass


