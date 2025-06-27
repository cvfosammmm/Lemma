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

import sqlite3, os.path
from operator import attrgetter

from lemma.document.document import Document
from lemma.infrastructure.html_exporter import HTMLExporter
from lemma.infrastructure.html_parser import HTMLParser
from lemma.infrastructure.service_locator import ServiceLocator
import lemma.infrastructure.timer as timer


class DocumentRepo():

    documents = list()
    documents_by_id = dict()

    pathname = None
    db_pathname = None
    db_connection = None

    @timer.timer
    def init():
        DocumentRepo.db_pathname = os.path.join(ServiceLocator.get_config_folder(), 'lemma.db')
        DocumentRepo.db_connection = sqlite3.connect(DocumentRepo.db_pathname)

        cursor = DocumentRepo.db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS document(id INT PRIMARY KEY, last_modified BIGINT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS link_graph(document_id INT, link_target VARCHAR(2048))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON document (last_modified)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_backlinks ON link_graph (link_target)")
        DocumentRepo.db_connection.commit()

        DocumentRepo.pathname = ServiceLocator.get_notes_folder()

        for direntry in os.scandir(DocumentRepo.pathname):
            if direntry.is_file() and direntry.name.isdigit():
                document = Document(int(direntry.name))
                document.last_modified = os.path.getmtime(direntry.path)

                with open(direntry.path, 'r') as file:
                    html = file.read()

                parser = HTMLParser(html, DocumentRepo.pathname)
                parser.run()
                document.title = parser.title
                document.ast = parser.composite
                document.cursor.set_state([document.ast[0].get_position(), document.ast[0].get_position()])
                document.update()
                document.change_flag[DocumentRepo] = False

                DocumentRepo.documents.append(document)
                DocumentRepo.documents_by_id[document.id] = document
                DocumentRepo.update_db(document)


    @timer.timer
    def list(limit=None):
        cursor = DocumentRepo.db_connection.cursor()
        limit_clause = 'LIMIT ' + str(limit) if limit != None else ''
        result = cursor.execute("SELECT id FROM document ORDER BY last_modified DESC" + limit_clause)
        return [doc[0] for doc in result]

    @timer.timer
    def list_by_link_target(title, limit=None):
        cursor = DocumentRepo.db_connection.cursor()
        limit_clause = 'LIMIT ' + str(limit) if limit != None else ''
        result = cursor.execute("SELECT document.id FROM document INNER JOIN link_graph ON document.id=link_graph.document_id WHERE link_graph.link_target='" + title + "' ORDER BY document.last_modified DESC" + limit_clause)
        return [doc[0] for doc in result]

    @timer.timer
    def get_by_id(document_id):
        if document_id in DocumentRepo.documents_by_id:
            return DocumentRepo.documents_by_id[document_id]
        return None

    @timer.timer
    def get_by_title(title):
        for document in DocumentRepo.documents:
            if title == document.title:
                return document
        return None

    @timer.timer
    def get_by_terms_in_title(terms, limit=None):
        cursor = DocumentRepo.db_connection.cursor()
        query_result = cursor.execute("SELECT id FROM document ORDER BY last_modified DESC")

        def is_match(document):
            if len(terms) == 0: return True
            return min(map(lambda x: x.lower() in document.title.lower(), terms))

        result = []
        for doc in query_result:
            doc = DocumentRepo.get_by_id(doc[0])
            if is_match(doc):
                result.append(doc)
            if len(result) == limit: break
        return result

    @timer.timer
    def get_max_document_id():
        cursor = DocumentRepo.db_connection.cursor()
        for result in cursor.execute("SELECT MAX(id) FROM document"):
            if result[0] != None:
                return result[0]
            return 0

    def add(document):
        if document.id in DocumentRepo.documents_by_id: return

        DocumentRepo.documents.append(document)
        DocumentRepo.documents_by_id[document.id] = document

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        exporter = HTMLExporter()
        html = exporter.export_html(document)

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(html)

        DocumentRepo.update_db(document)

    def delete(document):
        if document.id not in DocumentRepo.documents_by_id: return

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        os.remove(pathname)

        DocumentRepo.documents.remove(document)
        del(DocumentRepo.documents_by_id[document.id])

        DocumentRepo.update_db(document)

    def update(document):
        if not document.has_changed(DocumentRepo): return

        pathname = os.path.join(DocumentRepo.pathname, str(document.id))
        exporter = HTMLExporter()
        html = exporter.export_html(document)

        try: filehandle = open(pathname, 'w')
        except IOError: pass
        else:
            filehandle.write(html)

        DocumentRepo.update_db(document)

    def update_db(document):
        cursor = DocumentRepo.db_connection.cursor()

        cursor.execute("DELETE FROM document WHERE id=" + str(document.id))
        cursor.execute("DELETE FROM link_graph WHERE document_id=" + str(document.id))

        if document.id in DocumentRepo.documents_by_id:
            links = DocumentRepo.find_links(document.ast)
            data = set()
            for link in links:
                data.add((document.id, link))

            cursor.execute("INSERT INTO document VALUES (" + str(document.id) + ", " + str(int(document.last_modified * 10000000)) + ")")
            cursor.executemany("INSERT INTO link_graph VALUES (?, ?)", list(data))

        DocumentRepo.db_connection.commit()

    def find_links(node):
        links = []
        if node.link != None:
            links.append(node.link)
        for child in node:
            links += DocumentRepo.find_links(child)
        return links


