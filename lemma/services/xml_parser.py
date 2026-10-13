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

from lemma.document.ast import Paragraph, Node
from lemma.widgets.factory import WidgetFactory
import lemma.services.xml_helpers as xml_helpers
from lemma.services.ast_validator import ASTValidator


class XMLParser():

    def parse(xml_string, check_parents=False):
        parser = XMLParserObject()
        paragraphs = parser.parse(xml_string, check_parents)

        return parser.title, parser.meta, paragraphs


class XMLParserObject(object):

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
        self.check_parents = False

        self.level = 0
        self.current_link = [None for i in range(20)]
        self.current_tags = [set() for i in range(20)]
        self.current_indentation_level = 0
        self.current_paragraph_state = 0

        self.title = ''
        self.meta = dict()

    def parse(self, xml_string, check_parents):
        self.paragraphs = []
        self.nodes = []
        self.current_node = None
        self.level = 0
        self.current_link = [None for i in range(20)]
        self.current_tags = [set() for i in range(20)]
        self.title = ''
        self.check_parents = check_parents

        xml_string = '<?xml version="1.0" encoding="utf-8"?><list>' + xml_string + '</list>'
        try:
            self.expat_parser.Parse(xml_string, 1)
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
        node = None

        if tag == 'meta':
            if 'name' in attrs and 'content' in attrs:
                self.meta[attrs['name']] = attrs['content']
        elif tag == 'a':
            if 'href' in attrs:
                self.current_link[self.level] = xml_helpers.unescape(attrs['href'])
        elif tag == 'em':
            self.current_tags[self.level].add('italic')
        elif tag == 'strong':
            self.current_tags[self.level].add('bold')
        elif tag == 'verb':
            self.current_tags[self.level].add('verbatim')
        elif tag == 'mark':
            self.current_tags[self.level].add('highlight')
        elif tag in ['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl', 'code', 'result']:
            if 'indentation_level' in attrs:
                self.current_indentation_level = int(attrs['indentation_level'])
            if 'state' in attrs:
                self.current_paragraph_state = attrs['state']
            else:
                self.current_paragraph_state = None
        elif tag in ['math', 'msub', 'msup', 'msubsup', 'mfrac', 'mroot', 'msqrt', 'mrow', 'end', 'placeholder', 'table', 'tr', 'td']:
            if self.check_parents:
                if self.current_node != None:
                    parent_type = self.current_node.type
                else:
                    parent_type = 'paragraph'
                if parent_type != None and ASTValidator.validate_node_for_parent(tag, parent_type):
                    node = Node(tag)
            else:
                node = Node(tag)
        elif tag == 'widget':
            attributes = dict()
            for key, value in attrs.items():
                if key != 'type':
                    attributes[key] = value

            widget = WidgetFactory.make_widget(attrs['type'], attributes)
            if widget != None:
                node = Node('widget', widget)

        if node != None:
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

        if tag in ['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl', 'code', 'result']:
            new_paragraph = Paragraph()
            for node in self.nodes:
                new_paragraph.append(node)
            new_paragraph.style = tag
            new_paragraph.indentation_level = self.current_indentation_level
            new_paragraph.state = self.current_paragraph_state
            self.paragraphs.append(new_paragraph)
            self.nodes = []
        elif tag == 'a':
            self.current_link[self.level] = None
        elif tag == 'em':
            self.current_tags[self.level].discard('italic')
        elif tag == 'strong':
            self.current_tags[self.level].discard('bold')
        elif tag == 'verb':
            self.current_tags[self.level].discard('verbatim')
        elif tag == 'mark':
            self.current_tags[self.level].discard('highlight')
        elif tag in ['math', 'msub', 'msup', 'msubsup', 'mfrac', 'mroot', 'msqrt', 'mrow', 'end', 'placeholder', 'table', 'tr', 'td', 'widget']:
            if self.current_node != None and self.current_node.type == tag:
                if self.current_node.parent != None:
                    self.current_node = self.current_node.parent
                else:
                    self.current_node = None
                self.level -= 1

    def handle_data(self, data):
        if 'head' in self.open_xml_tags and 'title' in self.open_xml_tags:
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


