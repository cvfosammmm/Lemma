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
import io

from lemma.document.ast import Paragraph, Node
from lemma.widgets.image import Image
import lemma.services.xml_helpers as xml_helpers


class XMLParser(object):

    def __init__(self):
        self.expat_parser = None
        self.expat_parser = xml.parsers.expat.ParserCreate()
        self.expat_parser.StartElementHandler = self.handle_starttag
        self.expat_parser.EndElementHandler = self.handle_endtag
        self.expat_parser.CharacterDataHandler = self.handle_data

        self.paragraphs = []
        self.nodes = []
        self.current_node = None
        self.open_xml_tags = []

        self.level = 0
        self.current_link = [None for i in range(20)]
        self.current_tags = [set() for i in range(20)]
        self.current_attributes = dict()
        self.current_indentation_level = 0
        self.current_paragraph_state = 0

        self.widget_data = ''
        self.title = ''

    def parse(self, xml_string):
        self.paragraphs = []
        self.nodes = []
        self.current_node = None
        self.level = 0
        self.current_link = [None for i in range(20)]
        self.current_tags = [set() for i in range(20)]
        self.title = ''
        try:
            self.expat_parser.Parse('<?xml version="1.0" encoding="utf-8"?><list>' + xml_string + '</list>', 1)
        except xml.parsers.expat.ExpatError as error:
            return None
        else:
            if len(self.paragraphs) == 0 and len(self.nodes) > 0:
                new_paragraph = Paragraph()
                for node in self.nodes:
                    new_paragraph.append(node)
                self.paragraphs.append(new_paragraph)
            return self.paragraphs

    def handle_starttag(self, tag, attrs):
        self.open_xml_tags.append(tag)

        if tag == 'a' and 'href' in attrs:
            self.current_link[self.level] = xml_helpers.unescape(attrs['href'])
        if tag == 'em':
            self.current_tags[self.level].add('italic')
        if tag == 'strong':
            self.current_tags[self.level].add('bold')
        if tag == 'mark':
            self.current_tags[self.level].add('highlight')

        if tag in ['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl']:
            if 'indentation_level' in attrs:
                self.current_indentation_level = int(attrs['indentation_level'])
            if 'state' in attrs:
                self.current_paragraph_state = attrs['state']
            else:
                self.current_paragraph_state = None

        if tag in ['mathscript', 'mathfraction', 'mathroot', 'mathlist', 'end', 'placeholder', 'widget']:
            if tag == 'mathscript':
                node = Node('mathscript')
            if tag == 'mathfraction':
                node = Node('mathfraction')
            if tag == 'mathroot':
                node = Node('mathroot')
            if tag == 'mathlist':
                node = Node('mathlist')
            if tag == 'end':
                node = Node('end')
            if tag == 'placeholder':
                node = Node('placeholder', '')
            if tag == 'widget':
                node = Node('widget', None)
                self.current_attributes = attrs
                self.widget_data = ''

            node.link = self.current_link[self.level]
            node.tags = self.current_tags[self.level].copy()

            if self.current_node != None:
                self.current_node.append(node)
            else:
                self.nodes.append(node)

            self.current_node = node
            self.level += 1

    def handle_endtag(self, tag):
        self.open_xml_tags.pop()

        if tag in ['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl']:
            new_paragraph = Paragraph()
            for node in self.nodes:
                new_paragraph.append(node)
            new_paragraph.style = tag
            new_paragraph.indentation_level = self.current_indentation_level
            new_paragraph.state = self.current_paragraph_state
            self.paragraphs.append(new_paragraph)
            self.nodes = []

        if tag == 'a':
            self.current_link[self.level] = None
        if tag == 'em':
            self.current_tags[self.level].discard('italic')
        if tag == 'strong':
            self.current_tags[self.level].discard('bold')
        if tag == 'mark':
            self.current_tags[self.level].discard('highlight')

        if tag in ['mathscript', 'mathfraction', 'mathroot', 'mathlist', 'end', 'placeholder', 'widget']:
            if tag == 'widget' and self.current_node.type == 'widget':
                if self.current_attributes['type'] == 'image':
                    self.current_node.value = Image(eval(self.widget_data), attributes=self.current_attributes)

            if self.current_node.parent != None:
                self.current_node = self.current_node.parent
            else:
                self.current_node = None
            self.level -= 1

    def handle_data(self, data):
        if self.current_node != None and self.current_node.type == 'widget':
            self.widget_data += data

        elif 'head' in self.open_xml_tags and 'title' in self.open_xml_tags:
            self.title += data

        else:
            for char in data:
                if char == '\n':
                    node = Node('eol')
                else:
                    node = Node('char', char)
                node.link = self.current_link[self.level]
                node.tags = self.current_tags[self.level].copy()

                if self.current_node != None:
                    self.current_node.append(node)
                else:
                    self.nodes.append(node)


