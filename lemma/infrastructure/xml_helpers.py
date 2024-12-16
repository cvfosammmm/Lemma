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


class XMLHelpers(object):

    expat_parser = None
    current_node = []
    open_tags = []
    escape_translation = str.maketrans({'<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;'})

    def init():
        pass

    def escape(text):
        return text.translate(XMLHelpers.escape_translation)

    def parse(xml_string):
        XMLHelpers.expat_parser = xml.parsers.expat.ParserCreate()
        XMLHelpers.expat_parser.StartElementHandler = XMLHelpers.handle_starttag
        XMLHelpers.expat_parser.EndElementHandler = XMLHelpers.handle_endtag
        XMLHelpers.expat_parser.CharacterDataHandler = XMLHelpers.handle_data

        XMLHelpers.current_node = Node('list')
        XMLHelpers.open_tags = []
        XMLHelpers.expat_parser.Parse('<?xml version="1.0" encoding="utf-8"?><root>' + xml_string + '</root>', 1)
        return XMLHelpers.current_node

    def handle_starttag(tag, attrs):
        XMLHelpers.open_tags.append(tag)

        if tag == 'mathatom':
            node = Node('mathatom')
            XMLHelpers.current_node.append(node)
            XMLHelpers.current_node = node
        if tag == 'mathlist':
            node = Node('mathlist')
            XMLHelpers.current_node.append(node)
            XMLHelpers.current_node = node
        if tag == 'END':
            XMLHelpers.current_node.append(Node('END'))

    def handle_endtag(tag):
        XMLHelpers.open_tags.pop()

        if tag == 'mathatom':
            XMLHelpers.current_node = XMLHelpers.current_node.parent
        if tag == 'mathlist':
            XMLHelpers.current_node = XMLHelpers.current_node.parent

    def handle_data(data):
        for char in data:
            node = Node('char', char)
            XMLHelpers.current_node.append(node)


