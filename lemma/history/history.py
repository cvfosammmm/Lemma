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


class History():

    documents = list()
    active_document_index = None

    def add(document, remove_tail_after_last_active=True):
        if remove_tail_after_last_active and History.active_document_index != None:
            History.documents = History.documents[:History.active_document_index + 1]
        if document in History.documents:
            History.documents.remove(document)
        if len(History.documents) >= 100:
            History.documents = History.documents[-100:]
        History.documents.append(document)

    def activate_document(document):
        if document == None:
            History.active_document_index = None
        elif document in History.documents:
            History.active_document_index = History.documents.index(document)

    def delete(document):
        if document not in History.documents: return

        if History.documents.index(document) < History.active_document_index:
            History.active_document_index -= 1
        History.documents.remove(document)

    def get_active_document():
        if History.active_document_index == None: return None
        return History.documents[History.active_document_index]

    def get_next_in_line(document):
        if document not in History.documents: return None

        prev_doc = History.get_previous_if_any(document)
        if prev_doc != None: return prev_doc

        next_doc = History.get_next_if_any(document)
        if next_doc != None: return next_doc

        return None

    def get_previous_if_any(document):
        if document not in History.documents: return None

        index = History.documents.index(document)
        if index == 0: return None
        else: return History.documents[index - 1]

    def get_next_if_any(document):
        if document not in History.documents: return None

        index = History.documents.index(document)
        if index == (len(History.documents) - 1): return None
        else: return History.documents[index + 1]


