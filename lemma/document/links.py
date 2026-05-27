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

import lemma.services.timer as timer


class Links(object):

    def __init__(self, document):
        self.document = document

        self.paragraph_links = dict()
        self.links = set()

    def invalidate_paragraph(self, paragraph):
        if paragraph in self.paragraph_links:
            del(self.paragraph_links[paragraph])

    @timer.timer
    def update(self):
        self.links = set()

        for paragraph in self.document.ast:
            if paragraph not in self.paragraph_links:
                self.paragraph_links[paragraph] = set()
                for node in paragraph:
                    if node.link != None and node.type == 'char':
                        self.paragraph_links[paragraph].add(node.link)
            self.links |= self.paragraph_links[paragraph]


