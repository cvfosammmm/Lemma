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

import pickle, base64


class XMLExporter(object):

    def __init__(self):
        pass

    def export_xml_bytes(self, node):
        attributes = b' paragraph_style="' + node.paragraph_style.encode() + b'"'
        if node.link != None:
            attributes += b' link_target="' + node.link.target.encode() + b'"'
        if len(node.tags) > 0:
            attributes += b' tags="' + ' '.join(node.tags).encode() + b'"'

        if node.type == 'root':
            return b'<root' + attributes + b'>'\
                + b''.join([self.export_xml_bytes(child) for child in node.children]) + b'</root>'

        if node.type == 'mathatom':
            return b'<mathatom' + attributes + b'>'\
                + b''.join([self.export_xml_bytes(child) for child in node.children]) + b'</mathatom>'

        if node.type == 'mathlist':
            return b'<mathlist' + attributes + b'>'\
                + b''.join([self.export_xml_bytes(child) for child in node.children]) + b'</mathlist>'

        if node.type == 'char':
            return b'<char' + attributes + b'>' + node.value.encode() + b'</char>'

        if node.type == 'widget':
            return b'<widget' + attributes + b'><![CDATA[' + base64.b64encode(pickle.dumps(node.value)) + b']]></widget>'

        if node.type == 'placeholder':
            return b'<placeholder' + attributes + b'/>'

        if node.type == 'eol':
            return b'<eol' + attributes + b'/>'

        if node.type == 'end':
            return b'<end' + attributes + b'/>'


