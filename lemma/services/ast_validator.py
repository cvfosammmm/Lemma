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
            if not child.type in {'char', 'placeholder', 'eol', 'widget', 'math', 'end', 'table'}:
                return False
            if not ASTValidator.validate_node(child):
                return False
        return True

    def validate_node(node):
        if node.type in {'char', 'widget', 'placeholder', 'eol', 'end'}:
            return len(node.children) == 0
        elif node.type == 'math':
            return len(node.children) >= 1 \
                and all(child.type in {'char', 'placeholder', 'mathscript', 'mathfraction', 'mroot', 'msqrt', 'end'} for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'mathscript':
            return len(node.children) == 2 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'mathfraction':
            return len(node.children) == 2 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'mroot':
            return len(node.children) == 2 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'msqrt':
            return len(node.children) == 1 \
                and all(child.type == 'mathlist' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'mathlist':
            return len(node.children) >= 1 \
                and all(child.type in {'char', 'placeholder', 'end'} for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'table':
            return all(child.type == 'tr' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'tr':
            return len(node.children) >= 1 \
                and all(child.type == 'td' for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)
        elif node.type == 'td':
            return len(node.children) >= 1 \
                and all(child.type in {'char', 'placeholder', 'widget', 'math', 'end'} for child in node.children) \
                and all(ASTValidator.validate_node(child) for child in node.children)

    def validate_node_for_parent(node_type, parent_type):
        if parent_type == 'paragraph':
            return node_type in {'char', 'placeholder', 'eol', 'widget', 'math', 'end', 'table'}
        elif parent_type == 'math':
            return node_type in {'char', 'placeholder', 'mathscript', 'mathfraction', 'mroot', 'msqrt', 'end'}
        elif parent_type == 'mathlist':
            return node_type in {'char', 'placeholder', 'end'}
        elif parent_type == 'mathscript':
            return node_type in {'mathlist'}
        elif parent_type == 'mathfraction':
            return node_type in {'mathlist'}
        elif parent_type == 'mroot':
            return node_type in {'mathlist'}
        elif parent_type == 'msqrt':
            return node_type in {'mathlist'}
        elif parent_type == 'td':
            return node_type in {'char', 'placeholder', 'widget', 'math', 'end'}
        elif parent_type == 'tr':
            return node_type == 'td'
        elif parent_type == 'table':
            return node_type == 'tr'
        return False


