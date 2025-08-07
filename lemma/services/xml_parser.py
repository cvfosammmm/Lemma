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

import xml.parsers.expat
import pickle

from lemma.document.ast import Node


class XMLParser(object):

    def __init__(self):
        self.expat_parser = None
        self.expat_parser = xml.parsers.expat.ParserCreate()
        self.expat_parser.StartElementHandler = self.handle_starttag
        self.expat_parser.EndElementHandler = self.handle_endtag
        self.expat_parser.CharacterDataHandler = self.handle_data

        self.current_node = None
        self.marks = dict()
        self.open_tags = []
        self.current_link = None
        self.current_tags = None
        self.current_paragraph_style = 'p'

    def parse(self, xml_string, root_node_type='root'):
        self.current_node = Node(root_node_type)
        self.expat_parser.Parse('<?xml version="1.0" encoding="utf-8"?><list>' + xml_string + '</list>', 1)

        return self.current_node

    def handle_starttag(self, tag, attrs):
        self.open_tags.append(tag)

        if 'link_target' in attrs:
            self.current_link = attrs['link_target']
        else:
            self.current_link = None
        if 'tags' in attrs:
            self.current_tags = set(attrs['tags'].split())
        else:
            self.current_tags = set()
        if 'paragraph_style' in attrs:
            self.current_paragraph_style = attrs['paragraph_style']
        else:
            self.current_paragraph_style = 'p'

        node = None
        if tag == 'mathscript':
            node = Node('mathscript')
            self.current_node.append(node)
            self.current_node = node
        if tag == 'mathfraction':
            node = Node('mathfraction')
            self.current_node.append(node)
            self.current_node = node
        if tag == 'mathroot':
            node = Node('mathroot')
            self.current_node.append(node)
            self.current_node = node
        if tag == 'mathlist':
            node = Node('mathlist')
            self.current_node.append(node)
            self.current_node = node
        if tag == 'end':
            node = Node('end')
            node.link = self.current_link
            node.tags = self.current_tags
            node.paragraph_style = self.current_paragraph_style
            self.current_node.append(node)
        if tag == 'placeholder':
            node = Node('placeholder', '')
            node.link = self.current_link
            node.tags = self.current_tags
            node.paragraph_style = self.current_paragraph_style
            self.current_node.append(node)
        if tag == 'widget':
            self.widget_data = ''

        if node != None and 'marks' in attrs:
            for mark in attrs['marks'].split():
                self.marks[mark] = node

    def handle_endtag(self, tag):
        self.open_tags.pop()

        if tag == 'mathscript':
            self.current_node = self.current_node.parent
        if tag == 'mathfraction':
            self.current_node = self.current_node.parent
        if tag == 'mathroot':
            self.current_node = self.current_node.parent
        if tag == 'mathlist':
            self.current_node = self.current_node.parent
        if tag == 'widget':
            node = Node('widget', pickle.loads(eval(self.widget_data)))
            node.link = self.current_link
            node.tags = self.current_tags
            node.paragraph_style = self.current_paragraph_style
            self.current_node.append(node)
            self.widget_data = ''

    def handle_data(self, data):
        if 'widget' in self.open_tags:
            self.widget_data += data

        else:
            for char in data:
                if char == '\n':
                    node = Node('eol')
                    node.link = self.current_link
                    node.tags = self.current_tags
                    node.paragraph_style = self.current_paragraph_style
                else:
                    node = Node('char', char)
                    node.link = self.current_link
                    node.tags = self.current_tags
                    node.paragraph_style = self.current_paragraph_style
                self.current_node.append(node)


