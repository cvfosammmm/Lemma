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

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject

import os.path, os, pickle, time, threading

from lemma.document.document import Document
from lemma.document.ast import Paragraph
from lemma.services.xml_parser import XMLParser
from lemma.services.paths import Paths
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class DocumentRepo():

    document_stubs_by_id = dict()
    max_document_id = 0
    saving_schedule = dict()
    document_saving_lock = threading.Lock()
    stub_saving_lock = threading.Lock()

    @timer.timer
    def init():
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
                if document_id in stubs and direntry.stat().st_mtime >= stubs[document_id]['last_modified']:
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

        for document_id in stubs:
            pathname = os.path.join(Paths.get_stubs_folder(), str(document_id))
            os.remove(pathname)

        if len(DocumentRepo.document_stubs_by_id) > 0:
            DocumentRepo.max_document_id = max(DocumentRepo.document_stubs_by_id)
        else:
            DocumentRepo.max_document_id = 0

        GObject.timeout_add(1000, DocumentRepo.lazy_save_loop)

    @timer.timer
    def wrap_up():
        for document_id in list(DocumentRepo.saving_schedule):
            document = DocumentRepo.saving_schedule[document_id][0]
            del(DocumentRepo.saving_schedule[document_id])

            DocumentRepo.save_document(document, can_wait=False)

        for thread in threading.enumerate():
            try:
                thread.join()
            except RuntimeError:
                pass

    def list():
        return [stub for stub in sorted(DocumentRepo.document_stubs_by_id.values(), key=lambda stub: -stub['last_modified'])]

    @timer.timer
    def list_by_search_terms(terms, limit=None):
        if len(terms) == 0:
            return DocumentRepo.list()

        result = []
        for doc_stub in DocumentRepo.list():
            for term in terms:
                if min(x.casefold() in doc_stub['plaintext'].casefold() or x.casefold() in doc_stub['title'] for x in terms):
                    result.append(doc_stub)
                    break
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

    def list_by_title(title):
        return [stub for stub in DocumentRepo.list() if stub['title'] == title]

    def get_stub_by_id(document_id):
        if document_id in DocumentRepo.document_stubs_by_id:
            return DocumentRepo.document_stubs_by_id[document_id]
        return None

    @timer.timer
    def get_by_id(document_id):
        if document_id in DocumentRepo.saving_schedule:
            return DocumentRepo.saving_schedule[document_id][0]

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
                if len(paragraph) > 0 and paragraph[-1].type == 'eol':
                    document.ast.append(paragraph)
        if len(document.ast) > 1:
            document.ast.remove(document.ast[0])

        document.title = parser.title
        document.cursor.set_state([document.ast[0][0].get_position(), document.ast[0][0].get_position()])
        document.update()
        document.change_flag[DocumentRepo] = False

        return document

    @timer.timer
    def get_max_document_id():
        return DocumentRepo.max_document_id

    @timer.timer
    def add(document):
        if document.id in DocumentRepo.document_stubs_by_id: return

        DocumentRepo.document_stubs_by_id[document.id] = {'id': document.id, 'last_modified': document.last_modified, 'title': document.title, 'plaintext': document.plaintext, 'links': document.links}
        DocumentRepo.save_document(document, can_wait=False)
        DocumentRepo.max_document_id = max(document.id, DocumentRepo.max_document_id)

    @timer.timer
    def delete(document_id):
        if document_id not in DocumentRepo.document_stubs_by_id: return

        if document_id in DocumentRepo.saving_schedule:
            DocumentRepo.document_saving_lock.acquire()
            DocumentRepo.stub_saving_lock.acquire()
            del(DocumentRepo.saving_schedule[document_id])
            DocumentRepo.stub_saving_lock.release()
            DocumentRepo.document_saving_lock.release()

        pathname = os.path.join(Paths.get_notes_folder(), str(document_id))
        try:
            os.remove(pathname)
        except FileNotFoundError: pass

        del(DocumentRepo.document_stubs_by_id[document_id])
        pathname = os.path.join(Paths.get_stubs_folder(), str(document_id))
        try:
            os.remove(pathname)
        except FileNotFoundError: pass

    @timer.timer
    def update(document):
        if not document.has_changed(DocumentRepo): return

        DocumentRepo.document_stubs_by_id[document.id] = {'id': document.id, 'last_modified': document.last_modified, 'title': document.title, 'plaintext': document.plaintext, 'links': document.links}
        DocumentRepo.save_document(document, can_wait=True)

    @timer.timer
    def save_document(document, can_wait):
        if can_wait:
            DocumentRepo.saving_schedule[document.id] = (document, document.last_modified)
        else:
            pathname = os.path.join(Paths.get_notes_folder(), str(document.id))
            xml = document.get_xml()
            DocumentRepo.write_document_to_disk(xml, pathname)

            pathname = os.path.join(Paths.get_stubs_folder(), str(document.id))
            stub_file = pickle.dumps(DocumentRepo.document_stubs_by_id[document.id])
            DocumentRepo.write_stub_to_disk(stub_file, pathname)

    def lazy_save_loop():
        ready_to_save = list()
        for document_id, data in DocumentRepo.saving_schedule.items():
            if data[0].last_modified > data[1]: return True
            if time.time() - data[1] < 5: return True

            ready_to_save.append(document_id)

        for document_id in ready_to_save:
            document = DocumentRepo.saving_schedule[document_id][0]
            del(DocumentRepo.saving_schedule[document_id])

            pathname = os.path.join(Paths.get_notes_folder(), str(document.id))
            xml = document.get_xml()
            thread = threading.Thread(target=DocumentRepo.write_document_to_disk, args=(xml, pathname))
            thread.start()

            pathname = os.path.join(Paths.get_stubs_folder(), str(document.id))
            stub_file = pickle.dumps(DocumentRepo.document_stubs_by_id[document.id])
            thread = threading.Thread(target=DocumentRepo.write_stub_to_disk, args=(stub_file, pathname))
            thread.start()

        return True

    def write_document_to_disk(xml, pathname):
        DocumentRepo.document_saving_lock.acquire()
        with open(pathname, 'w') as filehandle:
            filehandle.write(xml)
        DocumentRepo.document_saving_lock.release()

    def write_stub_to_disk(stub_file, pathname):
        DocumentRepo.stub_saving_lock.acquire()
        with open(pathname, 'wb') as filehandle:
            filehandle.write(stub_file)
        DocumentRepo.stub_saving_lock.release()


