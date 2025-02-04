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
from lemma.infrastructure.html_exporter import HTMLExporter
from lemma.infrastructure.html_parser import HTMLParser


class DocumentRepo():

    documents = list()
    documents_by_id = dict()

    max_document_id = 0
    links_by_target = dict()

    pathname = None

    def init(pathname):
        DocumentRepo.pathname = pathname

        for direntry in os.scandir(pathname):
            if direntry.is_file() and direntry.name.isdigit():
                document = Document(int(direntry.name))
                document.last_modified = os.path.getmtime(direntry.path)

                with open(direntry.path, 'r') as file:
                    html = file.read()

                parser = HTMLParser(html, pathname)
                parser.run()
                document.title = parser.title
                document.ast = parser.composite
                document.cursor.set_state([document.ast[0].get_position(), document.ast[0].get_position()])
                document.update()

                DocumentRepo.add(document)

    def list():
        DocumentRepo.documents.sort(key=attrgetter('last_modified'), reverse=True)

        return list(DocumentRepo.documents_by_id)

    def list_by_link_target(title):
        DocumentRepo.documents.sort(key=attrgetter('last_modified'), reverse=True)

        if title in DocumentRepo.links_by_target:
            return [DocumentRepo.get_by_title(doc).id for doc in DocumentRepo.links_by_target[title]]
        else: return []

    def get_by_id(document_id):
        if document_id in DocumentRepo.documents_by_id:
            return DocumentRepo.documents_by_id[document_id]
        return None

    def get_by_title(title):
        for document in DocumentRepo.documents:
            if title == document.title:
                return document
        return None

    def add(document):
        if document.id == None:
            document.id = DocumentRepo.max_document_id + 1
        DocumentRepo.max_document_id = max(DocumentRepo.max_document_id, document.id)

        DocumentRepo.documents.append(document)
        DocumentRepo.documents.sort(key=attrgetter('last_modified'), reverse=True)
        DocumentRepo.documents_by_id[document.id] = document
        DocumentRepo.update_links()

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        exporter = HTMLExporter()
        html = exporter.export_html(document)

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(html)

    def delete(document):
        if document.id not in DocumentRepo.documents_by_id: return

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        os.remove(pathname)

        DocumentRepo.documents.remove(document)
        del(DocumentRepo.documents_by_id[document.id])
        DocumentRepo.update_links()

    def update(document):
        if not document.ast.has_changed(DocumentRepo): return

        DocumentRepo.documents.sort(key=attrgetter('last_modified'), reverse=True)
        DocumentRepo.update_links()

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        exporter = HTMLExporter()
        html = exporter.export_html(document)

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(html)

    def update_links():
        links_by_target = dict()
        for document in DocumentRepo.documents:
            links = DocumentRepo.find_links(document.ast)
            for link in links:
                if link.target not in links_by_target:
                    links_by_target[link.target] = set()
                links_by_target[link.target].add(document.title)

        DocumentRepo.links_by_target = links_by_target

    def find_links(node):
        links = []
        if node.link != None:
            links.append(node.link)
        for child in node:
            links += DocumentRepo.find_links(child)
        return links


