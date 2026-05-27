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


class Plaintext(object):

    def __init__(self, document):
        self.document = document

        self.paragraph_plaintexts = dict()
        self.plaintext = ''

    def invalidate_paragraph(self, paragraph):
        if paragraph in self.paragraph_plaintexts:
            del(self.paragraph_plaintexts[paragraph])

    @timer.timer
    def update(self):
        self.plaintext = ''

        for paragraph in self.document.ast:
            if paragraph not in self.paragraph_plaintexts:
                text = ''
                for node in paragraph:
                    if node.type == 'char':
                        text += node.value
                    elif node.type == 'eol':
                        text += '\n'
                    elif node.type == 'widget':
                        text += node.value.to_plaintext()
                self.paragraph_plaintexts[paragraph] = text
            self.plaintext += self.paragraph_plaintexts[paragraph]


