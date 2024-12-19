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


class UseCases(object):

    def __init__(self, workspace):
        self.workspace = workspace

    def insert_xml(self, xml, tags_at_cursor=set(), link_target=None):
        document = self.workspace.active_document
        insert = document.cursor.get_insert_node()
        parser = xml_parser.XMLParser()
        nodes = parser.parse(xml, insert.parent.type)
        commands = [['delete_selection'], ['insert_nodes', nodes, link_target, tags_at_cursor]]

        if 'add_prev_selection_or_placeholder' in parser.marks:
            prev_selection_node = parser.marks['add_prev_selection_or_placeholder']

            if document.cursor.has_selection():
                subtree = document.ast.get_subtree(*document.cursor.get_state())
                for node in subtree:
                    prev_selection_node.parent.insert_before(prev_selection_node, node.copy())
            else:
                prev_selection_node.parent.insert_before(prev_selection_node, Node('placeholder', ''))

        if 'new_insert' in parser.marks and 'new_selection_bound' in parser.marks:
            commands.append(['move_cursor_to_node', parser.marks['new_insert'], parser.marks['new_selection_bound']])
        elif 'new_insert' in parser.marks:
            commands.append(['move_cursor_to_node', parser.marks['new_insert']])

        if nodes.validate():
            document.add_composite_command(*commands)

    def add_image_from_filename(self, filename):
        document = self.workspace.active_document

        image = Image(filename)
        if document.cursor.get_insert_node().parent.is_root():
            node = Node('widget', image)
            document.add_command('insert_nodes', [node])

    def replace_max_string_before_cursor(self, tags_at_cursor=set()):
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
                    parser = xml_parser.XMLParser()
                    nodes = parser.parse(text)
                    commands = [['move_cursor_by_offset', -(length + 1)], ['selection_by_offset', length]]
                    commands.append(['delete_selection'])
                    commands.append(['insert_nodes', nodes, None, tags_at_cursor])
                    commands.append(['move_cursor_by_offset', 1])
                    document.add_composite_command(*commands)
                    return True
        return False


