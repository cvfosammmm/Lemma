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
import lemma.services.xml_parser as xml_parser
import lemma.services.xml_exporter as xml_exporter
from lemma.services.settings import Settings
from lemma.application_state.application_state import ApplicationState
from lemma.services.layout_info import LayoutInfo
from lemma.services.node_type_db import NodeTypeDB
from lemma.document.ast import Node
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.document.document import Document
from lemma.services.message_bus import MessageBus
from lemma.services.html_parser import HTMLParser
from lemma.services.text_shaper import TextShaper
import lemma.services.timer as timer


class UseCases():

    def settings_set_value(item, value):
        Settings.set_value(item, value)

        Settings.save()
        MessageBus.add_message('settings_changed')

    def app_state_set_value(item, value):
        ApplicationState.set_value(item, value)

        MessageBus.add_message('app_state_changed')

    def app_state_set_values(values):
        for key, value in values.items():
            ApplicationState.set_value(key, value)

        MessageBus.add_message('app_state_changed')

    def show_link_popover(main_window):
        document = WorkspaceRepo.get_workspace().get_active_document()
        scrolling_position_x, scrolling_position_y = document.get_current_scrolling_offsets()

        insert = document.get_insert_node()
        x, y = document.get_absolute_xy(insert.layout)
        x -= scrolling_position_x
        y -= scrolling_position_y
        document_view = main_window.document_view
        document_view_allocation = document_view.compute_bounds(main_window).out_bounds
        x += document_view_allocation.origin.x
        y += document_view_allocation.origin.y
        x += LayoutInfo.get_document_padding_left()
        y += LayoutInfo.get_normal_document_offset()
        fontname = insert.layout['fontname']
        padding_top = TextShaper.get_padding_top(fontname)
        padding_bottom = TextShaper.get_padding_bottom(fontname)
        y += insert.layout['height'] - padding_top - padding_bottom

        orientation = 'bottom'
        if y + 260 > document_view_allocation.size.height:
            orientation = 'top'
            y -= insert.layout['height'] - padding_top - padding_bottom

        if not document.has_selection() and insert.is_inside_link():
            document.set_insert_and_selection_node(*insert.link_bounds())

        ApplicationState.set_value('active_popover', 'link_autocomplete')
        ApplicationState.set_value('popover_position', (x, y))
        ApplicationState.set_value('popover_orientation', orientation)

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('app_state_changed')

    def show_popover(name, x, y, orientation='bottom'):
        ApplicationState.set_value('active_popover', name)
        ApplicationState.set_value('popover_position', (x, y))
        ApplicationState.set_value('popover_orientation', orientation)

        MessageBus.add_message('app_state_changed')

    def hide_popovers():
        ApplicationState.set_value('active_popover', None)
        ApplicationState.set_value('popover_position', (0, 0))

        MessageBus.add_message('app_state_changed')

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
                document.scroll_to_xy(0, 0, animation_type=None)

                workspace.set_active_document(document, update_history=True)
            else:
                new_document = Document()
                new_document.id = DocumentRepo.get_max_document_id() + 1
                new_document.title = link_target
                new_document.update_last_modified()
                new_document.update()

                workspace.set_active_document(new_document, update_history=True)

        if new_document != None:
            DocumentRepo.add(new_document)
        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')
        MessageBus.add_message('new_document')
        MessageBus.add_message('history_changed')

    def import_markdown(path):
        document = Document()
        document.id = DocumentRepo.get_max_document_id() + 1

        with open(path, 'r') as file:
            markdown = file.read()

        markdown = markdown.replace('$`', '<math>').replace('`$', '</math>')
        mdi = MarkdownIt()
        html = mdi.render(markdown)
        html = html.replace('.md">', '">')

        parser = HTMLParser(html, os.path.dirname(path))
        parser.run()

        if parser.title != None:
            document.title = parser.title
        else:
            document.title = os.path.basename(path)[:-3]

        document.ast = parser.root
        document.cursor.set_state([document.ast[0][0].get_position(), document.ast[0][0].get_position()])
        document.update_last_modified()
        document.update()

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
        document.update()

        workspace.set_active_document(document, update_history=True)
        workspace.leave_draft_mode()

        DocumentRepo.add(document)
        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')
        MessageBus.add_message('new_document')
        MessageBus.add_message('history_changed')

    def delete_document(document_id):
        workspace = WorkspaceRepo.get_workspace()

        if document_id == workspace.get_active_document_id():
            new_active_document_id = workspace.get_prev_id_in_history(document_id)
            if new_active_document_id == None:
                new_active_document_id = workspace.get_next_id_in_history(document_id)

            document = DocumentRepo.get_by_id(new_active_document_id)
            workspace.set_active_document(document, update_history=False)

        workspace.remove_from_history(document_id)
        workspace.unpin_document(document_id)

        DocumentRepo.delete(document_id)
        WorkspaceRepo.update(workspace)
        MessageBus.add_message('document_removed')
        MessageBus.add_message('history_changed')
        MessageBus.add_message('document_changed')
        MessageBus.add_message('pinned_documents_changed')

    def set_active_document(document_id, update_history=True):
        workspace = WorkspaceRepo.get_workspace()

        if document_id != workspace.get_active_document_id():
            document = DocumentRepo.get_by_id(document_id)
        else:
            document = workspace.get_active_document()
        workspace.set_active_document(document, update_history)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('mode_set')
        MessageBus.add_message('history_changed')

    def pin_document(document_id):
        workspace = WorkspaceRepo.get_workspace()

        workspace.pin_document(document_id)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('pinned_documents_changed')

    def unpin_document(document_id):
        workspace = WorkspaceRepo.get_workspace()

        workspace.unpin_document(document_id)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('pinned_documents_changed')

    def set_pinned_document_icon(document_id, icon_name=None):
        workspace = WorkspaceRepo.get_workspace()

        workspace.set_pinned_document_icon(document_id, icon_name)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('pinned_documents_changed')

    def move_document_pin(document_id, new_position):
        workspace = WorkspaceRepo.get_workspace()

        workspace.move_document_pin(document_id, new_position)

        WorkspaceRepo.update(workspace)
        MessageBus.add_message('pinned_documents_changed')

    @timer.timer
    def undo():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.undo()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def redo():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.redo()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def set_title(title):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.title = title
        document.update_last_modified()
        document.update()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_title_changed')

    @timer.timer
    def im_commit(text):
        document = WorkspaceRepo.get_workspace().get_active_document()

        tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
        link_at_cursor = ApplicationState.get_value('link_at_cursor')
        xml = xml_helpers.embellish_with_link_and_tags(xml_helpers.escape(text), link_at_cursor, tags_at_cursor)
        parser = xml_parser.XMLParser()
        paragraphs = parser.parse(xml)

        document.start_undoable_action()
        document.delete_selected_nodes()
        document.insert_nodes(paragraphs[0].children)
        if not document.has_selection() and text.isspace():
            document.replace_max_string_before_cursor()
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
        document.update_implicit_x_position()
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')
        MessageBus.add_message('keyboard_input')

    def replace_section(document, node_from, node_to, xml):
        parser = xml_parser.XMLParser()

        nodes = []
        paragraphs = parser.parse(xml)
        for paragraph in paragraphs:
            nodes += paragraph.children

        document.start_undoable_action()
        document.delete_nodes(node_from, node_to)
        document.insert_nodes(nodes, node_to)
        document.set_insert_and_selection_node(node_to)
        document.update_implicit_x_position()
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def insert_xml(xml):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection() and xml.find('<placeholder marks="prev_selection"/>') >= 0:
            if not document.has_multiple_lines_selected():
                prev_selection = document.get_selected_nodes()
                prev_selection_xml = xml_exporter.XMLExporter.export_paragraph(prev_selection)
                xml = xml.replace('<placeholder marks="prev_selection"/>', prev_selection_xml[prev_selection_xml.find('>') + 1:prev_selection_xml.rfind('<')])

        parser = xml_parser.XMLParser()
        paragraphs = parser.parse(xml)

        document.start_undoable_action()
        document.delete_selected_nodes()

        for paragraph in paragraphs:
            insert_node = document.get_insert_node()
            if insert_node.is_first_in_parent() and paragraph[-1].type == 'eol':
                document.insert_paragraph(paragraph)
            else:
                document.insert_nodes(paragraph.children)

        document.select_placeholder_in_range(paragraphs[0][0], document.get_insert_node())
        document.update_implicit_x_position()
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def add_newline():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.delete_selected_nodes()

        insert_paragraph = document.get_insert_node().paragraph()
        paragraph_style = insert_paragraph.style
        indentation_level = insert_paragraph.indentation_level

        document.insert_nodes([Node('eol')])

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
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def backspace():
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        document.start_undoable_action()
        if document.has_selection():
            document.delete_selected_nodes()
        elif not insert.is_first_in_parent() or (insert.parent.type == 'paragraph' and not insert.parent.is_first_in_parent()):
            document.delete_nodes(insert.prev_no_descent(), insert)
        elif len(insert.parent) == 1:
            document.set_insert_and_selection_node(insert.prev_no_descent(), insert)
        document.update_implicit_x_position()
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def delete():
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        document.start_undoable_action()
        if document.has_selection():
            document.delete_selected_nodes()
        elif not insert.is_last_in_parent() or (insert.parent.type == 'paragraph' and not insert.parent.is_last_in_parent()):
            insert_new = insert.next_no_descent()
            document.delete_nodes(insert, insert_new)
        elif len(insert.parent) == 1:
            document.set_insert_and_selection_node(insert.next_no_descent(), insert)
        document.update_implicit_x_position()
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def delete_selection():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.delete_selected_nodes()
        document.update_implicit_x_position()
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    def add_image(image):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.delete_selected_nodes()
        node = Node('widget', image)
        document.insert_nodes([node])
        document.update_implicit_x_position()
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
        document.end_undoable_action()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def resize_widget(new_width):
        document = WorkspaceRepo.get_workspace().get_active_document()
        selected_nodes = document.get_selected_nodes()

        if len(selected_nodes) == 1 and selected_nodes[0].type == 'widget' and selected_nodes[0].value.is_resizable():
            document.resize_widget(selected_nodes[0], new_width)

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

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

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

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def toggle_checkbox_at_cursor():
        document = WorkspaceRepo.get_workspace().get_active_document()

        paragraph = document.get_insert_node().paragraph()
        new_state = 'checked' if paragraph.state == None else None
        document.set_paragraph_state(paragraph, new_state)

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def toggle_tag(tagname):
        document = WorkspaceRepo.get_workspace().get_active_document()

        has_char_nodes = any(node.type == 'char' for node in document.get_selected_nodes())
        has_untagged_char_nodes = any(node.type == 'char' and (tagname not in node.tags) for node in document.get_selected_nodes())

        if has_char_nodes:
            if has_untagged_char_nodes:
                document.add_tag(tagname)
            else:
                document.remove_tag(tagname)

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def set_indentation_level(indentation_level):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.start_undoable_action()
        document.set_indentation_level(document.get_insert_node().paragraph(), indentation_level)
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
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
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')
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
            document.set_insert_and_selection_node(insert.prev_no_descent(), selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_first_selection_bound())
        else:
            document.set_insert_and_selection_node(insert.prev())
        document.update_implicit_x_position()
        if insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def jump_left(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selection = document.get_selection_node()
        original_insert = document.get_insert_node()
        insert = original_insert
        while NodeTypeDB.is_whitespace(insert.prev_no_descent()):
            if insert == insert.prev_no_descent():
                break
            insert = insert.prev_no_descent()

        if not NodeTypeDB.is_whitespace(insert.prev_no_descent()):
            insert_new = insert.prev_no_descent().word_bounds()[0]
        else:
            insert_new = insert.prev_no_descent()

        if do_selection:
            document.set_insert_and_selection_node(insert_new, selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_first_selection_bound())
        else:
            document.set_insert_and_selection_node(insert_new)
        document.update_implicit_x_position()
        if original_insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def right(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        selection = document.get_selection_node()

        if do_selection:
            document.set_insert_and_selection_node(insert.next_no_descent(), selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_last_selection_bound())
        else:
            document.set_insert_and_selection_node(insert.next())
        document.update_implicit_x_position()
        if insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def jump_right(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selection = document.get_selection_node()
        original_insert = document.get_insert_node()
        insert = original_insert
        while NodeTypeDB.is_whitespace(insert):
            if insert == insert.next_no_descent():
                break
            insert = insert.next_no_descent()

        if not NodeTypeDB.is_whitespace(insert):
            insert_new = insert.word_bounds()[1]
        else:
            insert_new = insert

        if do_selection:
            document.set_insert_and_selection_node(insert_new, selection)
        elif document.has_selection():
            document.set_insert_and_selection_node(document.get_last_selection_bound())
        else:
            document.set_insert_and_selection_node(insert_new)
        document.update_implicit_x_position()
        if original_insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def up(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        x, y = document.get_absolute_xy(insert.layout)
        if document.get_implicit_x_position() != None:
            x = document.get_implicit_x_position()

        new_node = None
        ancestors = document.get_ancestors(insert.layout)
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][:j]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast:
                        for hbox in paragraph.layout['children']:
                            if hbox['y'] + hbox['parent']['y'] < ancestors[i - 1]['y'] + ancestors[i - 1]['parent']['y']:
                                prev_hboxes.append(hbox)
                for hbox in reversed(prev_hboxes):
                    if new_node == None:
                        min_distance = 10000
                        for layout in hbox['children']:
                            layout_x, layout_y = document.get_absolute_xy(layout)
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = layout['node']
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[0][0]

        selection_node = document.get_selection_node()

        document.set_insert_and_selection_node(new_node, new_node if not do_selection else selection_node)
        if insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def down(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        x, y = document.get_absolute_xy(insert.layout)
        if document.get_implicit_x_position() != None:
            x = document.get_implicit_x_position()

        new_node = None
        ancestors = document.get_ancestors(insert.layout)
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][j + 1:]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast:
                        for hbox in paragraph.layout['children']:
                            if hbox['y'] + hbox['parent']['y'] > ancestors[i - 1]['y'] + ancestors[i - 1]['parent']['y']:
                                prev_hboxes.append(hbox)
                for child in prev_hboxes:
                    if new_node == None:
                        min_distance = 10000
                        for layout in child['children']:
                            layout_x, layout_y = document.get_absolute_xy(layout)
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = layout['node']
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[-1][-1]

        selection_node = document.get_selection_node()

        document.set_insert_and_selection_node(new_node, new_node if not do_selection else selection_node)
        if insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def paragraph_start(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        layout = insert.layout
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][0]['node'] == None:
            layout = layout['children'][0]
        new_node = layout['children'][0]['node']

        selection_node = document.get_selection_node()

        document.set_insert_and_selection_node(new_node, new_node if not do_selection else selection_node)
        document.update_implicit_x_position()
        if insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def paragraph_end(do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()

        layout = insert.layout
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][-1]['node'] == None:
            layout = layout['children'][-1]
        new_node = layout['children'][-1]['node']

        selection_node = document.get_selection_node()

        document.set_insert_and_selection_node(new_node, new_node if not do_selection else selection_node)
        document.update_implicit_x_position()
        if insert != document.get_insert_node():
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def page(y, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        insert = document.get_insert_node()
        orig_x, orig_y = document.get_absolute_xy(insert.layout)
        if document.get_implicit_x_position() != None:
            orig_x = document.get_implicit_x_position()
        new_x = orig_x
        new_y = orig_y + y
        layout = document.get_cursor_holding_layout_close_to_xy(new_x, new_y)

        new_insert = layout['node']
        new_selection_bound = document.get_selection_node() if do_selection else layout['node']

        document.set_insert_and_selection_node(new_insert, new_selection_bound)
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def select_next_placeholder():
        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.get_selected_nodes()
        insert = document.get_insert_node()
        node = insert

        if len(selected_nodes) == 1 and selected_nodes[0].type == 'placeholder':
            node = node.next()

        while not node.type == 'placeholder':
            if node == document.ast[-1][-1]:
                node = document.ast[0][0]
            else:
                node = node.next()
            if node == insert: break

        if node.type == 'placeholder':
            document.select_node(node)
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def select_prev_placeholder():
        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.get_selected_nodes()
        insert = document.get_insert_node()
        node = insert

        if insert.type == 'placeholder' or (len(selected_nodes) == 1 and selected_nodes[0].type == 'placeholder'):
            node = node.prev()

        while not node.type == 'placeholder':
            if node == document.ast[0][0]:
                node = document.ast[-1][-1]
            else:
                node = node.prev()
            if node == insert: break

        if node.type == 'placeholder':
            document.select_node(node)
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def select_node(node):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.select_node(node)
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def select_all():
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.set_insert_and_selection_node(document.ast[0][0], document.ast[-1][-1])
        document.update_implicit_x_position()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def remove_selection():
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection():
            document.set_insert_and_selection_node(document.get_last_selection_bound())
            document.update_implicit_x_position()
            document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    @timer.timer
    def move_cursor_to_xy(x, y, do_selection=False):
        document = WorkspaceRepo.get_workspace().get_active_document()

        document.move_cursor_to_xy(x, y, do_selection)
        document.update_implicit_x_position()

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

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
            document.update_implicit_x_position()

        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

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
        document.update_implicit_x_position()
        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type='default')

        DocumentRepo.update(document)
        MessageBus.add_message('document_changed')
        MessageBus.add_message('document_ast_or_cursor_changed')

    def scroll_insert_on_screen(animation_type='default'):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        document.scroll_insert_on_screen(ApplicationState.get_value('document_view_height'), animation_type)

        MessageBus.add_message('document_changed')

    @timer.timer
    def scroll_to_xy(x, y, animation_type='default'):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        document.scroll_to_xy(x, y, animation_type)

        MessageBus.add_message('document_changed')

    @timer.timer
    def decelerate_scrolling(x, y, vel_x, vel_y):
        document = WorkspaceRepo.get_workspace().get_active_document()
        if document == None: return

        max_y = max(0, LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height') + document.get_height() + LayoutInfo.get_document_padding_bottom() - ApplicationState.get_value('document_view_height'))
        max_x = max(0, LayoutInfo.get_document_padding_left() + document.get_width() - ApplicationState.get_value('document_view_width'))

        vel_x *= 0.4
        vel_y *= 0.4
        x = x + 15.13 / 16 * vel_x
        y = y + 15.13 / 16 * vel_y

        document.scroll_to_xy(x, y, 'decelerate')

        MessageBus.add_message('document_changed')
