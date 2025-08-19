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


class LinksScanner(object):

    def __init__(self, document):
        self.document = document

    def update(self):
        if self.document.has_changed(self):
            self.update_links()

    @timer.timer
    def update_links(self):
        links = []

        for line in self.document.ast.lines:
            for node in line['nodes']:
                if node.link != None and node.type == 'char':
                    links.append(node.link)

        self.document.links = set(links)


