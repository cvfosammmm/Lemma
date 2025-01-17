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

import lemma.infrastructure.xml_helpers as xml_helpers
import lemma.infrastructure.xml_parser as xml_parser
from lemma.db.character_db import CharacterDB
from lemma.widgets.image import Image
from lemma.document.ast.node import Node
import lemma.helpers.helpers as helpers


class UseCases(object):

    def __init__(self, workspace):
        self.workspace = workspace

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

        placeholders = nodes.collect(lambda n: n.is_placeholder())
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


