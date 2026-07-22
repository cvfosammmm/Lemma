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

import time

import lemma.services.xml_helpers as xml_helpers
from lemma.services.xml_parser import XMLParser
from lemma.document.ast import Root, Cursor
from lemma.document.command_manager import CommandManager
from lemma.services.character_db import CharacterDB
from lemma.document.plaintext import Plaintext
from lemma.document.links import Links
from lemma.document.files import Files
from lemma.document.xml import XML
from lemma.document.layout import Layout
from lemma.services.ast_validator import ASTValidator
from lemma.services.node_type_db import NodeTypeDB
import lemma.services.timer as timer


class Document():

    def __init__(self, id=None):
        self.last_modified = time.time()
        self.last_cursor_movement = time.time()

        self.id = id
        self.title = ''
        self.ast = Root()
        self.cursor = Cursor(self, self.ast[0][0], self.ast[0][0])

        self.plaintext = Plaintext(self)
        self.links = Links(self)
        self.files = Files(self)
        self.xml = XML(self)
        self.layout = Layout(self)

        self.secondary_formats_cache = dict()
        self.query_cache = dict()

        self.command_manager = CommandManager(self)

    def start_undoable_action(self):
        self.command_manager.start_undoable_action()

    def end_undoable_action(self):
        self.command_manager.end_undoable_action()

    def undoable_action(original_function):
        def new_function(*args, **kwargs):
            start_new_action = args[0].command_manager.current_undoable_action == None
            if start_new_action:
                args[0].command_manager.start_undoable_action()
            original_function(*args, **kwargs)
            if start_new_action:
                args[0].command_manager.end_undoable_action()

        return new_function

    def set_title(self, title):
        self.title = title
        self.update_last_modified()

    @undoable_action
    def insert_paragraph(self, paragraph, index):
        if not ASTValidator.validate_paragraph(paragraph): return

        self.command_manager.add_command('insert_paragraph', index, paragraph)

    @undoable_action
    def insert_nodes(self, nodes, insert=None):
        if insert == None:
            insert = self.get_insert_node()

        for node in nodes:
            if not ASTValidator.validate_node_for_parent_type(node, insert.parent.type): return
            if not ASTValidator.validate_node(node): return

        self.command_manager.add_command('insert_nodes', insert, nodes)

    @undoable_action
    def replace_max_string_before_cursor(self):
        insert_node = self.get_insert_node()
        last_node = insert_node.prev()

        if last_node == None: return

        first_node = last_node
        for i in range(5):
            prev_node = first_node.prev_in_parent()
            if prev_node != None and prev_node.type == 'char':
                first_node = prev_node
            else:
                break

        subtree = self.get_subtree(first_node, last_node)
        chars = ''.join([node.value for node in subtree])
        if len(chars) >= 2:
            for i in range(len(chars) - 1):
                if CharacterDB.has_replacement(chars[i:]):
                    length = len(chars) - i
                    text = xml_helpers.escape(CharacterDB.get_replacement(chars[i:]))
                    xml = xml_helpers.embellish_with_link_and_tags(text, None, first_node.tags)
                    start_node = last_node
                    for i in range(length):
                        start_node = start_node.prev_in_parent()

                    nodes = []
                    title, meta, paragraphs = XMLParser.parse(xml)
                    for paragraph in paragraphs:
                        nodes += paragraph.children

                    self.delete_nodes(start_node, last_node)
                    self.insert_nodes(nodes, last_node)
                    self.set_insert_and_selection_node(insert_node)
                    return

    @undoable_action
    def delete_selected_nodes(self):
        if self.has_selection():
            node_from = self.get_first_selection_bound()
            node_to = self.get_last_selection_bound()
            self.delete_nodes(node_from, node_to)

    @undoable_action
    def delete_nodes(self, node_from, node_to):
        if node_from.parent == node_to.parent:
            self.command_manager.add_command('delete_nodes', node_from, node_to)
        else:
            node_from_index = node_from.parent.index(node_from)
            paragraph_index_from = self.ast.index(node_from.parent)
            paragraph_index_to = self.ast.index(node_to.parent)

            if node_from.is_first_in_parent():
                self.command_manager.add_command('delete_paragraphs', paragraph_index_from, paragraph_index_to)
                self.command_manager.add_command('delete_nodes', node_to.first_in_parent(), node_to)
            else:
                copy_nodes = node_to.parent[node_to.parent.index(node_to):node_to.parent.index(node_to.last_in_parent())]
                end_of_first_paragraph = node_from.last_in_parent()
                last_paragraph = node_to.parent
                self.command_manager.add_command('delete_nodes', node_from, end_of_first_paragraph)
                self.command_manager.add_command('delete_nodes', node_to, node_to.last_in_parent())
                self.command_manager.add_command('delete_paragraphs', paragraph_index_from + 1, paragraph_index_to + 1)
                self.command_manager.add_command('insert_nodes', end_of_first_paragraph, copy_nodes)
                self.command_manager.add_command('move_cursor_to_node', self.ast[paragraph_index_from][node_from_index], self.ast[paragraph_index_from][node_from_index])

    @undoable_action
    def add_tag(self, tagname):
        self.command_manager.add_command('add_tag', tagname)

    @undoable_action
    def remove_tag(self, tagname):
        self.command_manager.add_command('remove_tag', tagname)

    @undoable_action
    def set_link(self, bounds, target):
        char_nodes = [node for node in self.get_subtree(*bounds) if node.type == 'char']

        self.command_manager.add_command('set_link', char_nodes, target)

    @undoable_action
    def set_paragraph_style(self, paragraph, style):
        self.command_manager.add_command('set_paragraph_style', paragraph, style)

    @undoable_action
    def set_indentation_level(self, paragraph, level):
        self.command_manager.add_command('set_indentation_level', paragraph, level)

    @undoable_action
    def set_paragraph_state(self, paragraph, state):
        self.command_manager.add_command('set_paragraph_state', paragraph, state)

    @timer.timer
    def set_insert_and_selection_node(self, new_insert, new_selection_bound=None):
        self.command_manager.add_command('move_cursor_to_node', new_insert, new_selection_bound)

    @undoable_action
    def resize_widget(self, node, new_width):
        if node.type != 'widget': return

        self.command_manager.add_command('resize_widget', node, new_width)

    @undoable_action
    def set_widget_attribute(self, node, key, value):
        if node.type != 'widget': return

        self.command_manager.add_command('set_widget_attribute', node, key, value)

    def select_placeholder_in_range(self, first_node, last_node):
        placeholder_found = False
        node = first_node
        while node != last_node:
            if node.type == 'placeholder':
                self.select_node(node)
                break
            node = node.next()

    def select_node(self, node):
        next_node = node.next_in_parent()
        self.command_manager.add_command('move_cursor_to_node', node, next_node)

    def undo(self):
        self.command_manager.undo()

    def redo(self):
        self.command_manager.redo()

    def update_last_modified(self):
        self.last_modified = time.time()
        self.last_cursor_movement = time.time()
        self.query_cache = dict()
        self.secondary_formats_cache = dict()

    def update_last_cursor_movement(self):
        self.last_cursor_movement = time.time()
        self.query_cache = dict()

    def invalidate_paragraph(self, paragraph):
        self.plaintext.invalidate_paragraph(paragraph)
        self.links.invalidate_paragraph(paragraph)
        self.files.invalidate_paragraph(paragraph)
        self.xml.invalidate_paragraph(paragraph)
        paragraph.update_last_modified()

    def has_multiple_lines_selected(self):
        if 'multiple_lines_selected' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['multiple_lines_selected'] = any(node.type == 'eol' for node in selected_nodes)
        return self.query_cache['multiple_lines_selected']

    def cursor_at_paragraph_start(self):
        if 'cursor_at_paragraph_start' not in self.query_cache:
            insert = self.get_insert_node()
            self.query_cache['cursor_at_paragraph_start'] = (insert == insert.paragraph_start())
        return self.query_cache['cursor_at_paragraph_start']

    def cursor_inside_link(self):
        if 'cursor_inside_link' not in self.query_cache:
            self.query_cache['cursor_inside_link'] = (not self.has_selection() and self.get_insert_node().is_inside_link())
        return self.query_cache['cursor_inside_link']

    def get_link_at_cursor(self):
        if self.has_selection(): return None

        current_node = self.get_insert_node()
        prev_node = current_node.prev_in_parent()
        if prev_node != None and current_node.link == prev_node.link:
            return current_node.link
        return None

    def links_inside_selection(self):
        if 'links_inside_selection' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['links_inside_selection'] = any(node.link != None for node in selected_nodes)
        return self.query_cache['links_inside_selection']

    def whole_selection_is_one_link(self):
        if 'whole_selection_is_one_link' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            self.query_cache['whole_selection_is_one_link'] = self.links_inside_selection() and all(node.link == selected_nodes[0].link for node in selected_nodes)
        return self.query_cache['whole_selection_is_one_link']

    def get_selected_widget(self):
        if 'selected_widget' not in self.query_cache:
            selected_nodes = self.get_selected_nodes()
            if len(selected_nodes) == 1 and selected_nodes[0].type == 'widget':
                self.query_cache['selected_widget'] = selected_nodes[0].value
            else:
                self.query_cache['selected_widget'] = None
        return self.query_cache['selected_widget']

    def get_insert_node(self):
        return self.cursor.get_insert_node()

    def get_selection_node(self):
        return self.cursor.get_selection_node()

    def insert_parent_is_root(self):
        if 'insert_parent_is_root' not in self.query_cache:
            self.query_cache['insert_parent_is_root'] = (self.get_insert_node().parent.type == 'paragraph')
        return self.query_cache['insert_parent_is_root']

    def has_selection(self):
        if 'has_selection' not in self.query_cache:
            self.query_cache['has_selection'] = self.cursor.has_selection()
        return self.query_cache['has_selection']

    def get_selected_nodes(self):
        if 'selected_nodes' not in self.query_cache:
            bounds = self.get_insert_node(), self.get_selection_node()
            self.query_cache['selected_nodes'] = self.get_subtree(*bounds)
        return self.query_cache['selected_nodes']

    @timer.timer
    def get_subtree(self, node1, node2):
        pos1 = node1.get_position()
        pos2 = node2.get_position()

        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        parent1, parent2 = self.get_node_at_position(pos1[:-1]), self.get_node_at_position(pos2[:-1])

        # this can happen, when the selection stretches over multiple paragraphs
        if parent1 != parent2:
            result = parent1[pos1[-1]:]
            for paragraph in self.ast[pos1[0] + 1:pos2[0]]:
                result += paragraph.children
            result += parent2[:pos2[-1]]
            return result
        else:
            return parent1[pos1[-1]:pos2[-1]]

    def get_node_at_position(self, pos):
        node = self.ast
        for index in pos:
            node = node[index]
        return node

    def get_first_selection_bound(self):
        if 'selection_bounds' not in self.query_cache:
            self.query_cache['selection_bounds'] = self.cursor.get_first_and_last_node()
        return self.query_cache['selection_bounds'][0]

    def get_last_selection_bound(self):
        if 'selection_bounds' not in self.query_cache:
            self.query_cache['selection_bounds'] = self.cursor.get_first_and_last_node()
        return self.query_cache['selection_bounds'][1]

    def get_cursor_state(self):
        if 'cursor_state' not in self.query_cache:
            self.query_cache['cursor_state'] = [self.get_insert_node().get_position(), self.get_selection_node().get_position()]
        return self.query_cache['cursor_state']

    def can_undo(self):
        if 'can_undo' not in self.query_cache:
            self.query_cache['can_undo'] = self.command_manager.can_undo()
        return self.query_cache['can_undo']

    def can_redo(self):
        if 'can_redo' not in self.query_cache:
            self.query_cache['can_redo'] = self.command_manager.can_redo()
        return self.query_cache['can_redo']

    def get_link_bounds_and_targets(self):
        current_target = None
        current_bounds = [None, None]
        result = list()
        for paragraph in self.ast:
            for node in paragraph:
                current_bounds[1] = node
                if current_target != node.link:
                    if current_bounds[0] != None and current_target != None:
                        result.append([[current_bounds[0], current_bounds[1]], current_target])
                    current_bounds[0] = node
                current_target = node.link
        if current_bounds[0] != None and current_target != None:
            result.append([[current_bounds[0], current_bounds[1]], current_target])
        return result

    def get_files(self):
        if 'files' not in self.secondary_formats_cache:
            self.files.update()
            self.secondary_formats_cache['files'] = self.files.files
        return self.secondary_formats_cache['files']

    def get_links(self):
        if 'links' not in self.secondary_formats_cache:
            self.links.update()
            self.secondary_formats_cache['links'] = self.links.links
        return self.secondary_formats_cache['links']

    def get_plaintext(self):
        if 'plaintext' not in self.secondary_formats_cache:
            self.plaintext.update()
            self.secondary_formats_cache['plaintext'] = self.plaintext.plaintext
        return self.secondary_formats_cache['plaintext']

    def get_layout(self, preedit_string, font_theme):
        if 'layout' not in self.secondary_formats_cache:
            self.layout.update()
            self.secondary_formats_cache['layout'] = self.layout
        elif self.layout.preedit_string != preedit_string or self.layout.font_theme != font_theme:
            self.layout.update_font_theme(font_theme)
            self.layout.update_preedit(preedit_string)
            self.layout.update()
        return self.secondary_formats_cache['layout']

    @timer.timer
    def get_xml(self):
        if 'xml' not in self.secondary_formats_cache:
            self.xml.update()
            xml = '<head>'
            xml += '<title>' + xml_helpers.escape(self.title) + '</title>'
            xml += '<meta name="insert-position" content="' + str(self.get_cursor_state()[0]) + '" />'
            xml += '<meta name="selection-position" content="' + str(self.get_cursor_state()[1]) + '" />'
            xml += '</head>'
            xml += '<root>'
            for paragraph in self.ast:
                xml += self.xml.paragraph_xml[paragraph]
            xml += '</root>'
            self.secondary_formats_cache['xml'] = xml
        return self.secondary_formats_cache['xml']


