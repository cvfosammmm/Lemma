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

import uuid

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.code_runner import CodeRunner
from lemma.use_cases.use_cases import UseCases
from lemma.ui.shortcuts import Shortcuts
import lemma.services.timer as timer


class Computation():

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
        self.view = main_window.document_view
        self.toolbar = main_window.toolbar.main_right

        self.document = None
        self.code_cells_by_paragraph = dict()
        self.paragraphs_by_code_cell = dict()

        self.shortcut_controller_docview = Shortcuts.new_controller()
        self.shortcut_controller_docview.add_cb('execute_current_code_block', self.execute_code_block)
        self.view.content.add_controller(self.shortcut_controller_docview)

    def execute_code_block(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        paragraph = document.get_insert_node().paragraph()
        if paragraph in self.code_cells_by_paragraph and paragraph.style == 'code':
            cell_id = self.code_cells_by_paragraph[paragraph]
            paragraphs = self.paragraphs_by_code_cell[cell_id]

            code = ''
            for paragraph in paragraphs:
                code += ''.join([node.value for node in paragraph if node.type == 'char']) + '\n'
            CodeRunner.run(document.id, cell_id, code)

            paragraphs_to_be_removed = []
            next_paragraph = paragraphs[-1].next_in_parent()
            while next_paragraph != None and next_paragraph.style == 'result':
                paragraphs_to_be_removed.append(next_paragraph)
                next_paragraph = next_paragraph.next_in_parent()

            for paragraph in paragraphs_to_be_removed:
                UseCases.delete_paragraph(paragraph)

    @timer.timer
    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        code_cells_by_paragraph = dict()
        paragraphs_by_code_cell = dict()

        current_cell = []
        current_cell_id = uuid.uuid4()
        for paragraph in document.ast:
            if paragraph.style == 'code':
                current_cell.append(paragraph)
            else:
                if len(current_cell) > 0:
                    paragraphs_by_code_cell[current_cell_id] = current_cell
                    for paragraph in current_cell:
                        code_cells_by_paragraph[paragraph] = current_cell_id
                    current_cell = []
                    current_cell_id = uuid.uuid4()
        if len(current_cell) > 0:
            paragraphs_by_code_cell[current_cell_id] = current_cell
            for paragraph in current_cell:
                code_cells_by_paragraph[paragraph] = current_cell_id

        # The cells are now compared to the old ones. If they can be identified,
        # we asign them the same id. Firstly, there have to be some paragraphs
        # that were already in the old cell. But we don't want to allow splits,
        # so exactly one new cell should have paragraphs of the old one. Also,
        # we don't allow merges, so only one old cell can have paragraphs of the
        # new one. If all that is given, we replace the new cell_id with the old
        # one. The following code is supposed to do the identification.
        for prev_cell_id, paragraphs in self.paragraphs_by_code_cell.items():
            new_cells_with_same_paragraphs = set([code_cells_by_paragraph[paragraph] for paragraph in paragraphs if paragraph in code_cells_by_paragraph])
            if len(new_cells_with_same_paragraphs) == 1:
                cell_id = new_cells_with_same_paragraphs.pop()
                old_cells_with_same_paragraphs = set([self.code_cells_by_paragraph[paragraph] for paragraph in paragraphs_by_code_cell[cell_id] if paragraph in self.code_cells_by_paragraph])
                if len(old_cells_with_same_paragraphs) == 1:
                    paragraphs_by_code_cell[prev_cell_id] = paragraphs_by_code_cell[cell_id]
                    for paragraph in paragraphs_by_code_cell[prev_cell_id]:
                        code_cells_by_paragraph[paragraph] = prev_cell_id
                    del(paragraphs_by_code_cell[cell_id])

        self.code_cells_by_paragraph = code_cells_by_paragraph
        self.paragraphs_by_code_cell = paragraphs_by_code_cell

        if document != self.document:
            if self.document != None:
                CodeRunner.stop_kernel(self.document.id)
            self.document = document

        for result in CodeRunner.fetch_results(document.id):
            cell_id = result['computation_id']
            if cell_id in self.paragraphs_by_code_cell:
                paragraph = self.paragraphs_by_code_cell[cell_id][-1]
                while True:
                    next_paragraph = paragraph.next_in_parent()
                    if next_paragraph != None and next_paragraph.style == 'result':
                        paragraph = next_paragraph
                    else:
                        break

            if 'data' in result['result']:
                data = result['result']['data']
                insert_node = paragraph[-1].next()
                if 'text/plain' in data:
                    UseCases.insert_result_after_paragraph(data['text/plain'] + '\n', paragraph)

            elif 'traceback' in result['result']:
                error_msg = result['result']['ename'] + ': ' + result['result']['evalue'] + '\n'
                insert_node = paragraph[-1].next()
                UseCases.insert_result_after_paragraph(error_msg, paragraph)

            elif 'text' in result['result']:
                UseCases.insert_result_after_paragraph(result['result']['text'], paragraph)

        running_computations = CodeRunner.get_running_computations(document.id)
        if len(running_computations) > 0:
            self.toolbar.kernel_state_button.show_busy_state()
        else:
            self.toolbar.kernel_state_button.show_idle_state()

    def save_quit(self):
        CodeRunner.stop_all()


