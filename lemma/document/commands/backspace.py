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


class Command():

    def __init__(self):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.state = dict()

    def run(self, document):
        self.state['insert_position_before'] = document.ast.get_insert_position()
        self.state['deleted_nodes'] = []

        if document.ast.get_insert_node().parent.is_line():
            iterator = document.ast.get_insert_node().get_iterator()
            if iterator.starts_line():
                if iterator.prev():
                    document.ast.move_insert_to_node(iterator.get_node())
                    self.state['deleted_nodes'] = document.ast.delete_char_at_insert()
            else:
                line = document.ast.get_insert_node().parent
                index = line.get_index(document.ast.get_insert_node())
                while not line.get_child(index - 1).is_leaf():
                    index -= 1
                document.ast.move_insert_to_node(line.get_child(index - 1))
                self.state['deleted_nodes'] = document.ast.delete_char_at_insert()
        elif document.ast.get_insert_node().parent.is_math_area():
            math_area = document.ast.get_insert_node().parent
            if document.ast.get_insert_node() != math_area.get_child(0):
                index = math_area.get_index(document.ast.get_insert_node())
                document.ast.move_insert_to_node(math_area.get_child(index - 1))
                self.state['deleted_nodes'] = document.ast.delete_char_at_insert()
            elif math_area.length() == 1:
                document.ast.move_insert_by_offset(-1)
                self.state['deleted_nodes'] = document.ast.delete_char_at_insert()

        self.is_undo_checkpoint = (len(self.state['deleted_nodes']) > 0)
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for node in self.state['deleted_nodes']:
            document.ast.insert_node(node)
        document.ast.move_insert_to_position(self.state['insert_position_before'])
        document.set_scroll_insert_on_screen_after_layout_update()


