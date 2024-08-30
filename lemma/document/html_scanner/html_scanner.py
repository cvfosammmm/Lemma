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

import urllib.parse
from lemma.latex_db.latex_db import LaTeXDB


class HTMLScanner(object):

    def __init__(self, document):
        self.document = document

        self.html = ''

    def update(self):
        self.html = '<html>'

        self.html += '<head>'
        self.html += '<title>' + self.document.title + '</title>'
        self.html += '</head>'

        self.html += '<body>'
        lines = self.group_by_line(self.document.ast.root)
        for line in lines:
            node_lists = self.group_by_node_type(line)

            self.html += '<' + line[-1].paragraph_style + '>'
            for node_list in node_lists:
                self.process_list(node_list)
            self.html += '</' + line[-1].paragraph_style + '>\n'
        self.html += '</body>'

        self.html += '</html>'
        self.document.html = self.html

    def group_by_line(self, root_node):
        result = list()
        result.append(list())
        for node in root_node:
            result[-1].append(node)
            if node.is_eol():
                result.append(list())
        result.pop()

        return result

    def group_by_node_type(self, node_list):
        last_type = None
        last_tags = set()
        last_link = None
        result = list()
        for node in node_list:
            if node.type != last_type or node.tags.symmetric_difference(last_tags) or node.link != last_link:
                result.append(list())
                last_type = node.type
                last_tags = node.tags
                last_link = node.link
            result[-1].append(node)

        return result

    def process_list(self, node_list):
        if node_list[0].type == 'char' and not LaTeXDB.is_whitespace(node_list[0].value):
            self.process_word(node_list)
        else:
            for node in node_list:
                self.process_node(node)

    def process_word(self, node_list):
        if len(node_list) == 0: return

        text = ''
        for char in node_list:
            text += char.value

        node = node_list[0]
        if 'italic' in node.tags:
            text = '<em>' + text + '</em>'
        if 'bold' in node.tags:
            text = '<strong>' + text + '</strong>'
        if node.link != None:
            text = '<a href="' + urllib.parse.quote_plus(node.link.target) + '">' + text + '</a>'

        self.html += text

    def process_node(self, node):
        if node.type == 'placeholder':
            pass

        elif node.type == 'mathsymbol':
            self.html += '<math>'
            self.html += node.value
            self.html += '</math>'


