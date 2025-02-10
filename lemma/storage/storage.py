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

import os, os.path, pickle

from lemma.infrastructure.service_locator import ServiceLocator
from lemma.document_repo.document_repo import DocumentRepo
from lemma.history.history import History
from lemma.settings.settings import Settings
from lemma.application_state.application_state import ApplicationState


class Storage(object):

    def populate_settings():
        try: filehandle = open(os.path.join(ServiceLocator.get_config_folder(), 'settings.pickle'), 'rb')
        except IOError: return False
        else:
            try: Settings.data = pickle.load(filehandle)
            except EOFError: return False
        return True

    def populate_app_state():
        try: filehandle = open(os.path.join(ServiceLocator.get_config_folder(), 'app_state.pickle'), 'rb')
        except IOError: return False
        else:
            try: ApplicationState.data = pickle.load(filehandle)
            except EOFError: return False
        return True

    def populate_history():
        pathname = os.path.join(ServiceLocator.get_notes_folder(), 'workspace')
        if not os.path.isfile(pathname): return

        with open(pathname, 'rb') as file:
            data = pickle.loads(file.read())

            for document_id in data['history']:
                document = DocumentRepo.get_by_id(document_id)
                if document != None:
                    History.add(document, remove_tail_after_last_active=False)
                    if document_id == data['active_document_id']:
                        History.activate_document(document)

    def save_settings():
        try: filehandle = open(os.path.join(ServiceLocator.get_config_folder(), 'settings.pickle'), 'wb')
        except IOError: return False
        else: pickle.dump(Settings.data, filehandle)

    def save_app_state():
        try: filehandle = open(os.path.join(ServiceLocator.get_config_folder(), 'app_state.pickle'), 'wb')
        except IOError: return False
        else: pickle.dump(ApplicationState.data, filehandle)

    def save_history():
        pathname = os.path.join(ServiceLocator.get_notes_folder(), 'workspace')

        try: filehandle = open(pathname, 'wb')
        except IOError: pass
        else:
            active_document = History.get_active_document()
            if active_document != None:
                active_document_id = active_document.id
            else:
                active_document_id = None

            data = {'active_document_id': active_document_id,
                    'history': Storage.get_history_list()}
            filehandle.write(pickle.dumps(data))

    def get_history_list():
        history_list = []
        for i, document in enumerate(History.documents):
            if document != None:
                history_list.append(document.id)
        return history_list


