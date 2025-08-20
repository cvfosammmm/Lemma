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
from markdown_it import MarkdownIt

import lemma.services.xml_helpers as xml_helpers
import lemma.services.xml_parser as xml_parser
import lemma.services.xml_exporter as xml_exporter
from lemma.services.settings import Settings
from lemma.application_state.application_state import ApplicationState
from lemma.services.character_db import CharacterDB
from lemma.services.node_type_db import NodeTypeDB
from lemma.widgets.image import Image
from lemma.document.ast import Node
from lemma.document_repo.document_repo import DocumentRepo
from lemma.history.history import History
from lemma.storage.storage import Storage
from lemma.document.document import Document
from lemma.services.message_bus import MessageBus
from lemma.services.html_parser import HTMLParser
from lemma.services.font_manager import FontManager
import lemma.services.timer as timer


class UseCases():

    def settings_set_value(item, value):
        Settings.set_value(item, value)
        Storage.save_settings()
        MessageBus.add_change_code('settings_changed')

    def app_state_set_value(item, value):
        ApplicationState.set_value(item, value)
        MessageBus.add_change_code('app_state_changed')

    def app_state_set_values(values):
        for key, value in values.items():
            ApplicationState.set_value(key, value)
        MessageBus.add_change_code('app_state_changed')

    def show_insert_link_popover(main_window):
        document = History.get_active_document()

        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        insert = document.cursor.get_insert_node()
        x, y = document.get_absolute_xy(insert.layout)
        x -= document.clipping.offset_x
        y -= document.clipping.offset_y
        document_view = main_window.document_view
        document_view_allocation = document_view.compute_bounds(main_window).out_bounds
        x += document_view_allocation.origin.x
        y += document_view_allocation.origin.y
        x += ApplicationState.get_value('document_padding_left')
        y += ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')
        fontname = FontManager.get_fontname_from_node(insert)
        padding_top = FontManager.get_padding_top(fontname)
        padding_bottom = FontManager.get_padding_bottom(fontname)
        y += insert.layout['height'] - padding_top - padding_bottom

        orientation = 'bottom'
        if y + 260 > document_view_allocation.size.height:
            orientation = 'top'
            y -= insert.layout['height'] - padding_top - padding_bottom

        if not document.cursor.has_selection() and insert.is_inside_link():
            document.add_command('move_cursor_to_node', *insert.link_bounds())
        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

        UseCases.show_popover('link_ac', x, y, orientation)

    def show_popover(name, x, y, orientation='bottom'):
        ApplicationState.set_value('active_popover', name)
        ApplicationState.set_value('popover_position', (x, y))
        ApplicationState.set_value('popover_orientation', orientation)
        MessageBus.add_change_code('app_state_changed')

    def hide_popovers():
        ApplicationState.set_value('active_popover', None)
        ApplicationState.set_value('popover_position', (0, 0))
        MessageBus.add_change_code('app_state_changed')

    def show_tools_sidebar(name):
        Settings.set_value('show_tools_sidebar', True)
        Settings.set_value('tools_sidebar_active_tab', name)
        Storage.save_settings()
        MessageBus.add_change_code('settings_changed')

    def hide_tools_sidebar():
        Settings.set_value('show_tools_sidebar', False)
        Storage.save_settings()
        MessageBus.add_change_code('settings_changed')

    def open_link(link_target):
        if urlparse(link_target).scheme in ['http', 'https']:
            webbrowser.open(link_target)
        elif link_target != None:
            target_document = DocumentRepo.get_by_title(link_target)
            if target_document != None:
                UseCases.set_active_document(target_document)
            else:
                UseCases.new_document(link_target)

    def import_markdown(path):
        document = Document()
        document.id = DocumentRepo.get_max_document_id() + 1
        document.title = os.path.basename(path)[:-3]

        with open(path, 'r') as file:
            markdown = file.read()

        if markdown.startswith('# ' + document.title):
            markdown = markdown[len(document.title) + 3:]

        markdown = markdown.replace('$`', '<math>').replace('`$', '</math>')
        mdi = MarkdownIt()
        html = mdi.render(markdown)
        html = html.replace('.md">', '">')

        parser = HTMLParser(html, os.path.dirname(path))
        parser.run()
        document.ast = parser.composite
        document.cursor.set_state([document.ast[0].get_position(), document.ast[0].get_position()])
        document.update_last_modified()
        document.update()

        DocumentRepo.add(document)
        MessageBus.add_change_code('new_document')

    def enter_draft_mode():
        ApplicationState.set_value('mode', 'draft')

        MessageBus.add_change_code('mode_set')

    def leave_draft_mode():
        ApplicationState.set_value('mode', 'documents')

        MessageBus.add_change_code('mode_set')

    def new_document(title):
        document = Document()
        document.id = DocumentRepo.get_max_document_id() + 1
        document.title = title
        document.update_last_modified()
        document.update()
        DocumentRepo.add(document)

        MessageBus.add_change_code('new_document')

        UseCases.set_active_document(document)

    def delete_document(document):
        DocumentRepo.delete(document)
        if document == History.get_active_document():
            UseCases.set_active_document(History.get_next_in_line(document))
        History.delete(document)
        Storage.save_history()

        MessageBus.add_change_code('history_changed')
        MessageBus.add_change_code('document_removed')

    def set_active_document(document, update_history=True, scroll_to_top=True):
        ApplicationState.set_value('mode', 'documents')
        if update_history and document != None:
            History.add(document)
        History.activate_document(document)
        Storage.save_history()

        MessageBus.add_change_code('mode_set')
        MessageBus.add_change_code('history_changed')

        if scroll_to_top:
            UseCases.scroll_to_xy(0, 0)

    @timer.timer
    def undo():
        document = History.get_active_document()
        document.undo()

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def redo():
        document = History.get_active_document()
        document.redo()

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def set_title(title):
        document = History.get_active_document()

        document.title = title
        document.update_last_modified()
        document.update()
        DocumentRepo.update(document)

        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    def im_commit(text):
        document = History.get_active_document()
        tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
        link_at_cursor = ApplicationState.get_value('link_at_cursor')

        xml = xml_helpers.embellish_with_link_and_tags(xml_helpers.escape(text), link_at_cursor, tags_at_cursor)
        UseCases.insert_xml(xml)

        if not document.cursor.has_selection() and text.isspace():
            UseCases.replace_max_string_before_cursor()

        MessageBus.add_change_code('keyboard_input')

    def replace_section(document, node_from, node_to, xml):
        insert = document.cursor.get_insert_node()
        parser = xml_parser.XMLParser()
        nodes = parser.parse(xml)

        commands = []
        commands.append(['delete', node_from, node_to])
        commands.append(['insert', node_to, nodes])
        commands.append(['move_cursor_to_node', node_to])
        document.add_composite_command(*commands)

        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def insert_xml(xml):
        document = History.get_active_document()
        insert = document.cursor.get_insert_node()
        insert_prev = insert.prev_in_parent()
        parser = xml_parser.XMLParser()

        if document.cursor.has_selection():
            prev_selection = document.ast.get_subtree(*document.cursor.get_state())
            prev_selection_xml = xml_exporter.XMLExporter.export(prev_selection)
            xml = xml.replace('<placeholder marks="prev_selection"/>', prev_selection_xml)

        nodes = parser.parse(xml)
        selection_from = document.cursor.get_first_node()
        selection_to = document.cursor.get_last_node()
        commands = [['delete', selection_from, selection_to], ['insert', selection_to, nodes], ['move_cursor_to_node', selection_to]]

        if len(nodes) == 0: return
        if insert_prev != None and not insert_prev.type == 'eol':
            last_node_style = nodes[-1].paragraph_style
            for node in nodes:
                node.paragraph_style = insert_prev.paragraph_style
                if node.type == 'eol':
                    if insert.type == 'eol':
                        insert.paragraph_style = last_node_style
                    break
        if not insert.type == 'eol':
            for node in reversed(nodes):
                if node.type == 'eol': break
                node.paragraph_style = insert.paragraph_style

        root_copy = selection_to.parent.copy()
        for node in nodes:
            root_copy.append(node)
        if not root_copy.validate():
            return

        document.add_composite_command(*commands)

        placeholder_found = False
        for node_list in [node.flatten() for node in nodes]:
            for node in node_list:
                if node.type == 'placeholder':
                    UseCases.select_node(node)
                    placeholder_found = True
                    break
            if placeholder_found:
                break
                    
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def backspace():
        document = History.get_active_document()
        insert = document.cursor.get_insert_node()

        if document.cursor.has_selection():
            UseCases.delete_selection()
        elif not insert.is_first_in_parent():
            document.add_command('delete', document.cursor.prev_no_descent(insert), insert)
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')
            MessageBus.add_change_code('document_ast_changed')
        elif len(insert.parent) == 1:
            document.add_composite_command(['move_cursor_to_node', document.cursor.prev_no_descent(insert), insert])
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')
            MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def delete():
        document = History.get_active_document()
        insert = document.cursor.get_insert_node()

        if document.cursor.has_selection():
            UseCases.delete_selection()
        elif not insert.is_last_in_parent():
            insert_new = document.cursor.next_no_descent(insert)
            document.add_command('delete', insert, insert_new)
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')
            MessageBus.add_change_code('document_ast_changed')
        elif len(insert.parent) == 1:
            document.add_composite_command(['move_cursor_to_node', document.cursor.next_no_descent(insert), insert])
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')
            MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def delete_selection():
        document = History.get_active_document()
        node_from = document.cursor.get_first_node()
        node_to = document.cursor.get_last_node()

        document.add_command('delete', node_from, node_to)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def add_image_from_filename(filename):
        document = History.get_active_document()

        with open(filename, 'rb') as file:
            image = Image(file)
        if document.cursor.get_insert_node().parent.type == 'root':
            insert = document.cursor.get_insert_node()
            node = Node('widget', image)
            document.add_command('insert', insert, [node])
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')
            MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def replace_max_string_before_cursor():
        document = History.get_active_document()

        last_node = document.cursor.get_insert_node().prev_in_parent()
        first_node = last_node
        for i in range(5):
            prev_node = first_node.prev_in_parent()
            if prev_node != None and prev_node.type == 'char':
                first_node = prev_node
            else:
                break

        subtree = document.ast.get_subtree(first_node.get_position(), last_node.get_position())
        chars = ''.join([node.value for node in subtree])
        if len(chars) >= 2:
            for i in range(len(chars) - 1):
                if CharacterDB.has_replacement(chars[i:]):
                    length = len(chars) - i
                    text = xml_helpers.escape(CharacterDB.get_replacement(chars[i:]))
                    xml = xml_helpers.embellish_with_link_and_tags(text, None, first_node.tags)
                    parser = xml_parser.XMLParser()
                    nodes = parser.parse(xml)

                    commands = [['delete', last_node.prev_in_parent(length), last_node]]
                    commands.append(['insert', last_node, nodes])
                    commands.append(['move_cursor_to_node', last_node.next_in_parent()])

                    document.add_composite_command(*commands)
                    document.add_command('update_implicit_x_position')
                    document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())
                    DocumentRepo.update(document)
                    MessageBus.add_change_code('document_changed')
                    MessageBus.add_change_code('document_ast_changed')
                    return True
        return False

    @timer.timer
    def resize_widget(new_width):
        document = History.get_active_document()
        document.add_command('resize_widget', new_width)
        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def set_link(document, bounds, target):
        pos_1, pos_2 = bounds[0].get_position(), bounds[1].get_position()
        char_nodes = [node for node in document.ast.get_subtree(pos_1, pos_2) if node.type == 'char']
        document.add_command('set_link', char_nodes, target)
        document.add_command('move_cursor_to_node', bounds[1])
        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def set_paragraph_style(style):
        document = History.get_active_document()

        current_style = document.cursor.get_first_node().get_paragraph_style()
        if current_style == style:
            style = 'p'

        document.add_command('set_paragraph_style', style)
        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')
        MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def toggle_tag(tagname):
        document = History.get_active_document()

        char_nodes = [node for node in document.ast.get_subtree(*document.cursor.get_state()) if node.type == 'char']
        all_tagged = True
        for node in char_nodes:
            if tagname not in node.tags: all_tagged = False

        if len(char_nodes) > 0:
            if all_tagged:
                document.add_command('remove_tag', tagname)
            else:
                document.add_command('add_tag', tagname)

            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')
            MessageBus.add_change_code('document_ast_changed')

    @timer.timer
    def left(do_selection=False):
        document = History.get_active_document()

        insert = document.cursor.get_insert_node()
        selection = document.cursor.get_selection_node()
        if do_selection:
            document.add_command('move_cursor_to_node', document.cursor.prev_no_descent(insert), selection)
        elif document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_first_node())
        else:
            document.add_command('move_cursor_to_node', document.cursor.prev(insert))
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def jump_left(do_selection=False):
        document = History.get_active_document()

        insert = document.cursor.get_insert_node()
        selection = document.cursor.get_selection_node()

        insert_prev = insert.prev_in_parent()
        if insert_prev != None and insert_prev.type == 'char' and not NodeTypeDB.is_whitespace(insert_prev):
            insert_new = insert_prev.word_bounds()[0]
        else:
            insert_new = document.cursor.prev_no_descent(insert)

        if do_selection:
            document.add_command('move_cursor_to_node', insert_new, selection)
        elif document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_first_node())
        else:
            document.add_command('move_cursor_to_node', insert_new)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def right(do_selection=False):
        document = History.get_active_document()

        insert = document.cursor.get_insert_node()
        selection = document.cursor.get_selection_node()
        if do_selection:
            document.add_command('move_cursor_to_node', document.cursor.next_no_descent(insert), selection)
        elif document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_last_node())
        else:
            document.add_command('move_cursor_to_node', document.cursor.next(insert))
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def jump_right(do_selection=False):
        document = History.get_active_document()

        insert = document.cursor.get_insert_node()
        selection = document.cursor.get_selection_node()

        if insert != None and insert.type == 'char' and not NodeTypeDB.is_whitespace(insert):
            insert_new = insert.word_bounds()[1]
        else:
            insert_new = document.cursor.next_no_descent(insert)

        if do_selection:
            document.add_command('move_cursor_to_node', insert_new, selection)
        elif document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_last_node())
        else:
            document.add_command('move_cursor_to_node', insert_new)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def up(do_selection=False):
        document = History.get_active_document()

        x, y = document.get_absolute_xy(document.cursor.get_insert_node().layout)
        if document.cursor.implicit_x_position != None:
            x = document.cursor.implicit_x_position

        new_node = None
        insert_layout = document.cursor.get_insert_node().layout
        ancestors = document.get_ancestors(insert_layout)
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][:j]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast.lines:
                        for hbox in paragraph['layout']['children']:
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
            new_node = document.ast[0]

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node)
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def down(do_selection=False):
        document = History.get_active_document()

        x, y = document.get_absolute_xy(document.cursor.get_insert_node().layout)
        if document.cursor.implicit_x_position != None:
            x = document.cursor.implicit_x_position

        new_node = None
        insert_layout = document.cursor.get_insert_node().layout
        ancestors = document.get_ancestors(insert_layout)
        for i, box in enumerate(ancestors):
            if new_node == None and box['type'] == 'vbox' or box['type'] == 'paragraph':
                if box['type'] == 'vbox':
                    j = box['children'].index(ancestors[i - 1])
                    prev_hboxes = box['children'][j + 1:]
                elif box['type'] == 'paragraph':
                    prev_hboxes = []
                    for paragraph in document.ast.lines:
                        for hbox in paragraph['layout']['children']:
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
            new_node = document.ast[-1]

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node)
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def line_start(do_selection=False):
        document = History.get_active_document()

        layout = document.cursor.get_insert_node().layout
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][0]['node'] == None:
            layout = layout['children'][0]
        new_node = layout['children'][0]['node']

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def line_end(do_selection=False):
        document = History.get_active_document()

        layout = document.cursor.get_insert_node().layout
        while layout['parent']['parent'] != None:
            layout = layout['parent']
        while layout['children'][-1]['node'] == None:
            layout = layout['children'][-1]
        new_node = layout['children'][-1]['node']

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def select_next_placeholder():
        document = History.get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        insert = document.cursor.get_insert_node()
        node = insert

        if len(selected_nodes) == 1 and selected_nodes[0].type == 'placeholder':
            node = document.cursor.next(node)

        while not node.type == 'placeholder':
            if node == document.ast[-1]:
                node = document.ast[0]
            else:
                node = document.cursor.next(node)
            if node == insert: break

        if node.type == 'placeholder':
            UseCases.select_node(node)

    @timer.timer
    def select_prev_placeholder():
        document = History.get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        insert = document.cursor.get_insert_node()
        node = insert

        if insert.type == 'placeholder' or (len(selected_nodes) == 1 and selected_nodes[0].type == 'placeholder'):
            node = document.cursor.prev(node)

        while not node.type == 'placeholder':
            if node == document.ast[0]:
                node = document.ast[-1]
            else:
                node = document.cursor.prev(node)
            if node == insert: break

        if node.type == 'placeholder':
            UseCases.select_node(node)

    @timer.timer
    def select_node(node):
        document = History.get_active_document()

        next_node = node.next_in_parent()
        document.add_command('move_cursor_to_node', node, next_node)
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def select_all():
        document = History.get_active_document()
        document.add_composite_command(['move_cursor_to_node', document.ast[0], document.ast[-1]])
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def remove_selection():
        document = History.get_active_document()
        if document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_last_node())
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')

    @timer.timer
    def move_cursor_by_xy_offset(x, y, do_selection=False):
        document = History.get_active_document()

        orig_x, orig_y = document.get_absolute_xy(document.cursor.get_insert_node().layout)
        if document.cursor.implicit_x_position != None:
            orig_x = document.cursor.implicit_x_position
        new_y = orig_y + y

        document.add_command('move_cursor_to_xy', orig_x, new_y, do_selection)
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def move_cursor_to_xy(x, y, do_selection=False):
        document = History.get_active_document()
        document.add_command('move_cursor_to_xy', x, y, do_selection)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    @timer.timer
    def move_cursor_to_parent():
        document = History.get_active_document()

        insert = document.cursor.get_insert_node()
        new_insert = None
        for ancestor in reversed(insert.ancestors()):
            if NodeTypeDB.can_hold_cursor(ancestor):
                new_insert = ancestor
                break
            if (ancestor.type == 'mathlist' or ancestor.type == 'root') and insert != ancestor[0]:
                new_insert = ancestor[0]
                break

        if new_insert != None:
            document.add_command('move_cursor_to_node', new_insert, new_insert)
            document.add_command('update_implicit_x_position')
            document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

            DocumentRepo.update(document)
            MessageBus.add_change_code('document_changed')

    @timer.timer
    def extend_selection():
        document = History.get_active_document()

        insert = document.cursor.get_insert_node()
        selection = document.cursor.get_selection_node()

        word_start, word_end = document.cursor.get_insert_node().word_bounds()
        if word_start != None and word_end != None and (document.cursor.get_first_node().get_position() > word_start.get_position() or document.cursor.get_last_node().get_position() < word_end.get_position()):
            new_insert = word_end
            new_selection = word_start

        else:
            for ancestor in reversed(insert.ancestors()):
                if NodeTypeDB.can_hold_cursor(ancestor):
                    new_insert = ancestor
                    new_selection = document.cursor.get_selection_node()
                    break

                if ancestor.type == 'mathlist':
                    if insert == ancestor[0] and selection == ancestor[-1]: continue
                    if insert == ancestor[-1] and selection == ancestor[0]: continue
                    new_insert = ancestor[-1]
                    new_selection = ancestor[0]
                    break

                if ancestor.type == 'root':
                    line_start, line_end = document.cursor.get_insert_node().line_bounds()
                    if line_start != None and line_end != None and (document.cursor.get_first_node().get_position() > line_start.get_position() or document.cursor.get_last_node().get_position() < line_end.get_position()):
                        new_insert = line_end
                        new_selection = line_start
                    else:
                        new_insert = document.ast[0]
                        new_selection = document.ast[-1]

        document.add_command('move_cursor_to_node', new_insert, new_selection)
        document.add_command('update_implicit_x_position')
        document.add_command('scroll_to_xy', *UseCases.get_insert_on_screen_scrolling_position())

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')

    def get_insert_on_screen_scrolling_position():
        document = History.get_active_document()
        insert_node = document.cursor.get_insert_node()
        insert_position = document.get_absolute_xy(insert_node.layout)
        content_offset = ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height')
        insert_y = insert_position[1] + content_offset
        insert_height = insert_node.layout['height']
        window_height = ApplicationState.get_value('document_view_height')
        scrolling_offset_y = document.clipping.offset_y
        content_height = document.get_height() + ApplicationState.get_value('document_padding_bottom') + ApplicationState.get_value('document_padding_top') + ApplicationState.get_value('title_height') + ApplicationState.get_value('subtitle_height') + ApplicationState.get_value('title_buttons_height')

        if window_height <= 0: return (0, 0)
        if insert_y == content_offset: return (0, 0)
        if insert_y < scrolling_offset_y:
            if insert_height > window_height: return (0, insert_y - window_height + insert_height)
            else: return (0, insert_y)
        if insert_position[1] == document.get_height() - document.ast.lines[-1]['layout']['children'][-1]['height'] and content_height >= window_height:
            return (0, document.get_height() + content_offset + ApplicationState.get_value('document_padding_bottom') - window_height)
        elif insert_y > scrolling_offset_y - insert_height + window_height:
            return (0, insert_y - window_height + insert_height)
        return (document.clipping.offset_x, document.clipping.offset_y)

    @timer.timer
    def scroll_to_xy(x, y):
        document = History.get_active_document()
        document.add_command('scroll_to_xy', x, y)

        DocumentRepo.update(document)
        MessageBus.add_change_code('document_changed')


