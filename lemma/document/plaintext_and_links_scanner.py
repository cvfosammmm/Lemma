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

from lemma.services.node_type_db import NodeTypeDB
import lemma.services.timer as timer


class PlaintextAndLinksScanner(object):

    def __init__(self, document):
        self.document = document

        self.text = ''
        self.links = []

    def update(self):
        if self.document.has_changed(self):
            self.update_pal()

    @timer.timer
    def update_pal(self):
        self.text = ''
        self.links = []

        for child in self.document.ast:
            self.process_node(child)

        self.document.plaintext = self.text
        self.document.links = set(self.links)

    def process_node(self, node):
        if node.type == 'eol':
            self.text += '\n'

        elif node.type == 'char':
            if node.link != None:
                self.links.append(node.link)
            if NodeTypeDB.is_whitespace(node):
                if self.text == '' or self.text[-1] != ' ':
                    self.text += ' '
            else:
                self.text += node.value


