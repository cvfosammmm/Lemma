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

from operator import attrgetter

from lemma.helpers.observable import Observable
from lemma.workspace.document_history import DocumentHistory
import lemma.infrastructure.timer as timer


class Workspace(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.active_document = None
        self.mode = 'documents'

        self.history = DocumentHistory(self)

    def get_active_document(self):
        return self.active_document

    def set_mode(self, mode):
        self.mode = mode

    def set_active_document(self, document):
        self.active_document = document


