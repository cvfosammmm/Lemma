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

from lemma.document.ast.node import Node


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

    def parse(self, xml_string, root_node_type='root'):
        self.current_node = Node(root_node_type)
        self.expat_parser.Parse('<?xml version="1.0" encoding="utf-8"?><list>' + xml_string + '</list>', 1)

        return self.current_node

    def handle_starttag(self, tag, attrs):
        self.open_tags.append(tag)

        node = None
        if tag == 'mathatom':
            node = Node('mathatom')
            self.current_node.append(node)
            self.current_node = node
        if tag == 'mathlist':
            node = Node('mathlist')
            self.current_node.append(node)
            self.current_node = node
        if tag == 'end':
            node = Node('end')
            self.current_node.append(node)
        if tag == 'placeholder':
            node = Node('placeholder', '')
            self.current_node.append(node)

        if node != None and 'marks' in attrs:
            for mark in attrs['marks'].split():
                self.marks[mark] = node

    def handle_endtag(self, tag):
        self.open_tags.pop()

        if tag == 'mathatom':
            self.current_node = self.current_node.parent
        if tag == 'mathlist':
            self.current_node = self.current_node.parent

    def handle_data(self, data):
        for char in data:
            if char == '\n':
                node = Node('eol')
            else:
                node = Node('char', char)
            self.current_node.append(node)


