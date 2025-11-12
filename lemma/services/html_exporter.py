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
import os, os.path, shutil

from lemma.services.character_db import CharacterDB
from lemma.services.paths import Paths


class HTMLExporter(object):

    def __init__(self):
        self.files_folder = None
        self.file_no = 0
        self.document_id = None
        self.html = ''

    def export_document(self, document, filename):
        self.document_id = document.id
        self.files_folder = filename[:-3] + '_files'

        if os.path.exists(self.files_folder): shutil.rmtree(self.files_folder)
        os.mkdir(self.files_folder)

        self.file_no = 0

        self.html = '<html>\n'

        self.html += '<head>\n'
        self.html += '<title>' + document.title + '</title>\n'
        self.html += '</head>\n'

        self.html += '<body>\n'
        self.html += '<h1>' + document.title + '</h1>\n'

        for i, paragraph in enumerate(document.ast.paragraphs):
            if paragraph.style in ['ul']:
                if i == 0 or paragraph.style != document.ast.paragraphs[i-1].style:
                    self.html += '<' + paragraph.style + '><li>'
                else:
                    self.html += '<li>'
            else:
                self.html += '<' + paragraph.style + '>'

            node_lists = self.group_by_node_type(paragraph.nodes)

            for node_list in node_lists:
                self.process_list(node_list)

            if paragraph.style in ['ul']:
                if i == len(document.ast.paragraphs) - 1 or paragraph.style != document.ast.paragraphs[i+1].style:
                    self.html += '</li></' + paragraph.style + '>'
                else:
                    self.html += '</li>'
            else:
                self.html += '</' + paragraph.style + '>\n'
        self.html += '</body>\n'

        self.html += '</html>'
        return self.html

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
        if node_list[0].type == 'char':
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
            text = '<a href="' + urllib.parse.quote(node.link) + '.html">' + text + '</a>'

        self.html += text

    def process_node(self, node):
        if node.type == 'char' and CharacterDB.is_mathsymbol(node.value):
            if node.parent.type == 'root':
                self.html += '<math>'
            self.html += node.value
            if node.parent.type == 'root':
                self.html += '</math>'
        elif node.type == 'mathscript':
            if node.parent.type == 'root':
                self.html += '<math>'
            self.html += '<msubsup>'
            self.html += '<mn>'
            self.process_node(node[0])
            self.html += '</mn>'
            self.html += '<mn>'
            self.process_node(node[1])
            self.html += '</mn>'
            self.html += '</msubsup>'
            if node.parent.type == 'root':
                self.html += '</math>'
        elif node.type == 'mathfraction':
            if node.parent.type == 'root':
                self.html += '<math>'
            self.html += '<mfrac>'
            self.html += '<mn>'
            self.process_node(node[0])
            self.html += '</mn>'
            self.html += '<mn>'
            self.process_node(node[1])
            self.html += '</mn>'
            self.html += '</mfrac>'
            if node.parent.type == 'root':
                self.html += '</math>'
        elif node.type == 'mathroot':
            if node.parent.type == 'root':
                self.html += '<math>'
            self.html += '<mroot>'
            self.html += '<mtext>'
            self.process_node(node[0])
            self.html += '</mtext>'
            self.html += '<mtext>'
            self.process_node(node[1])
            self.html += '</mtext>'
            self.html += '</mroot>'
            if node.parent.type == 'root':
                self.html += '</math>'
        elif node.type == 'mathlist':
            for child in node:
                self.process_node(child)
        elif node.type == 'char':
            self.html += node.value
        elif node.type == 'placeholder':
            self.html += '<placeholder value="' + node.value + '"/>'
        elif node.type == 'widget':
            self.html += node.value.to_html(os.path.join(self.files_folder, str(self.file_no)))
            self.file_no += 1
        elif node.type == 'end':
            self.html += '<end/>'


