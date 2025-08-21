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

import urllib.parse, os.path
from html.parser import HTMLParser as HTMLParserLib

from lemma.document.ast import RootNode, Node
from lemma.widgets.image import Image
from lemma.services.layout_info import LayoutInfo


class HTMLParser(HTMLParserLib):

    def __init__(self, html, path):
        HTMLParserLib.__init__(self)

        self.html = html
        self.path = path

        self.open_tags = list()
        self.tags = set()
        self.link_target = None
        self.paragraph_style = 'p'

        self.title = None
        self.composite = None
        self.composite_prev = None

    def run(self):
        self.composite = RootNode('root')

        head, divider, rest = self.html.partition('<body>')
        body, divider, rest = rest.partition('</body>')
        self.feed(head)

        if body != '':
            self.feed(body)
            self.composite[-2].parent.remove([self.composite[-3], self.composite[-2]])
            self.composite[-1].paragraph_style = self.paragraph_style

    def handle_starttag(self, tag, attrs):
        self.open_tags.append(tag)

        if tag == 'br':
            node = Node('eol')
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
            width = LayoutInfo.get_layout_width()
            for name, value in attrs:
                if name == 'src':
                    filename = urllib.parse.unquote_plus(value)
                if name == 'width':
                    width = int(value)

            try:
                with open(os.path.join(self.path, filename), 'rb') as file:
                    image = Image(file, attributes={'width': width})
                node = Node('widget', image)
                node.paragraph_style = self.paragraph_style
                self.composite.append(node)
            except FileNotFoundError: pass
        if tag == 'msubsup':
            node = Node('mathscript')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)
            self.composite = node
        if tag == 'mfrac':
            node = Node('mathfraction')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)
            self.composite = node
        if tag == 'mroot':
            node = Node('mathroot')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)
            self.composite = node
        if tag in ['mtext', 'mn']:
            node = Node('mathlist')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)
            self.composite = node
        if tag in ['mo']:
            self.composite_prev = self.composite
            self.composite = self.composite.parent
        if tag == 'placeholder':
            for name, value in attrs:
                if name == 'value':
                    node = Node('placeholder', value)
                    node.paragraph_style = self.paragraph_style
                    self.composite.append(node)
        if tag == 'end':
            node = Node('end')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)

    def handle_endtag(self, tag):
        self.open_tags.pop()

        if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            node = Node('eol')
            node.paragraph_style = self.paragraph_style
            self.composite.append(node)

        if tag == 'strong': self.tags.discard('bold')
        if tag == 'em': self.tags.discard('italic')
        if tag == 'a': self.link_target = None
        if tag == 'msubsup':
            self.composite = self.composite.parent
        if tag == 'mfrac':
            self.composite = self.composite.parent
        if tag == 'mroot':
            self.composite = self.composite.parent
        if tag in ['mtext', 'mn']:
            self.composite = self.composite.parent
        if tag in ['mo']:
            self.composite = self.composite_prev
            self.composite_prev = None

    def handle_data(self, data):
        if 'title' in self.open_tags:
            self.title = data

        elif 'math' in self.open_tags:
            for char in data:
                node = Node('char', char)
                node.paragraph_style = self.paragraph_style
                self.composite.append(node)

        else:
            for char in data:
                if char == '\n':
                    if len(self.open_tags) > 0:
                        char = ' '
                    else:
                        continue
                node = Node('char', char)
                node.tags = self.tags.copy()
                node.paragraph_style = self.paragraph_style
                if self.link_target != None:
                    node.link = self.link_target
                self.composite.append(node)


