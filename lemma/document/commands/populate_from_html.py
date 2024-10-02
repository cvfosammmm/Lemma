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

import re, urllib.parse, os.path
from PIL import Image
from html.parser import HTMLParser

from lemma.document.ast.node import Node
from lemma.document.ast.link import Link


class Command(HTMLParser):

    def __init__(self, html, path):
        HTMLParser.__init__(self)

        self.html = html
        self.path = path
        self.is_undo_checkpoint = False
        self.update_implicit_x_position = True

        self.open_tags = list()
        self.tags = set()
        self.link_target = None
        self.paragraph_style = 'p'
        self.document = None
        self.composite = None

    def run(self, document):
        self.document = document
        self.composite = Node('list')

        head, divider, rest = self.html.partition('<body>')
        body, divider, rest = rest.partition('</body>')
        self.feed(head)

        if body == '':
            self.composite.append(Node('EOL', '\n'))
        else:
            self.feed(body)

        self.document.ast.root = self.composite
        self.document = None
        self.composite = None

        document.cursor.set_state([[0], [0]])
        document.set_scroll_insert_on_screen_after_layout_update()

    def handle_starttag(self, tag, attrs):
        self.open_tags.append(tag)

        if tag == 'br':
            node = Node('EOL', '\n')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)

        if tag == 'strong': self.tags.add('bold')
        if tag == 'em': self.tags.add('italic')
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.link_target = urllib.parse.unquote_plus(value)
        if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.paragraph_style = tag
        if tag == 'img':
            for name, value in attrs:
                if name == 'src':
                    path = urllib.parse.unquote_plus(value)
                    node = Node('image', Image.open(os.path.join(self.path, path)))
                    node.paragraph_style = self.paragraph_style
                    self.composite.append(node)

    def handle_endtag(self, tag):
        self.open_tags.pop()

        if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            node = Node('EOL', '\n')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)

        if tag == 'strong': self.tags.remove('bold')
        if tag == 'em': self.tags.remove('italic')
        if tag == 'a': self.link_target = None

    def handle_data(self, data):
        if 'title' in self.open_tags:
            self.document.title = data

        elif 'math' in self.open_tags:
            for char in data:
                self.composite.append(Node('mathsymbol', char))

        else:
            for char in data:
                if char != '\n':
                    node = Node('char', char)
                    node.tags = self.tags.copy()
                    node.paragraph_style = self.paragraph_style
                    if self.link_target != None:
                        node.link = Link(self.link_target)
                    self.composite.append(node)

    def undo(self, document):
        pass


