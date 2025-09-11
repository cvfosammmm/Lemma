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

from lemma.services.character_db import CharacterDB
from lemma.services.node_type_db import NodeTypeDB

import lemma.services.timer as timer


class FontHelper():

    def get_fontname_from_node(node=None):
        if NodeTypeDB.is_subscript(node) or NodeTypeDB.is_superscript(node):
            return 'math_small'
        if NodeTypeDB.in_fraction(node):
            return 'math_small'
        if node.type == 'char' and CharacterDB.is_mathsymbol(node.value):
            return 'math'
        if node.value != None and node.type == 'char' and node.value.isnumeric():
            return 'math'

        if node.type == 'char' and CharacterDB.is_emoji(node.value):
            return 'emojis'

        if node.get_paragraph_style().startswith('h'):
            return node.get_paragraph_style()

        if 'bold' in node.tags and 'italic' not in node.tags: return 'bold'
        if 'bold' in node.tags and 'italic' in node.tags: return 'bolditalic'
        if 'bold' not in node.tags and 'italic' in node.tags: return 'italic'

        return 'book'


