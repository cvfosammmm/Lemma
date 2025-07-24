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

import pickle
import lemma.infrastructure.xml_helpers as xml_helpers


class XMLExporter(object):

    def __init__(self):
        pass

    def export_xml(self, node):
        attributes = ' paragraph_style="' + node.paragraph_style + '"'
        if node.link != None:
            attributes += ' link_target="' + xml_helpers.escape(node.link) + '"'
        if len(node.tags) > 0:
            attributes += ' tags="' + ' '.join(node.tags) + '"'

        if node.type == 'root':
            return '<root' + attributes + '>'\
                + ''.join([self.export_xml(child) for child in node]) + '</root>'

        if node.type == 'mathscript':
            return '<mathscript' + attributes + '>'\
                + ''.join([self.export_xml(child) for child in node]) + '</mathscript>'

        if node.type == 'mathfraction':
            return '<mathfraction' + attributes + '>'\
                + ''.join([self.export_xml(child) for child in node]) + '</mathfraction>'

        if node.type == 'mathroot':
            return '<mathroot' + attributes + '>'\
                + ''.join([self.export_xml(child) for child in node]) + '</mathroot>'

        if node.type == 'mathlist':
            return '<mathlist' + attributes + '>'\
                + ''.join([self.export_xml(child) for child in node]) + '</mathlist>'

        if node.type == 'char':
            return '<char' + attributes + '>' + xml_helpers.escape(node.value) + '</char>'

        if node.type == 'widget':
            return '<widget' + attributes + '><![CDATA[' + str(pickle.dumps(node.value)) + ']]></widget>'

        if node.type == 'placeholder':
            return '<placeholder' + attributes + '/>'

        if node.type == 'eol':
            return '<char' + attributes + '>\n</char>'

        if node.type == 'end':
            return '<end' + attributes + '/>'


