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

import os.path, re, mistune
from lemma.document.ast.node import Node
from lemma.document.ast.link import Link


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
                document.ast.root = self.build_ast(document, rest)

        document.ast.set_cursor_state([[0], [0]])
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        pass

    def build_ast(self, document, markdown):
        root = Node('root')
        root.insert(0, Node('EOL'))

        parser = mistune.create_markdown(renderer=None)
        for line in parser(markdown):
            if line['type'] == 'blank_line':
                root.append(Node('EOL'))
            elif line['type'] == 'paragraph':
                for section in line['children']:
                    self.parse_section(document, root, section)
                root.append(Node('EOL'))

        return root

    def parse_section(self, document, root, section, tags=set(), link_target=None):
        if section['type'] == 'codespan':
            matharea = Node('matharea')
            matharea.insert(0, Node('placeholder'))
            self.add_math(document, matharea, section['raw'])
            root.append(matharea)
        elif section['type'] == 'link':
            link_target = section['attrs']['url']
            for child in section['children']:
                self.parse_section(document, root, child, tags, link_target)
        elif section['type'] == 'emphasis':
            tags.add('italic')
            for child in section['children']:
                self.parse_section(document, root, child, tags, link_target)
            tags.remove('italic')
        elif section['type'] == 'strong':
            tags.add('bold')
            for child in section['children']:
                self.parse_section(document, root, child, tags, link_target)
            tags.remove('bold')
        elif section['type'] == 'text':
            self.add_non_math(document, root, section['raw'].strip('$'), tags, link_target)
        elif section['type'] == 'softbreak':
            root.append(Node('EOL'))

    def add_non_math(self, document, composite, text, tags, link_target=None):
        for char in text:
            if char != '\n':
                node = Node(char)
                node.tags = tags.copy()
                if link_target != None:
                    node.link = Link(document.title, link_target)
                composite.append(node)

    def add_math(self, document, composite, text):
        for char in text:
            composite.append(Node(char))


