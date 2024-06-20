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

import os.path, re, mistune, urllib.parse
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
            document.ast.root = self.build_ast(rest)

        document.ast.set_cursor_state([[0], [0]])
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        pass

    def build_ast(self, markdown):
        root = Node('list')

        if markdown == '':
            root.append(Node('EOL', '\n'))
        else:
            for line in markdown.splitlines():
                if line != '':
                    self.parse_markdown(root, line)
                root.append(Node('EOL', '\n'))

        return root

    def parse_markdown(self, root, line):
        parser = mistune.create_markdown(renderer=None)
        for line in parser(line):
            if line['type'] == 'paragraph':
                for section in line['children']:
                    self.parse_section(root, section)

    def parse_section(self, root, section, tags=set(), link_target=None):
        if section['type'] == 'codespan':
            self.add_math(root, section['raw'])
        elif section['type'] == 'link':
            link_target = urllib.parse.unquote_plus(section['attrs']['url'])
            for child in section['children']:
                self.parse_section(root, child, tags, link_target)
        elif section['type'] == 'emphasis':
            tags.add('italic')
            for child in section['children']:
                self.parse_section(root, child, tags, link_target)
            tags.remove('italic')
        elif section['type'] == 'strong':
            tags.add('bold')
            for child in section['children']:
                self.parse_section(root, child, tags, link_target)
            tags.remove('bold')
        elif section['type'] == 'text':
            self.add_non_math(root, section['raw'].strip('$'), tags, link_target)
        elif section['type'] == 'softbreak':
            root.append(Node('EOL', '\n'))

    def add_non_math(self, composite, text, tags, link_target=None):
        for char in text:
            if char != '\n':
                node = Node('char', char)
                node.tags = tags.copy()
                if link_target != None:
                    node.link = Link(link_target)
                composite.append(node)

    def add_math(self, composite, text):
        for char in text:
            composite.append(Node('mathsymbol', char))


