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

import lemma.infrastructure.timer as timer


class PlaintextScanner(object):

    def __init__(self, document):
        self.document = document

        self.text = ''

    def update(self):
        if self.document.has_changed(self):
            self.update_text()

    @timer.timer
    def update_text(self):
        self.text = ''

        for child in self.document.ast:
            self.process_node(child)

        self.document.plaintext = self.text

    def process_node(self, node):
        if node.is_eol():
            self.text += '\n'

        elif node.is_char():
            if node.is_whitespace():
                if self.text == '' or self.text[-1] != ' ':
                    self.text += ' '
            else:
                self.text += node.value


