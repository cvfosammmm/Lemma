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

import os.path, os, pickle
from operator import attrgetter

from lemma.document.document import Document
from lemma.services.xml_parser import XMLParser
from lemma.services.paths import Paths
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class DocumentRepo():

    document_stubs_by_id = dict()
    history = list()
    active_document = None

    max_document_id = 0

    @timer.timer
    def init():
        pathname = os.path.join(Paths.get_notes_folder(), 'workspace')
        workspace_data = None
        if os.path.isfile(pathname):
            with open(pathname, 'rb') as file:
                try:
                    workspace_data = pickle.loads(file.read())
                except EOFError: pass

        stubs = dict()
        for direntry in os.scandir(Paths.get_stubs_folder()):
            with open(direntry.path, 'rb') as file:
                try:
                    stub = pickle.load(file)
                except EOFError: pass
                else:
                    stubs[int(direntry.name)] = stub

        for direntry in os.scandir(Paths.get_notes_folder()):
            if direntry.is_file() and direntry.name.isdigit():
                document_id = int(direntry.name)
                if document_id in stubs and direntry.stat().st_mtime == stubs[document_id]['last_modified']:
                    DocumentRepo.document_stubs_by_id[document_id] = stubs[document_id]
                    del(stubs[document_id])
                else:
                    document = DocumentRepo.get_by_id(document_id)
                    DocumentRepo.document_stubs_by_id[document_id] = {'id': document_id, 'last_modified': document.last_modified, 'title': document.title, 'plaintext': document.plaintext, 'links': document.links}
                    pathname = os.path.join(Paths.get_stubs_folder(), str(document.id))
                    with open(pathname, 'wb') as filehandle:
                        pickle.dump(DocumentRepo.document_stubs_by_id[document.id], filehandle)

                    if document_id in stubs:
                        del(stubs[document_id])

                    if workspace_data != None and workspace_data['active_document_id'] == document_id:
                        DocumentRepo.active_document = document

        for document_id in stubs:
            pathname = os.path.join(Paths.get_stubs_folder(), str(document_id))
            os.remove(pathname)

        if len(DocumentRepo.document_stubs_by_id) > 0:
            DocumentRepo.max_document_id = max(DocumentRepo.document_stubs_by_id)
        else:
            DocumentRepo.max_document_id = 0

        if workspace_data != None:
            DocumentRepo.history = [doc_id for doc_id in workspace_data['history'] if doc_id in DocumentRepo.document_stubs_by_id]
            if workspace_data['active_document_id'] in DocumentRepo.document_stubs_by_id and DocumentRepo.active_document == None:
                DocumentRepo.activate_document(workspace_data['active_document_id'], update_history=False)

    def list():
        return [stub for stub in sorted(DocumentRepo.document_stubs_by_id.values(), key=lambda stub: -stub['last_modified'])]

    def list_by_search_terms(terms, limit=None):
        result = []
        for doc_stub in DocumentRepo.list():
            if len(terms) == 0:
                result.append(doc_stub)
            elif min(map(lambda x: x in doc_stub['plaintext'] or x in doc_stub['title'], terms)):
                result.append(doc_stub)
        return result

    def list_by_link_target(title):
        result = []
        for document_stub in DocumentRepo.list():
            if title in document_stub['links']:
                result.append(document_stub)
        return result

    def list_by_terms_in_title(terms, limit=None):
        result = []
        for document_stub in DocumentRepo.list():
            if len(terms) == 0:
                result.append(document_stub)
            elif min(map(lambda x: x.lower() in document_stub['title'].lower(), terms)):
                result.append(document_stub)

            if len(result) == limit:
                break
        return result

    def list_by_history():
        return [DocumentRepo.get_stub_by_id(doc_id) for doc_id in DocumentRepo.history]

    def list_by_title(title):
        return [stub for stub in DocumentRepo.list() if stub['title'] == title]

    def get_stub_by_id(document_id):
        if document_id in DocumentRepo.document_stubs_by_id:
            return DocumentRepo.document_stubs_by_id[document_id]
        return None

    @timer.timer
    def get_by_id(document_id):
        pathname = os.path.join(Paths.get_notes_folder(), str(document_id))
        if not os.path.isfile(pathname): return None

        document = Document(document_id)
        document.last_modified = os.path.getmtime(pathname)

        with open(pathname, 'r') as file:
            xml = file.read()

        parser = XMLParser()
        paragraphs = parser.parse(xml)
        if paragraphs != None:
            for paragraph in paragraphs:
                document.ast.append_paragraph(paragraph)

        document.title = parser.title
        document.cursor.set_state([document.ast[0].get_position(), document.ast[0].get_position()])
        document.update()
        document.change_flag[DocumentRepo] = False

        return document

    def get_active_document():
        if DocumentRepo.active_document == None:
            return None
        return DocumentRepo.active_document

    def get_active_document_id():
        return DocumentRepo.active_document.id if DocumentRepo.active_document != None else None

    def get_prev_id_in_history(document_id):
        if document_id not in DocumentRepo.history: return None

        index = DocumentRepo.history.index(document_id)
        if index == 0: return None
        else:
            return DocumentRepo.history[index - 1]

    def get_next_id_in_history(document_id):
        if document_id not in DocumentRepo.history: return None

        index = DocumentRepo.history.index(document_id)
        if index == (len(DocumentRepo.history) - 1): return None
        else: return DocumentRepo.history[index + 1]

    @timer.timer
    def get_max_document_id():
        return DocumentRepo.max_document_id

    @timer.timer
    def add(document):
        if document.id in DocumentRepo.document_stubs_by_id: return

        pathname = os.path.join(Paths.get_notes_folder(), str(document.id))
        xml = document.xml

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(xml)

        DocumentRepo.document_stubs_by_id[document.id] = {'id': document.id, 'last_modified': document.last_modified, 'title': document.title, 'plaintext': document.plaintext, 'links': document.links}
        pathname = os.path.join(Paths.get_stubs_folder(), str(document.id))
        with open(pathname, 'wb') as filehandle:
            pickle.dump(DocumentRepo.document_stubs_by_id[document.id], filehandle)

        DocumentRepo.max_document_id = max(document.id, DocumentRepo.max_document_id)

    @timer.timer
    def delete(document_id):
        if document_id not in DocumentRepo.document_stubs_by_id: return

        pathname = os.path.join(Paths.get_notes_folder(), str(document_id))
        try:
            os.remove(pathname)
        except FileNotFoundError: pass

        if document_id == DocumentRepo.get_active_document_id():
            new_active_document_id = DocumentRepo.get_prev_id_in_history(document_id)
            if new_active_document_id == None:
                new_active_document_id = DocumentRepo.get_next_id_in_history(document_id)
            DocumentRepo.activate_document(new_active_document_id, update_history=False)

        del(DocumentRepo.document_stubs_by_id[document_id])
        pathname = os.path.join(Paths.get_stubs_folder(), str(document_id))
        try:
            os.remove(pathname)
        except FileNotFoundError: pass

        if document_id in DocumentRepo.history:
            DocumentRepo.history.remove(document_id)
        DocumentRepo.save_history()

    @timer.timer
    def update(document):
        if not document.has_changed(DocumentRepo): return

        pathname = os.path.join(Paths.get_notes_folder(), str(document.id))
        xml = document.xml

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(xml)

        DocumentRepo.document_stubs_by_id[document.id] = {'id': document.id, 'last_modified': document.last_modified, 'title': document.title, 'plaintext': document.plaintext, 'links': document.links}
        pathname = os.path.join(Paths.get_stubs_folder(), str(document.id))
        with open(pathname, 'wb') as filehandle:
            pickle.dump(DocumentRepo.document_stubs_by_id[document.id], filehandle)

    def activate_document(document_id, update_history):
        if document_id == None:
            DocumentRepo.active_document = None
        else:
            if update_history:
                DocumentRepo.add_to_history(document_id)
            DocumentRepo.active_document = DocumentRepo.get_by_id(document_id)

        DocumentRepo.save_history()

    def add_to_history(document_id):
        if document_id == None: return

        if DocumentRepo.active_document != None and DocumentRepo.active_document.id in DocumentRepo.history:
            DocumentRepo.history = DocumentRepo.history[:DocumentRepo.history.index(DocumentRepo.active_document.id) + 1]
        if document_id in DocumentRepo.history:
            DocumentRepo.history.remove(document_id)
        if len(DocumentRepo.history) >= 100:
            DocumentRepo.history = DocumentRepo.history[-100:]
        DocumentRepo.history.append(document_id)

    def save_history():
        pathname = os.path.join(Paths.get_notes_folder(), 'workspace')

        try: filehandle = open(pathname, 'wb')
        except IOError: pass
        else:
            active_document_id = DocumentRepo.active_document.id if DocumentRepo.active_document != None else None
            history_list = [document_id for document_id in DocumentRepo.history if document_id != None]
            data = {'active_document_id': active_document_id,
                    'history': history_list}
            filehandle.write(pickle.dumps(data))


