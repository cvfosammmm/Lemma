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


def escape(text):
    escape_translation = str.maketrans({'<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;'})
    return text.translate(escape_translation)

def unescape(text):
    return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&apos;', "'").replace('&quot;', '"')

def embellish_with_link_and_tags(xml, link, tags):
    if 'italic' in tags:
        xml = '<em>' + xml + '</em>'
    if 'bold' in tags:
        xml = '<strong>' + xml + '</strong>'
    if 'verbatim' in tags:
        xml = '<code>' + xml + '</code>'
    if 'highlight' in tags:
        xml = '<mark>' + xml + '</mark>'
    if link != None:
        xml = '<a href="' + escape(link) + '">' + xml + '</a>'
    return xml


