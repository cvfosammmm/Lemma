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

import time


class Workspace():

    def __init__(self):
        self.last_modified = time.time()

        self.active_document = None
        self.history = []

        self.in_draft_mode = False

    def set_active_document(self, document, update_history):
        self.active_document = document

        if update_history and document != None:
            self.add_to_history(document.id)

    def enter_draft_mode(self):
        self.in_draft_mode = True

    def leave_draft_mode(self):
        self.in_draft_mode = False

    def add_to_history(self, document_id):
        if document_id == None: return

        if self.active_document != None and self.active_document.id in self.history:
            self.history = self.history[:self.history.index(self.active_document.id) + 1]
        if document_id in self.history:
            self.history.remove(document_id)
        if len(self.history) >= 100:
            self.history = self.history[-100:]
        self.history.append(document_id)

    def remove_from_history(self, document_id):
        if document_id in self.history:
            self.history.remove(document_id)

    def get_active_document(self):
        return self.active_document

    def get_active_document_id(self):
        return self.active_document.id if self.active_document != None else None

    def get_mode(self):
        if self.in_draft_mode:
            return 'draft'
        elif self.active_document != None:
            return 'documents'
        else:
            return 'welcome'

    def get_history(self):
        return self.history

    def get_prev_id_in_history(self, document_id):
        if document_id not in self.history: return None

        index = self.history.index(document_id)
        if index == 0: return None
        else:
            return self.history[index - 1]

    def get_next_id_in_history(self, document_id):
        if document_id not in self.history: return None

        index = self.history.index(document_id)
        if index == (len(self.history) - 1): return None
        else: return self.history[index + 1]


