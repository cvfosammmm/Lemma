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

import lemma.services.xml_helpers as xml_helpers


class XMLExporter():

    def export(nodes):
        xml = ''
        current_paragraph_tag = None

        node_lists = XMLExporter.group_by_node_type(nodes)
        for node_list in node_lists:
            if current_paragraph_tag == None:
                current_paragraph_tag = node_list[0].get_paragraph_style()
                xml += '<' + current_paragraph_tag + '>'
            xml += XMLExporter.process_list(node_list)
            if node_list[0].type == 'eol':
                xml += '</' + current_paragraph_tag + '>'
                current_paragraph_tag = None
        if current_paragraph_tag != None:
            xml += '</' + current_paragraph_tag + '>'
            current_paragraph_tag = None

        return xml

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
        xml = ''

        if node_list[0].type == 'char':
            xml += XMLExporter.export_word(node_list)
        else:
            for node in node_list:
                xml += XMLExporter.export_node(node)

        return xml

    def export_word(node_list):
        if len(node_list) == 0: return

        xml = ''
        for char in node_list:
            xml += char.value

        node = node_list[0]
        xml = xml_helpers.embellish_with_link_and_tags(xml_helpers.escape(xml), node.link, node.tags)

        return xml

    def export_node(node):
        xml = ''

        if node.type == 'mathscript':
            xml = '<mathscript>' + ''.join([XMLExporter.export_node(child) for child in node]) + '</mathscript>'

        if node.type == 'mathfraction':
            xml = '<mathfraction>' + ''.join([XMLExporter.export_node(child) for child in node]) + '</mathfraction>'

        if node.type == 'mathroot':
            xml = '<mathroot>' + ''.join([XMLExporter.export_node(child) for child in node]) + '</mathroot>'

        if node.type == 'mathlist':
            xml = '<mathlist>' + ''.join([XMLExporter.export_node(child) for child in node]) + '</mathlist>'

        if node.type == 'char':
            xml = '<char>' + xml_helpers.escape(node.value) + '</char>'

        if node.type == 'widget':
            data = node.value.get_data()
            attributes = ''
            for key, value in node.value.get_attributes().items():
                attributes += ' ' + key + '="' + value + '"'
            xml = '<widget' + attributes + '><![CDATA[' + str(data) + ']]></widget>'

        if node.type == 'placeholder':
            xml = '<placeholder/>'

        if node.type == 'eol':
            xml = '\n'

        if node.type == 'end' and node.parent.type != 'root':
            xml = '<end/>'

        xml = xml_helpers.embellish_with_link_and_tags(xml, node.link, node.tags)

        return xml


