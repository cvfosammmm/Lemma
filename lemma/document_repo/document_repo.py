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

import os.path
from operator import attrgetter

from lemma.document.document import Document
from lemma.services.xml_parser import XMLParser
from lemma.services.paths import Paths
import lemma.services.timer as timer


class DocumentRepo():

    documents = list()
    documents_by_id = dict()
    documents_by_link_target = dict()
    link_targets_by_document = dict()
    max_document_id = 0

    pathname = None

    @timer.timer
    def init():
        DocumentRepo.pathname = Paths.get_notes_folder()

        for direntry in os.scandir(DocumentRepo.pathname):
            if direntry.is_file() and direntry.name.isdigit():
                document = Document(int(direntry.name))
                document.last_modified = os.path.getmtime(direntry.path)

                with open(direntry.path, 'r') as file:
                    xml = file.read()

                parser = XMLParser()
                nodes = parser.parse(xml)
                if nodes != None:
                    for node in nodes:
                        document.ast.append(node)
                    document.title = parser.title
                    document.cursor.set_state([document.ast[0].get_position(), document.ast[0].get_position()])
                    document.update()
                    document.change_flag[DocumentRepo] = False

                    DocumentRepo.documents.append(document)
                    DocumentRepo.documents_by_id[document.id] = document
                    DocumentRepo.update_link_graph(document)

        if len(DocumentRepo.documents_by_id) > 0:
            DocumentRepo.max_document_id = max(DocumentRepo.documents_by_id)
        else:
            DocumentRepo.max_document_id = 0

    @timer.timer
    def list():
        return [doc.id for doc in sorted(DocumentRepo.documents, key=lambda doc: -doc.last_modified)]

    @timer.timer
    def list_by_link_target(title):
        if title in DocumentRepo.documents_by_link_target:
            return [doc.id for doc in sorted(DocumentRepo.documents_by_link_target[title], key=lambda doc: -doc.last_modified)]
        return []

    @timer.timer
    def get_by_id(document_id):
        if document_id in DocumentRepo.documents_by_id:
            return DocumentRepo.documents_by_id[document_id]
        return None

    @timer.timer
    def get_by_title(title):
        for document in DocumentRepo.documents:
            if document.title == title:
                return document
        return None

    @timer.timer
    def get_by_terms_in_title(terms, limit=None):
        def is_match(document):
            if len(terms) == 0: return True
            return min(map(lambda x: x.lower() in document.title.lower(), terms))

        result = []
        for doc_id in DocumentRepo.list():
            doc = DocumentRepo.get_by_id(doc_id)
            if is_match(doc):
                result.append(doc)
            if len(result) == limit: break
        return result

    @timer.timer
    def get_max_document_id():
        return DocumentRepo.max_document_id

    @timer.timer
    def add(document):
        if document.id in DocumentRepo.documents_by_id: return

        DocumentRepo.documents.append(document)
        DocumentRepo.documents_by_id[document.id] = document
        DocumentRepo.max_document_id = max(document.id, DocumentRepo.max_document_id)

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        xml = document.xml

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(xml)

        DocumentRepo.update_link_graph(document)

    @timer.timer
    def delete(document):
        if document.id not in DocumentRepo.documents_by_id: return

        DocumentRepo.documents.remove(document)
        del(DocumentRepo.documents_by_id[document.id])

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        os.remove(pathname)

        DocumentRepo.update_link_graph(document)

    @timer.timer
    def update(document):
        if not document.has_changed(DocumentRepo): return

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        xml = document.xml

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(xml)

        DocumentRepo.update_link_graph(document)

    def update_link_graph(document):
        if document in DocumentRepo.link_targets_by_document:
            for link_target in DocumentRepo.link_targets_by_document[document]:
                DocumentRepo.documents_by_link_target[link_target].remove(document)
            del(DocumentRepo.link_targets_by_document[document])

        if document.id in DocumentRepo.documents_by_id:
            for link_target in document.links:
                if link_target not in DocumentRepo.documents_by_link_target:
                    DocumentRepo.documents_by_link_target[link_target] = set()
                DocumentRepo.documents_by_link_target[link_target].add(document)

                if document not in DocumentRepo.link_targets_by_document:
                    DocumentRepo.link_targets_by_document[document] = set()
                DocumentRepo.link_targets_by_document[document].add(link_target)


