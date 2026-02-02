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

from lemma.workspace.workspace import Workspace
from lemma.services.paths import Paths


class WorkspaceRepo():

    workspace = None

    def init(DocumentRepo):
        WorkspaceRepo.workspace = Workspace()

        pathname = os.path.join(Paths.get_notes_folder(), 'workspace')
        workspace_data = None
        if os.path.isfile(pathname):
            with open(pathname, 'rb') as file:
                try:
                    workspace_data = pickle.loads(file.read())
                except EOFError: pass
                else:
                    if 'history' in workspace_data:
                        for document_id in workspace_data['history']:
                            if document_id in DocumentRepo.document_stubs_by_id:
                                WorkspaceRepo.workspace.history.append(document_id)
                    if 'bookmarks' in workspace_data:
                        for document_id in workspace_data['bookmarks']:
                            if document_id in DocumentRepo.document_stubs_by_id:
                                WorkspaceRepo.workspace.bookmarked_document_ids.append(document_id)
                    if 'active_document_id' in workspace_data:
                        if workspace_data['active_document_id'] in DocumentRepo.document_stubs_by_id:
                            document = DocumentRepo.get_by_id(workspace_data['active_document_id'])
                            WorkspaceRepo.workspace.set_active_document(document, update_history=False)

    def get_workspace():
        return WorkspaceRepo.workspace

    def update(workspace):
        pathname = os.path.join(Paths.get_notes_folder(), 'workspace')

        try: filehandle = open(pathname, 'wb')
        except IOError: pass
        else:
            active_document_id = workspace.active_document.id if workspace.active_document != None else None
            history_list = [document_id for document_id in workspace.history if document_id != None]
            data = {'active_document_id': active_document_id,
                    'history': history_list,
                    'bookmarks': workspace.bookmarked_document_ids}
            filehandle.write(pickle.dumps(data))


