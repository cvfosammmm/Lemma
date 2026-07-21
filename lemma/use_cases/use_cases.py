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

from urllib.parse import urlparse
import webbrowser
import os.path
import time, io
from markdown_it import MarkdownIt

import lemma.services.xml_helpers as xml_helpers
import lemma.services.xml_exporter as xml_exporter
from lemma.services.xml_parser import XMLParser
from lemma.services.settings import Settings
from lemma.services.regex import RegexService
from lemma.services.files import Files
from lemma.services.node_type_db import NodeTypeDB
from lemma.document.ast import Node
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.application_state.application_state import ApplicationState
from lemma.document.document import Document
from lemma.services.message_bus import MessageBus
from lemma.services.html_parser import HTMLParser
from lemma.services.layout_info import LayoutInfo
from lemma.services.text_shaper import TextShaper
from lemma.use_cases.queries import Queries
import lemma.services.timer as timer


class UseCases():

    def settings_set_value(item, value):
        Settings.set_value(item, value)

        Settings.save()
        MessageBus.add_message(item + '_settings_changed')
        MessageBus.add_message('settings_changed')

    def toggle_tools_sidebar(name):
        if Settings.get_value('show_tools_sidebar') and Settings.get_value('tools_sidebar_active_tab') == name:
            Settings.set_value('show_tools_sidebar', False)
        else:
            Settings.set_value('show_tools_sidebar', True)
            Settings.set_value('tools_sidebar_active_tab', name)

        Settings.save()
        MessageBus.add_message('sidebar_visibility_changed')

    def open_link(link_target):
        workspace = WorkspaceRepo.get_workspace()
        new_document = None

        if urlparse(link_target).scheme in ['http', 'https']:
            webbrowser.open(link_target)

        elif link_target != None:
            target_list = DocumentRepo.list_by_title(link_target)

            if len(target_list) > 0:
                document = DocumentRepo.get_by_id(target_list[0]['id'])
                workspace.set_active_document(document, update_history=True)
            else:
                new_document = Document()
                new_document.id = DocumentRepo.get_max_document_id() + 1
                new_document.title = link_target
                new_document.update_last_modified()

                workspace.set_active_document(new_document, update_history=True)

                ApplicationState.set_scrolling_target(new_document.id, 0, 0, None)

        UseCases.__update_implicit_x_position()
        UseCases.__reset_tags_at_cursor()

        if new_document != None:
            DocumentRepo.add(new_document)
        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')
        MessageBus.add_message('new_document')
        MessageBus.add_message('history_changed')
        MessageBus.add_message('new_active_document')
        MessageBus.add_message('tags_at_cursor_changed')

    def import_markdown(path):
        document = Document()
        document.id = DocumentRepo.get_max_document_id() + 1

        with open(path, 'r') as file:
            markdown = file.read()

        markdown = markdown.replace('$`', '<math>').replace('`$', '</math>')
        mdi = MarkdownIt()
        html = mdi.render(markdown)
        html = html.replace('.md">', '">')

        title, ast = HTMLParser.parse(html, os.path.dirname(path), str(document.id) + '_files')

        if title != None:
            document.title = title
        else:
            document.title = os.path.basename(path)[:-3]

        document.ast = ast
        document.cursor.set_state([document.ast[0][0].get_position(), document.ast[0][0].get_position()])
        document.update_last_modified()

        DocumentRepo.add(document)
        MessageBus.add_message('new_document')

    def enter_draft_mode():
        workspace = WorkspaceRepo.get_workspace()

        workspace.enter_draft_mode()

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')

    def leave_draft_mode():
        workspace = WorkspaceRepo.get_workspace()

        workspace.leave_draft_mode()

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')

    def new_document(title):
        workspace = WorkspaceRepo.get_workspace()

        document = Document()
        document.id = DocumentRepo.get_max_document_id() + 1
        document.title = title
        document.update_last_modified()

        workspace.set_active_document(document, update_history=True)
        workspace.leave_draft_mode()

        ApplicationState.set_scrolling_target(document.id, 0, 0, None)
        UseCases.__update_implicit_x_position()
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.add(document)
        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')
        MessageBus.add_message('new_document')
        MessageBus.add_message('history_changed')
        MessageBus.add_message('new_active_document')
        MessageBus.add_message('tags_at_cursor_changed')

    def delete_document(document_id):
        workspace = WorkspaceRepo.get_workspace()

        document_changed = (document_id == workspace.get_active_document_id())
        if document_changed:
            new_active_document_id = workspace.get_prev_id_in_history(document_id)
            if new_active_document_id == None:
                new_active_document_id = workspace.get_next_id_in_history(document_id)

            document = DocumentRepo.get_by_id(new_active_document_id)

            workspace.set_active_document(document, update_history=False)

            ApplicationState.set_scrolling_target(document.id, 0, 0, None)
            UseCases.__update_implicit_x_position()
            UseCases.__reset_tags_at_cursor()

        workspace.remove_from_history(document_id)
        workspace.unbookmark_document(document_id)

        DocumentRepo.delete(document_id)
        WorkspaceRepo.update(workspace)
        MessageBus.add_message('document_removed')
        MessageBus.add_message('history_changed')
        MessageBus.add_message('document_changed')
        MessageBus.add_message('bookmarks_changed')
        if document_changed:
            MessageBus.add_message('new_active_document')
        MessageBus.add_message('tags_at_cursor_changed')

    def set_active_document(document_id, update_history=True):
        workspace = WorkspaceRepo.get_workspace()

        if document_id != workspace.get_active_document_id():
            document = DocumentRepo.get_by_id(document_id)
        else:
            document = workspace.get_active_document()
        workspace.set_active_document(document, update_history)

        if update_history:
            ApplicationState.set_scrolling_target(document.id, 0, 0, None)
        else:
            pos = ApplicationState.get_scrolling_position(document.id)
            if pos != None:
                ApplicationState.set_scrolling_target(document.id, pos[0], pos[1], None)
            else:
                ApplicationState.set_scrolling_target(document.id, 0, 0, None)
        UseCases.__update_implicit_x_position()
        UseCases.__reset_tags_at_cursor()

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')
        if update_history:
            MessageBus.add_message('history_changed')
        MessageBus.add_message('new_active_document')
        MessageBus.add_message('tags_at_cursor_changed')

    def bookmark_document(document_id):
        workspace = WorkspaceRepo.get_workspace()

        workspace.bookmark_document(document_id)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('bookmarks_changed')

    def unbookmark_document(document_id):
        workspace = WorkspaceRepo.get_workspace()

        workspace.unbookmark_document(document_id)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('bookmarks_changed')

    def move_bookmark(document_id, new_position):
        workspace = WorkspaceRepo.get_workspace()

        workspace.move_bookmark(document_id, new_position)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('bookmarks_changed')

    @timer.timer
    def undo():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.undo()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('undo_executed')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def redo():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.redo()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('redo_executed')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def set_title(title):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.set_title(title)

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_title_changed')

    @timer.timer
    def im_commit(text):
        document = WorkspaceRepo.get_workspace().get_active_document()
        tags = ApplicationState.get_tags_at_cursor()

        link_at_cursor = document.get_link_at_cursor()
        xml = xml_helpers.embellish_with_link_and_tags(xml_helpers.escape(text), link_at_cursor, tags.copy())
        title, paragraphs = XMLParser.parse(xml)

        document.start_undoable_action()
        document.delete_selected_nodes()
        document.insert_nodes(paragraphs[0].children)
        if not document.has_selection() and text.isspace():
            document.replace_max_string_before_cursor()
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def add_newline():
        document = WorkspaceRepo.get_workspace().get_active_document()
        tags = ApplicationState.get_tags_at_cursor()

        document.start_undoable_action()
        document.delete_selected_nodes()

        insert_paragraph = document.get_insert_node().paragraph()
        paragraph_style = insert_paragraph.style
        indentation_level = insert_paragraph.indentation_level

        node = Node('eol')
        node.tags = tags.copy()
        node.link = document.get_link_at_cursor()
        document.insert_nodes([node])

        if paragraph_style in ['ul', 'ol', 'cl']:
            paragraph = document.get_insert_node().paragraph()
            document.set_paragraph_style(paragraph, paragraph_style)
            if indentation_level != 0:
                document.set_indentation_level(document.get_insert_node().paragraph(), indentation_level)
        elif paragraph_style.startswith('h'):
            if len(document.get_insert_node().paragraph()) == 1:
                paragraph = document.get_insert_node().paragraph()
                document.set_paragraph_style(paragraph, 'p')

        document.replace_max_string_before_cursor()
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def insert_text(text):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.delete_selected_nodes()
        for line in text.splitlines(keepends=True):
            xml = xml_helpers.escape(line)
            xml = RegexService.get_regex(r'((?:http://|https://)[a-zA-Z0-9\.\/\&\?=\-_#]*)').sub(r'<a href="\1">\1</a>', xml)

            title, paragraphs = XMLParser.parse(xml)
            paragraph = paragraphs[0]

            insert_node = document.get_insert_node()
            if insert_node.parent.type == 'paragraph' and insert_node.is_first_in_parent() and paragraph[-1].type == 'eol':
                document.insert_paragraph(paragraph, document.ast.index(insert_node.paragraph()))
            else:
                document.insert_nodes(paragraph.children)
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    def replace_section(document, node_from, node_to, xml):
        nodes = []
        title, paragraphs = XMLParser.parse(xml)
        for paragraph in paragraphs:
            nodes += paragraph.children

        document.start_undoable_action()
        document.delete_nodes(node_from, node_to)
        document.insert_nodes(nodes, node_to)
        document.set_insert_and_selection_node(node_to)
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def insert_xml(xml):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection() and xml.find('<placeholder marks="prev_selection"/>') >= 0:
            if not document.has_multiple_lines_selected():
                prev_selection = document.get_selected_nodes()
                prev_selection_xml = xml_exporter.XMLExporter.export_paragraph(prev_selection)
                xml = xml.replace('<placeholder marks="prev_selection"/>', prev_selection_xml[prev_selection_xml.find('>') + 1:prev_selection_xml.rfind('<')])

        title, paragraphs = XMLParser.parse(xml)

        document.start_undoable_action()
        document.delete_selected_nodes()

        insert_position = document.get_insert_node().get_position()
        for paragraph in paragraphs:
            for node in paragraph:
                if node.type == 'widget':
                    for filename in node.value.get_filenames():
                        origin = os.path.join(Files.get_documents_folder(), filename)
                        new_name = Files.add_file_to_doc_folder_with_distinct_name(document, origin)
                        node.value.change_filename(filename, new_name)

            insert_node = document.get_insert_node()
            if insert_node.is_first_in_parent() and paragraph[-1].type == 'eol':
                document.insert_paragraph(paragraph, document.ast.index(insert_node.paragraph()))
            else:
                document.insert_nodes(paragraph.children)

        document.select_placeholder_in_range(document.get_node_at_position(insert_position), document.get_insert_node())
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def backspace():
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        if document.has_selection():
            document.delete_selected_nodes()
        elif not insert.is_first_in_parent():
            document.delete_nodes(insert.prev_in_parent(), insert)
        elif insert.parent.type == 'paragraph' and not insert.parent.is_first_in_parent():
            document.delete_nodes(insert.prev_no_descent(), insert)
        elif insert.parent.type != 'paragraph' and len(insert.parent) == 1:
            document.set_insert_and_selection_node(insert.prev_no_descent(), insert)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def delete():
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        if document.has_selection():
            document.delete_selected_nodes()
        elif not insert.is_last_in_parent():
            document.delete_nodes(insert, insert.next_in_parent())
        elif insert.parent.type == 'paragraph' and not insert.parent.is_last_in_parent():
            document.delete_nodes(insert, insert.next())
        elif insert.parent.type != 'paragraph' and len(insert.parent) == 1:
            document.set_insert_and_selection_node(insert.next_no_descent(), insert)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def delete_section(node_from, node_to):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.delete_nodes(node_from, node_to)
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def delete_selection():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.delete_selected_nodes()
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    def add_widget(widget):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if not document.insert_parent_is_root(): return

        document.start_undoable_action()
        document.delete_selected_nodes()
        node = Node('widget', widget)
        document.insert_nodes([node])
        document.end_undoable_action()

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def resize_widget(new_width):
        document = WorkspaceRepo.get_workspace().get_active_document()
        selected_nodes = document.get_selected_nodes()

        document.resize_widget(selected_nodes[0], new_width)

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def set_widget_attribute_filename(key, value):
        document = WorkspaceRepo.get_workspace().get_active_document()
        selected_nodes = document.get_selected_nodes()

        Files.change_document_file_name(selected_nodes[0].value.get_attribute(key), value)
        document.set_widget_attribute(selected_nodes[0], key, value)

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def set_link(document, bounds, target):
        document.start_undoable_action()
        document.set_link(bounds, target)
        document.set_insert_and_selection_node(bounds[1])
        document.end_undoable_action()

        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def set_paragraph_style(style):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection():
            first_paragraph = document.get_first_selection_bound().paragraph()
            last_paragraph = document.get_last_selection_bound().prev().paragraph()

            paragraph_nos = range(document.ast.index(first_paragraph), document.ast.index(last_paragraph) + 1)
            paragraphs = []
            for paragraph_no in paragraph_nos:
                paragraphs.append(document.ast[paragraph_no])
        else:
            paragraphs = [document.get_insert_node().paragraph()]

        document.start_undoable_action()
        for paragraph in paragraphs:
            document.set_paragraph_style(paragraph, style)
        document.end_undoable_action()

        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def toggle_checkbox_at_cursor():
        document = WorkspaceRepo.get_workspace().get_active_document()

        paragraph = document.get_insert_node().paragraph()
        new_state = 'checked' if paragraph.state == None else None
        document.set_paragraph_state(paragraph, new_state)

        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def toggle_tag(tagname):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection():
            has_untagged_nodes_in_selection = any((tagname not in node.tags) for node in document.get_selected_nodes())

            if has_untagged_nodes_in_selection:
                document.add_tag(tagname)
            else:
                document.remove_tag(tagname)

            UseCases.__reset_tags_at_cursor()

            DocumentRepo.update(document)
            MessageBus.add_message('document_changed')
            MessageBus.add_message('document_ast_changed')
            MessageBus.add_message('document_ast_or_cursor_changed')
            MessageBus.add_message('tags_at_cursor_changed')

        else:
            ApplicationState.toggle_tag_at_cursor(tagname)

            MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def set_indentation_level(indentation_level):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.set_indentation_level(document.get_insert_node().paragraph(), indentation_level)
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def change_indentation_level(difference):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection():
            first_paragraph = document.get_first_selection_bound().paragraph()
            last_paragraph = document.get_last_selection_bound().prev().paragraph()

            paragraph_nos = range(document.ast.index(first_paragraph), document.ast.index(last_paragraph) + 1)
            paragraphs = []
            for paragraph_no in paragraph_nos:
                paragraphs.append(document.ast[paragraph_no])
        else:
            paragraphs = [document.get_insert_node().paragraph()]

        document.start_undoable_action()
        for paragraph in paragraphs:
            new_level = max(0, min(4, paragraph.indentation_level + difference))
            document.set_indentation_level(paragraph, new_level)
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def left(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        selection = document.get_selection_node()

        if do_selection:
            new_insert = insert.prev_no_descent()
            if new_insert != None:
                document.set_insert_and_selection_node(new_insert, selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_first_selection_bound(), document.get_first_selection_bound())
        else:
            next_insert = insert.prev()
            if next_insert != None:
                document.set_insert_and_selection_node(next_insert, next_insert)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def jump_left(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selection = document.get_selection_node()
        original_insert = document.get_insert_node()
        insert = original_insert
        prev_insert = insert.prev_no_descent()
        while prev_insert != None and NodeTypeDB.is_whitespace(prev_insert):
            insert = prev_insert
            prev_insert = insert.prev_no_descent()

        if prev_insert != None:
            insert_new = insert.prev_no_descent().word_bounds()[0]
        else:
            insert_new = insert

        if do_selection:
            document.set_insert_and_selection_node(insert_new, selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_first_selection_bound(), document.get_first_selection_bound())
        else:
            document.set_insert_and_selection_node(insert_new, insert_new)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def right(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        selection = document.get_selection_node()

        if do_selection:
            new_insert = insert.next_no_descent()
            if new_insert != None:
                document.set_insert_and_selection_node(new_insert, selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_last_selection_bound(), document.get_last_selection_bound())
        else:
            next_insert = insert.next()
            if next_insert != None:
                document.set_insert_and_selection_node(next_insert, next_insert)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def jump_right(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selection = document.get_selection_node()
        original_insert = document.get_insert_node()
        insert = original_insert
        while NodeTypeDB.is_whitespace(insert):
            next_insert = insert.next_no_descent()
            if next_insert == None:
                break
            insert = next_insert

        if not NodeTypeDB.is_whitespace(insert):
            insert_new = insert.word_bounds()[1]
        else:
            insert_new = insert

        if do_selection:
            document.set_insert_and_selection_node(insert_new, selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_last_selection_bound(), document.get_last_selection_bound())
        else:
            document.set_insert_and_selection_node(insert_new, insert_new)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def up(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
        insert = document.get_insert_node()

        x, y = document_layout.get_absolute_xy(document_layout.get_node_layout(insert))
        implicit_x_position = ApplicationState.get_implicit_x_position()
        if implicit_x_position != None:
            x = implicit_x_position

        new_node = None
        ancestors = document_layout.get_ancestors(document_layout.get_node_layout(insert))
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][:j]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast:
                        for hbox in document_layout.get_paragraph_layout(paragraph)['children']:
                            if hbox['y'] + hbox['parent']['y'] < ancestors[i - 1]['y'] + ancestors[i - 1]['parent']['y']:
                                prev_hboxes.append(hbox)
                for hbox in reversed(prev_hboxes):
                    if new_node == None:
                        min_distance = 10000
                        for hbox_child in hbox['children']:
                            layout_x, layout_y = document_layout.get_absolute_xy(hbox_child)
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = hbox_child['node']
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[0][0]

        if do_selection:
            document.set_insert_and_selection_node(new_node, document.get_selection_node())
        else:
            document.set_insert_and_selection_node(new_node, new_node)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def down(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
        insert = document.get_insert_node()
        layout = document_layout.get_node_layout(insert)

        x, y = document_layout.get_absolute_xy(layout)
        implicit_x_position = ApplicationState.get_implicit_x_position()
        if implicit_x_position != None:
            x = implicit_x_position

        new_node = None
        ancestors = document_layout.get_ancestors(layout)
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][j + 1:]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast:
                        for hbox in document_layout.get_paragraph_layout(paragraph)['children']:
                            if hbox['y'] + hbox['parent']['y'] > ancestors[i - 1]['y'] + ancestors[i - 1]['parent']['y']:
                                prev_hboxes.append(hbox)
                for child in prev_hboxes:
                    if new_node == None:
                        min_distance = 10000
                        for child_layout in child['children']:
                            layout_x, layout_y = document_layout.get_absolute_xy(child_layout)
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = child_layout['node']
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[-1][-1]

        if do_selection:
            document.set_insert_and_selection_node(new_node, document.get_selection_node())
        else:
            document.set_insert_and_selection_node(new_node, new_node)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def paragraph_start(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
        insert = document.get_insert_node()

        layout = document_layout.get_node_layout(insert)
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][0]['node'] == None:
            layout = layout['children'][0]
        new_node = layout['children'][0]['node']

        if do_selection:
            document.set_insert_and_selection_node(new_node, document.get_selection_node())
        else:
            document.set_insert_and_selection_node(new_node, new_node)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def paragraph_end(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
        insert = document.get_insert_node()

        layout = document_layout.get_node_layout(insert)
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][-1]['node'] == None:
            layout = layout['children'][-1]
        new_node = layout['children'][-1]['node']

        if do_selection:
            document.set_insert_and_selection_node(new_node, document.get_selection_node())
        else:
            document.set_insert_and_selection_node(new_node, new_node)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def page(y, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        insert = document.get_insert_node()
        orig_x, orig_y = document_layout.get_absolute_xy(document_layout.get_node_layout(insert))
        implicit_x_position = ApplicationState.get_implicit_x_position()
        if implicit_x_position != None:
            orig_x = implicit_x_position
        new_x = orig_x
        new_y = orig_y + y
        layout = document_layout.get_cursor_holding_layout_close_to_xy(new_x, new_y)

        if do_selection:
            document.set_insert_and_selection_node(layout['node'], document.get_selection_node())
        else:
            document.set_insert_and_selection_node(layout['node'], layout['node'])

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def select_next_placeholder():
        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.get_selected_nodes()
        node = document.get_first_selection_bound()
        start_node = node

        if len(selected_nodes) == 1 and selected_nodes[0].type == 'placeholder':
            node = node.next()

        while node != None and not node.type == 'placeholder':
            if node == document.ast[-1][-1]:
                node = document.ast[0][0]
            else:
                node = node.next()
            if node == start_node:
                break

        if node != None and node.type == 'placeholder':
            document.select_node(node)

            UseCases.__scroll_insert_on_screen(document, animation_type='default')
            UseCases.__reset_tags_at_cursor()

            DocumentRepo.update(document)
            MessageBus.add_message('document_changed')
            MessageBus.add_message('document_ast_or_cursor_changed')
            MessageBus.add_message('cursor_movement')
            MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def select_prev_placeholder():
        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.get_selected_nodes()
        node = document.get_first_selection_bound()
        start_node = node

        while node != None and not node.type == 'placeholder':
            if node == document.ast[0][0]:
                node = document.ast[-1][-1]
            else:
                node = node.prev()
            if node == start_node:
                break

        if node != None and node.type == 'placeholder':
            document.select_node(node)

            UseCases.__scroll_insert_on_screen(document, animation_type='default')
            UseCases.__reset_tags_at_cursor()

            DocumentRepo.update(document)
            MessageBus.add_message('document_changed')
            MessageBus.add_message('document_ast_or_cursor_changed')
            MessageBus.add_message('cursor_movement')
            MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def select_node(node):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.select_node(node)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def select_section(node_from, node_to):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.set_insert_and_selection_node(node_from, node_to)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def select_all():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.set_insert_and_selection_node(document.ast[0][0], document.ast[-1][-1])

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def remove_selection():
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection():
            document.set_insert_and_selection_node(document.get_last_selection_bound())

            UseCases.__scroll_insert_on_screen(document, animation_type='default')
            UseCases.__reset_tags_at_cursor()

            DocumentRepo.update(document)
            MessageBus.add_message('document_changed')
            MessageBus.add_message('document_ast_or_cursor_changed')
            MessageBus.add_message('cursor_movement')
            MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def move_cursor_to_xy(x, y, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        layout = document_layout.get_cursor_holding_layout_close_to_xy(x, y)
        if do_selection:
            document.set_insert_and_selection_node(layout['node'], document.get_selection_node())
        else:
            document.set_insert_and_selection_node(layout['node'], layout['node'])
        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def move_cursor_to_node(node):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.set_insert_and_selection_node(node, node)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def move_cursor_to_parent():
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        new_insert = None
        for ancestor in reversed(insert.ancestors()):
            if NodeTypeDB.can_hold_cursor(ancestor):
                new_insert = ancestor
                break

        if new_insert != None:
            document.set_insert_and_selection_node(new_insert, new_insert)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def extend_selection():
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        selection = document.get_selection_node()

        word_start, word_end = document.get_insert_node().word_bounds()
        if word_start != None and word_end != None and (document.get_first_selection_bound().get_position() > word_start.get_position() or document.get_last_selection_bound().get_position() < word_end.get_position()):
            new_insert = word_end
            new_selection = word_start

        else:
            for ancestor in reversed(insert.ancestors()):
                if NodeTypeDB.can_hold_cursor(ancestor):
                    new_insert = ancestor
                    new_selection = document.get_selection_node()
                    break

                if ancestor.type == 'mathlist':
                    if insert == ancestor[0] and selection == ancestor[-1]: continue
                    if insert == ancestor[-1] and selection == ancestor[0]: continue
                    new_insert = ancestor[-1]
                    new_selection = ancestor[0]
                    break

                if ancestor.type == 'root':
                    paragraph_start, paragraph_end = document.get_insert_node().paragraph_bounds()
                    if paragraph_start != None and paragraph_end != None and (document.get_first_selection_bound().get_position() > paragraph_start.get_position() or document.get_last_selection_bound().get_position() < paragraph_end.get_position()):
                        new_insert = paragraph_end
                        new_selection = paragraph_start
                    else:
                        new_insert = document.ast[0][0]
                        new_selection = document.ast[-1][-1]

        document.set_insert_and_selection_node(new_insert, new_selection)

        UseCases.__scroll_insert_on_screen(document, animation_type='default')
        UseCases.__reset_tags_at_cursor()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    def set_frame_time(time):
        ApplicationState.set_frame_time(time)

    def set_view_size(width, height):
        ApplicationState.set_view_size(width, height)

    def set_title_buttons_height(height):
        ApplicationState.set_title_buttons_height(height)

    def set_dark_mode(is_dark):
        ApplicationState.set_dark_mode(is_dark)

        MessageBus.add_message('dark_mode_changed')

    def set_ctrl_pressed(is_pressed):
        ApplicationState.set_ctrl_pressed(is_pressed)

    @timer.timer
    def set_preedit(preedit_string):
        document = WorkspaceRepo.get_workspace().get_active_document()

        ApplicationState.set_preedit(preedit_string)
        UseCases.__scroll_insert_on_screen(document, 'default')

        MessageBus.add_message('preedit_changed')
        MessageBus.add_message('cursor_movement')
        MessageBus.add_message('tags_at_cursor_changed')

    @timer.timer
    def update_implicit_x_position():
        UseCases.__update_implicit_x_position()

    @timer.timer
    def scroll_to_xy(x, y, animation_type='default'):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        ApplicationState.set_scrolling_target(document.id, x, y, animation_type)

    @timer.timer
    def scroll_insert_on_screen(animation_type='default'):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        UseCases.__scroll_insert_on_screen(document, animation_type)

    @timer.timer
    def decelerate(vel_x, vel_y):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        view_width, view_height = ApplicationState.get_view_size()
        x, y = Queries.get_current_scrolling_offsets()

        max_y = max(0, LayoutInfo.get_normal_document_offset() + ApplicationState.get_title_buttons_height() + document_layout.get_height() + LayoutInfo.get_document_padding_bottom() - view_height)
        max_x = max(0, LayoutInfo.get_document_padding_left() + document_layout.get_width() - view_width)

        vel_x *= 0.4
        vel_y *= 0.4
        x = x + 15.13 / 16 * vel_x
        y = y + 15.13 / 16 * vel_y

        ApplicationState.set_scrolling_target(document.id, x, y, 'decelerate')

    def show_dialog(name, argument=None):
        ApplicationState.schedule_dialog_display(name, argument)

        MessageBus.add_message('dialog_display_scheduled')

    def show_popover(name, x, y, orientation='bottom'):
        ApplicationState.set_popover(name, x, y, orientation)

        MessageBus.add_message('popover_changed')

    def show_popover_at_node(name, document, node, offset_x, offset_y):
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()
        view_width, view_height = ApplicationState.get_view_size()

        x, y = document_layout.get_absolute_xy(document_layout.get_node_layout(node))
        x += LayoutInfo.get_document_padding_left() + offset_x - scrolling_pos_x
        y += LayoutInfo.get_normal_document_offset() + offset_y - scrolling_pos_y
        fontname = document_layout.get_node_layout(node)['fontname']
        padding_top = TextShaper.get_padding_top(fontname)
        padding_bottom = TextShaper.get_padding_bottom(fontname)
        y += document_layout.get_node_layout(node)['height'] - padding_top - padding_bottom
        x += document_layout.get_node_layout(node)['width'] / 2

        orientation = 'bottom'
        if y + 260 > view_height:
            orientation = 'top'
            y -= document_layout.get_node_layout(node)['height'] - padding_top - padding_bottom

        ApplicationState.set_popover(name, x, y, orientation)

        MessageBus.add_message('popover_changed')

    def hide_popovers():
        ApplicationState.set_popover(None)

        MessageBus.add_message('popover_changed')

    def __scroll_insert_on_screen(document, animation_type='default'):
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))

        window_height = ApplicationState.view_height
        insert_node = document.get_insert_node()
        insert_position = document_layout.get_absolute_xy(document_layout.get_node_layout(insert_node))

        content_offset = LayoutInfo.get_normal_document_offset()
        insert_y = insert_position[1] + content_offset
        insert_height = document_layout.get_node_layout(insert_node)['height']
        scrolling_offset_y = Queries.get_current_scrolling_offsets()[1]
        content_height = document_layout.get_height() + LayoutInfo.get_document_padding_bottom() + LayoutInfo.get_normal_document_offset() + ApplicationState.title_buttons_height

        if window_height <= 0:
            new_position = (0, 0)
        elif document_layout.get_absolute_xy(document_layout.get_line_layout_at_y(insert_position[1]))[1] == 0:
            new_position = (0, 0)
        elif insert_y < scrolling_offset_y:
            if insert_height > window_height:
                new_position = (0, insert_y - window_height + insert_height)
            else:
                new_position = (0, insert_y)
        elif insert_position[1] >= document_layout.get_height() - insert_height and content_height >= window_height:
            new_position = (0, document_layout.get_height() + content_offset + LayoutInfo.get_document_padding_bottom() - window_height)
        elif insert_y > scrolling_offset_y - insert_height + window_height:
            new_position = (0, insert_y - window_height + insert_height)
        else:
            new_position = (ApplicationState.scrolling_target_x, ApplicationState.scrolling_target_y)

        ApplicationState.set_scrolling_target(document.id, new_position[0], new_position[1], animation_type)

    def __update_implicit_x_position():
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            value = 0
        else:
            document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
            insert = document.get_insert_node()
            value = document_layout.get_absolute_xy(document_layout.get_node_layout(insert))[0]

        ApplicationState.set_implicit_x_position(value)

    def __reset_tags_at_cursor():
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document == None:
            tags_at_cursor = set()
        else:
            node = document.get_insert_node()

            if node.parent.type == 'paragraph':
                prev_node = node.prev_no_descent()
            else:
                prev_node = node.prev_in_parent()

            if node == None or prev_node == None:
                tags_at_cursor = set()
            else:
                tags_at_cursor = prev_node.tags.copy()

        ApplicationState.set_tags_at_cursor(tags_at_cursor)


