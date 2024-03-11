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

import re

import lemma.document.ast.node as ast


def build_ast(markdown):
    document_lines = ast.Root()

    lines = markdown.splitlines()
    for line in lines:
        document_line = ast.Line()
        for segment in re.split(r'(\$`.*?`\$)', line):
            if segment.startswith('$`') and segment.endswith('`$'):
                add_math_to_line(document_line, segment[2:-2])
            else:
                add_non_math_to_line(document_line, segment)
        document_lines.append(document_line)

    if document_lines.length() == 0: document_lines.append(ast.Line())

    return document_lines


def add_non_math_to_line(document_line, text):
    for char in text:
        if char != '\n':
            document_line.append(ast.UnicodeCharacter(char))


def add_math_to_line(document_line, text):
    for name in re.split(r'(\\[^\\]*)', text):
        if name.startswith('\\'):
            document_line.append(ast.MathSymbol(name[1:]))


