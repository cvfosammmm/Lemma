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

import lemma.services.timer as timer


class ASTValidator():

    def validate_paragraph(paragraph):
        for child in paragraph:
            if not child.type in {'char', 'placeholder', 'eol', 'widget', 'mathscript', 'mathfraction', 'mathroot', 'end'}:
                return False
            if not ASTValidator.validate_node(child):
                return False
        return True

    def validate_node(node):
        if node.type in {'char', 'widget', 'placeholder', 'eol', 'end'}:
            return len(node.children) == 0

        if node.type == 'mathscript':
            return len(node.children) == 2 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)

        if node.type == 'mathfraction':
            return len(node.children) == 2 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)

        if node.type == 'mathroot':
            return len(node.children) == 2 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)

        if node.type == 'mathlist':
            return len(node.children) == 0 \
                or all(child.type in {'char', 'placeholder', 'end'} for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)

    def validate_node_for_parent_type(node, parent_type):
        if parent_type == 'paragraph':
            return node.type in {'char', 'placeholder', 'eol', 'widget', 'mathscript', 'mathfraction', 'mathroot', 'end'}
        if parent_type == 'mathlist':
            return node.type in {'char', 'placeholder', 'end'}
        print(node.type, parent_type)
        return False


