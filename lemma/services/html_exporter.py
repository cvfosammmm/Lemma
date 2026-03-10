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


class HTMLExporter():

    files_folder = None
    html = ''

    def export_document(document, filename):
        HTMLExporter.files_folder = filename[:-3] + '_files'

        if os.path.exists(HTMLExporter.files_folder): shutil.rmtree(HTMLExporter.files_folder)
        os.mkdir(HTMLExporter.files_folder)

        HTMLExporter.html = '<html>\n'

        HTMLExporter.html += '<head>\n'
        HTMLExporter.html += '<title>' + document.title + '</title>\n'
        HTMLExporter.html += '</head>\n'

        HTMLExporter.html += '<body>\n'
        HTMLExporter.html += '<h1>' + document.title + '</h1>\n'

        for i, paragraph in enumerate(document.ast):
            if paragraph.style in ['ul', 'ol']:
                if i == 0 or paragraph.style != document.ast[i-1].style:
                    HTMLExporter.html += '<' + paragraph.style + '><li>'
                else:
                    HTMLExporter.html += '<li>'
            elif paragraph.style == 'cl':
                if i == 0 or paragraph.style != document.ast[i-1].style:
                    HTMLExporter.html += '<ul><li>'
                else:
                    HTMLExporter.html += '<li>'
            else:
                HTMLExporter.html += '<' + paragraph.style + '>'

            node_lists = HTMLExporter.group_by_node_type(paragraph.children)

            for node_list in node_lists:
                HTMLExporter.process_list(node_list)

            if paragraph.style in ['ul', 'ol']:
                if i == len(document.ast) - 1 or paragraph.style != document.ast[i+1].style:
                    HTMLExporter.html += '</li></' + paragraph.style + '>'
                else:
                    HTMLExporter.html += '</li>'
            elif paragraph.style == 'cl':
                if i == len(document.ast) - 1 or paragraph.style != document.ast[i+1].style:
                    HTMLExporter.html += '</li></ul>'
                else:
                    HTMLExporter.html += '</li>'
            else:
                HTMLExporter.html += '</' + paragraph.style + '>\n'
        HTMLExporter.html += '</body>\n'

        HTMLExporter.html += '</html>'
        return HTMLExporter.html

    def group_by_node_type(node_list):
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

    def process_list(node_list):
        if node_list[0].type == 'char':
            HTMLExporter.process_word(node_list)
        else:
            for node in node_list:
                HTMLExporter.process_node(node)

    def process_word(node_list):
        if len(node_list) == 0: return

        text = ''
        for char in node_list:
            text += char.value

        node = node_list[0]
        if 'italic' in node.tags:
            text = '<em>' + text + '</em>'
        if 'bold' in node.tags:
            text = '<strong>' + text + '</strong>'
        if 'verbatim' in node.tags:
            text = '<code>' + text + '</code>'
        if 'highlight' in node.tags:
            text = '<mark>' + text + '</mark>'
        if node.link != None:
            text = '<a href="' + urllib.parse.quote(node.link) + '.html">' + text + '</a>'

        HTMLExporter.html += text

    def process_node(node):
        if node.type == 'char' and CharacterDB.is_mathsymbol(node.value):
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '<math>'
            HTMLExporter.html += node.value
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '</math>'
        elif node.type == 'mathscript':
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '<math>'
            HTMLExporter.html += '<msubsup>'
            HTMLExporter.html += '<mn>'
            HTMLExporter.process_node(node[0])
            HTMLExporter.html += '</mn>'
            HTMLExporter.html += '<mn>'
            HTMLExporter.process_node(node[1])
            HTMLExporter.html += '</mn>'
            HTMLExporter.html += '</msubsup>'
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '</math>'
        elif node.type == 'mathfraction':
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '<math>'
            HTMLExporter.html += '<mfrac>'
            HTMLExporter.html += '<mn>'
            HTMLExporter.process_node(node[0])
            HTMLExporter.html += '</mn>'
            HTMLExporter.html += '<mn>'
            HTMLExporter.process_node(node[1])
            HTMLExporter.html += '</mn>'
            HTMLExporter.html += '</mfrac>'
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '</math>'
        elif node.type == 'mathroot':
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '<math>'
            HTMLExporter.html += '<mroot>'
            HTMLExporter.html += '<mtext>'
            HTMLExporter.process_node(node[0])
            HTMLExporter.html += '</mtext>'
            HTMLExporter.html += '<mtext>'
            HTMLExporter.process_node(node[1])
            HTMLExporter.html += '</mtext>'
            HTMLExporter.html += '</mroot>'
            if node.parent.type == 'paragraph':
                HTMLExporter.html += '</math>'
        elif node.type == 'mathlist':
            for child in node:
                HTMLExporter.process_node(child)
        elif node.type == 'char':
            HTMLExporter.html += node.value
        elif node.type == 'placeholder':
            HTMLExporter.html += '<placeholder value="' + node.value + '"/>'
        elif node.type == 'widget':
            HTMLExporter.html += node.value.to_html(HTMLExporter.files_folder)
        elif node.type == 'end':
            HTMLExporter.html += '<end/>'


