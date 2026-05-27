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

from lemma.services.xml_exporter import XMLExporter
import lemma.services.timer as timer


class XML(object):

    def __init__(self, document):
        self.document = document

        self.paragraph_xml = dict()

    def invalidate_paragraph(self, paragraph):
        if paragraph in self.paragraph_xml:
            del(self.paragraph_xml[paragraph])

    @timer.timer
    def update(self):
        for paragraph in self.document.ast:
            if paragraph not in self.paragraph_xml:
                self.paragraph_xml[paragraph] = XMLExporter.export_paragraph(paragraph.children, paragraph.style, paragraph.indentation_level, paragraph.state)


