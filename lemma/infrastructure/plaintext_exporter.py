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


class PlaintextExporter(object):

    def __init__(self):
        self.text = ''

    def export_plaintext(self, document, max_length=None):
        self.text = ''

        for child in document.ast:
            self.process_node(child)

            if max_length != None and len(self.text) >= max_length:
                break

        return self.text

    def process_node(self, node):
        if node.is_eol():
            self.text += '\n'

        elif node.is_char():
            if node.is_whitespace():
                if self.text == '' or self.text[-1] != ' ':
                    self.text += ' '
            else:
                self.text += node.value


