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

import os.path, re
import lemma.document.ast.node as ast


class Command():

    def __init__(self, path):
        self.path = path
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True

    def run(self, document):
        document.last_modified = os.path.getmtime(self.path)

        with open(self.path, 'r') as file:
            content = file.read()

        if content.startswith('# '):
            line, newline, rest = content.partition('\n')
            document.title = line[1:].strip()

        if rest != '':
            document.ast.root = self.build_ast(rest)

        document.ast.insert.set_position([0, 0])
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        pass

    def build_ast(self, markdown):
        document_lines = ast.Root()

        lines = markdown.splitlines()
        for line in lines:
            document_line = ast.Line()
            for segment in re.split(r'(\$`.*?`\$)', line):
                if segment.startswith('$`') and segment.endswith('`$'):
                    self.add_math_to_line(document_line, segment[2:-2])
                else:
                    self.add_non_math_to_line(document_line, segment)
            document_lines.append(document_line)

        if document_lines.length() == 0: document_lines.append(ast.Line())

        return document_lines

    def add_non_math_to_line(self, document_line, text):
        for char in text:
            if char != '\n':
                document_line.append(ast.UnicodeCharacter(char))

    def add_math_to_line(self, document_line, text):
        for name in re.split(r'(\\[^\\]*)', text):
            if name.startswith('\\'):
                document_line.append(ast.MathSymbol(name[1:]))


