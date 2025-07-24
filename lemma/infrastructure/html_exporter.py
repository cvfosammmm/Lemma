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
import os, os.path

from lemma.db.character_db import CharacterDB
from lemma.infrastructure.service_locator import ServiceLocator


class HTMLExporter(object):

    def __init__(self):
        self.pathname = ServiceLocator.get_notes_folder()
        self.file_no = 0
        self.document_id = None
        self.html = ''

    def export_html(self, document):
        self.document_id = document.id

        data_dir = ServiceLocator.get_notes_folder()
        for file in [file for file in os.listdir(data_dir) if file.startswith(str(self.document_id) + '-')]:
            os.remove(os.path.join(data_dir, file))
        self.file_no = 0

        self.html = '<html>'

        self.html += '<head>'
        self.html += '<title>' + document.title + '</title>'
        self.html += '</head>'

        self.html += '<body>'
        lines = self.group_by_line(document.ast)
        for line in lines:
            node_lists = self.group_by_node_type(line)

            self.html += '<' + line[-1].get_paragraph_style() + '>'
            for node_list in node_lists:
                self.process_list(node_list)
            self.html += '</' + line[-1].get_paragraph_style() + '>\n'
        self.html += '</body>'

        self.html += '</html>'
        return self.html

    def group_by_line(self, root_node):
        result = list()
        result.append(list())
        for node in root_node:
            result[-1].append(node)
            if node.is_eol():
                result.append(list())

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
        if node_list[0].is_char():
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
            text = '<a href="' + urllib.parse.quote_plus(node.link) + '">' + text + '</a>'

        self.html += text

    def process_node(self, node):
        if node.type == 'char' and CharacterDB.is_mathsymbol(node.value):
            if node.parent.is_root():
                self.html += '<math>'
            self.html += node.value
            if node.parent.is_root():
                self.html += '</math>'
        elif node.is_mathscript():
            if node.parent.is_root():
                self.html += '<math>'
            self.html += '<msubsup>'
            self.html += '<mn>'
            self.process_node(node[0])
            self.html += '</mn>'
            self.html += '<mn>'
            self.process_node(node[1])
            self.html += '</mn>'
            self.html += '</msubsup>'
            if node.parent.is_root():
                self.html += '</math>'
        elif node.is_mathfraction():
            if node.parent.is_root():
                self.html += '<math>'
            self.html += '<mfrac>'
            self.html += '<mn>'
            self.process_node(node[0])
            self.html += '</mn>'
            self.html += '<mn>'
            self.process_node(node[1])
            self.html += '</mn>'
            self.html += '</mfrac>'
            if node.parent.is_root():
                self.html += '</math>'
        elif node.is_mathroot():
            if node.parent.is_root():
                self.html += '<math>'
            self.html += '<mroot>'
            self.html += '<mtext>'
            self.process_node(node[0])
            self.html += '</mtext>'
            self.html += '<mtext>'
            self.process_node(node[1])
            self.html += '</mtext>'
            self.html += '</mroot>'
            if node.parent.is_root():
                self.html += '</math>'
        elif node.is_mathlist():
            for child in node:
                self.process_node(child)
        elif node.is_char():
            self.html += node.value
        elif node.is_placeholder():
            self.html += '<placeholder value="' + node.value + '"/>'
        elif node.is_widget():
            self.html += node.value.to_html(os.path.join(self.pathname, str(self.document_id) + '-' + str(self.file_no)))
            self.file_no += 1
        elif node.is_end():
            self.html += '<end/>'


