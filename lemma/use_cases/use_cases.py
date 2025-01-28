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

import lemma.infrastructure.xml_helpers as xml_helpers
import lemma.infrastructure.xml_parser as xml_parser
from lemma.db.character_db import CharacterDB
from lemma.widgets.image import Image
from lemma.document.ast.node import Node
from lemma.document.layout.layout_vbox import LayoutVBox
from lemma.document.layout.layout_document import LayoutDocument
import lemma.helpers.helpers as helpers


class UseCases(object):

    def __init__(self, workspace):
        self.workspace = workspace

    def open_link(self, link_target):
        workspace = self.workspace

        if urlparse(link_target).scheme in ['http', 'https']:
            webbrowser.open(link_target)
        else:
            target_document = workspace.get_by_title(link_target)
            if target_document != None:
                workspace.set_active_document(target_document)
            else:
                id = workspace.get_new_document_id()
                document = Document(id)
                document.title = link_target
                workspace.add(document)
                workspace.set_active_document(document)

    def set_title(self, title):
        document = self.workspace.active_document
        document.add_command('set_title', title)

    #@helpers.timer
    def insert_xml(self, xml):
        document = self.workspace.active_document
        insert = document.cursor.get_insert_node()
        insert_prev = insert.prev_in_parent()
        parser = xml_parser.XMLParser()
        nodes = parser.parse(xml, insert.parent.type)
        commands = [['delete_selection'], ['insert_nodes', nodes]]

        if len(nodes) == 0: return

        if insert_prev != None and not insert_prev.is_eol():
            last_node_style = nodes[-1].paragraph_style
            for node in nodes:
                node.paragraph_style = insert_prev.paragraph_style
                if node.is_eol():
                    if insert.is_eol():
                        insert.paragraph_style = last_node_style
                    break
        if not insert.is_eol():
            for node in reversed(nodes):
                if node.is_eol(): break
                node.paragraph_style = insert.paragraph_style

        if 'prev_selection_start' in parser.marks and 'prev_selection_end' in parser.marks:
            prev_selection_start = parser.marks['prev_selection_start']
            prev_selection_end = parser.marks['prev_selection_end']

            if document.cursor.has_selection() and prev_selection_start.parent == prev_selection_end.parent:
                subtree = document.ast.get_subtree(*document.cursor.get_state())
                prev_selection_start.parent.remove_range(prev_selection_start, prev_selection_end)
                for node in subtree:
                    prev_selection_end.parent.insert_before(prev_selection_end, node.copy())

        placeholders = [n for n in nodes.flatten() if n.is_placeholder()]
        if len(placeholders) > 0:
            commands.append(['move_cursor_to_node', placeholders[0], placeholders[0].next_in_parent()])
        elif 'new_insert' in parser.marks and 'new_selection_bound' in parser.marks:
            if parser.marks['new_insert'].parent != None and parser.marks['new_selection_bound'].parent != None:
                commands.append(['move_cursor_to_node', parser.marks['new_insert'], parser.marks['new_selection_bound']])
        elif 'new_insert' in parser.marks:
            if parser.marks['new_insert'].parent != None:
                commands.append(['move_cursor_to_node', parser.marks['new_insert']])

        if nodes.validate():
            document.add_composite_command(*commands)

    def backspace(self):
        document = self.workspace.active_document
        insert = document.cursor.get_insert_node()

        if document.cursor.has_selection():
            self.delete_selection()
        else:
            if not insert.is_first_in_parent() or len(insert.parent) == 1:
                document.add_composite_command(['move_cursor_by_offset', -1, True], ['delete_selection'])

    def delete(self):
        document = self.workspace.active_document
        insert = document.cursor.get_insert_node()

        if document.cursor.has_selection():
            self.delete_selection()
        elif not insert.is_last_in_parent() or len(insert.parent) == 1:
            document.add_composite_command(['move_cursor_by_offset', 1, True], ['delete_selection'])

    def delete_selection(self):
        document = self.workspace.active_document
        document.add_command('delete_selection')

    def add_image_from_filename(self, filename):
        document = self.workspace.active_document

        image = Image(filename)
        if document.cursor.get_insert_node().parent.is_root():
            node = Node('widget', image)
            document.add_command('insert_nodes', [node])

    def replace_max_string_before_cursor(self, tags):
        document = self.workspace.active_document

        last_node = document.cursor.get_insert_node().prev_in_parent()
        first_node = last_node
        for i in range(5):
            prev_node = first_node.prev_in_parent()
            if prev_node != None and prev_node.is_char():
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
                    xml = '<char tags="' + ' '.join(tags) + '">' + text + '</char>'
                    parser = xml_parser.XMLParser()
                    nodes = parser.parse(xml)
                    commands = [['move_cursor_by_offset', -(length + 1)], ['move_cursor_by_offset', length, True]]
                    commands.append(['delete_selection'])
                    commands.append(['insert_nodes', nodes])
                    commands.append(['move_cursor_by_offset', 1])
                    document.add_composite_command(*commands)
                    return True
        return False

    def resize_widget(self, new_width):
        document = self.workspace.active_document
        document.add_command('resize_widget', new_width)

    def set_link(self, bounds, target):
        document = self.workspace.active_document
        document.add_command('set_link', bounds, target)

    def set_paragraph_style(self, style):
        document = self.workspace.active_document

        current_style = document.cursor.get_insert_node().get_paragraph_style()
        if current_style == style:
            style = 'p'

        document.add_command('set_paragraph_style', style)

    def toggle_tag(self, tagname):
        document = self.workspace.active_document

        char_nodes = [node for node in document.ast.get_subtree(*document.cursor.get_state()) if node.is_char()]
        all_tagged = True
        for node in char_nodes:
            if tagname not in node.tags: all_tagged = False

        if len(char_nodes) > 0:
            if all_tagged:
                document.add_command('remove_tag', tagname)
            else:
                document.add_command('add_tag', tagname)

    def left(self, do_selection=False):
        document = self.workspace.active_document

        if do_selection:
            document.add_command('move_cursor_by_offset', -1, True)
        elif document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_first_node())
        else:
            document.add_command('move_cursor_by_offset', -1)

    def right(self, do_selection=False):
        document = self.workspace.active_document

        if do_selection:
            document.add_command('move_cursor_by_offset', 1, True)
        elif document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_last_node())
        else:
            document.add_command('move_cursor_by_offset', 1)

    def up(self, do_selection=False):
        document = self.workspace.active_document

        x, y = document.cursor.get_insert_node().layout.get_absolute_xy()
        if document.cursor.implicit_x_position != None:
            x = document.cursor.implicit_x_position

        new_node = None
        insert_layout = document.cursor.get_insert_node().layout
        ancestors = insert_layout.get_ancestors()
        for i, box in enumerate(ancestors):
            if new_node == None and isinstance(box, LayoutVBox) or isinstance(box, LayoutDocument):
                j = box.children.index(ancestors[i - 1])
                for child in reversed(box.children[:j]):
                    if new_node == None:
                        min_distance = 10000
                        for layout in child.children:
                            layout_x, layout_y = layout.get_absolute_xy()
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = layout.node
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[0]

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node, False)

    def down(self, do_selection=False):
        document = self.workspace.active_document

        x, y = document.cursor.get_insert_node().layout.get_absolute_xy()
        if document.cursor.implicit_x_position != None:
            x = document.cursor.implicit_x_position

        new_node = None
        insert_layout = document.cursor.get_insert_node().layout
        ancestors = insert_layout.get_ancestors()
        for i, box in enumerate(ancestors):
            if new_node == None and isinstance(box, LayoutVBox) or isinstance(box, LayoutDocument):
                j = box.children.index(ancestors[i - 1])
                for child in box.children[j + 1:]:
                    if new_node == None:
                        min_distance = 10000
                        for layout in child.children:
                            layout_x, layout_y = layout.get_absolute_xy()
                            distance = abs(layout_x - x)
                            if distance < min_distance:
                                new_node = layout.node
                                min_distance = distance
        if new_node == None:
            new_node = document.ast[-1]

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node, False)

    def line_start(self, do_selection=False):
        document = self.workspace.active_document

        layout = document.cursor.get_insert_node().layout
        while layout.parent.parent != None:
            layout = layout.parent
        while layout.children[0].node == None:
            layout = layout.children[0]
        new_node = layout.children[0].node

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node, True)

    def line_end(self, do_selection=False):
        document = self.workspace.active_document

        layout = document.cursor.get_insert_node().layout
        while layout.parent.parent != None:
            layout = layout.parent
        while layout.children[-1].node == None:
            layout = layout.children[-1]
        new_node = layout.children[-1].node

        selection_node = document.cursor.get_selection_node()
        document.add_command('move_cursor_to_node', new_node, new_node if not do_selection else selection_node, True)

    def select_next_placeholder(self):
        document = self.workspace.active_document

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        insert = document.cursor.get_insert_node()
        node = insert

        if len(selected_nodes) == 1 and selected_nodes[0].is_placeholder():
            node = document.cursor.next(node)

        while not node.is_placeholder():
            if node == document.ast[-1]:
                node = document.ast[0]
            else:
                node = document.cursor.next(node)
            if node == insert: break

        if node.is_placeholder():
            self.select_node(node)

    def select_prev_placeholder(self):
        document = self.workspace.active_document

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        insert = document.cursor.get_insert_node()
        node = insert

        if insert.is_placeholder() or (len(selected_nodes) == 1 and selected_nodes[0].is_placeholder()):
            node = document.cursor.prev(node)

        while not node.is_placeholder():
            if node == document.ast[0]:
                node = document.ast[-1]
            else:
                node = document.cursor.prev(node)
            if node == insert: break

        if node.is_placeholder():
            self.select_node(node)

    def select_node(self, node):
        document = self.workspace.active_document

        next_node = node.next_in_parent()
        document.add_command('move_cursor_to_node', node, next_node, False)

    def select_all(self):
        document = self.workspace.active_document
        document.add_composite_command(['move_cursor_to_node', document.ast[0], document.ast[-1]])

    def remove_selection(self):
        document = self.workspace.active_document
        if document.cursor.has_selection():
            document.add_command('move_cursor_to_node', document.cursor.get_last_node())

    def move_cursor_by_xy_offset(self, x, y, do_selection=False):
        document = self.workspace.active_document

        orig_x, orig_y = document.cursor.get_insert_node().layout.get_absolute_xy()
        if document.cursor.implicit_x_position != None:
            orig_x = document.cursor.implicit_x_position
        new_y = orig_y + y

        document.add_command('move_cursor_to_xy', orig_x, new_y, do_selection, False)

    def move_cursor_to_xy(self, x, y, do_selection=False):
        document = self.workspace.active_document
        document.add_command('move_cursor_to_xy', x, y, do_selection, True)

    def select_word_at_insert(self):
        document = self.workspace.active_document

        word_start, word_end = document.cursor.get_insert_node().word_bounds()
        if word_start != None and word_end != None:
            self.extend_selection(word_start, word_end)

    def select_line_at_insert(self):
        document = self.workspace.active_document

        line_start, line_end = document.cursor.get_insert_node().line_bounds()
        self.extend_selection(line_start, line_end)

    def extend_selection(self, node_start, node_end):
        document = self.workspace.active_document

        node_1 = document.cursor.get_first_node()
        node_2 = document.cursor.get_last_node()

        if node_1.get_position() > node_start.get_position(): node_1 = node_start
        if node_2.get_position() < node_end.get_position(): node_2 = node_end

        document.add_command('move_cursor_to_node', node_2, node_1)

    def scroll_to_xy(self, x, y):
        document = self.workspace.active_document
        document.add_command('scroll_to_xy', x, y)


