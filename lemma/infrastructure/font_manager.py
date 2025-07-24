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

import gi
gi.require_version('Rsvg', '2.0')
gi.require_version('HarfBuzz', '0.0')
from gi.repository import Rsvg
from gi.repository import HarfBuzz

import cairo
import os.path

import lib.freetype2.freetype2 as freetype2
import lib.fontconfig.fontconfig as fontconfig
import lemma.infrastructure.timer as timer

from lemma.db.character_db import CharacterDB
from lemma.infrastructure.service_locator import ServiceLocator


class FontManager():

    fonts = dict()
    harfbuzz_buffer = HarfBuzz.buffer_create()
    harfbuzz_features = [HarfBuzz.feature_from_string(b'liga 0')[1], HarfBuzz.feature_from_string(b'kern 1')[1]]

    def add_font(name, filename, size, ascend, descend, padding_top, padding_bottom):
        fontconfig.Config.get_current().app_font_add_file(filename)

        FontManager.fonts[name] = dict()
        FontManager.fonts[name]['filename'] = filename
        face = freetype2.get_default_lib().new_face(filename)
        face.set_char_size(size=size, resolution=72)
        FontManager.fonts[name]['face'] = face
        FontManager.fonts[name]['ascend'] = ascend
        FontManager.fonts[name]['descend'] = -descend
        FontManager.fonts[name]['line_height'] = FontManager.fonts[name]['ascend'] - FontManager.fonts[name]['descend']
        FontManager.fonts[name]['padding_top'] = padding_top
        FontManager.fonts[name]['padding_bottom'] = padding_bottom
        harfbuzz_blob = HarfBuzz.blob_create_from_file_or_fail(filename)
        harfbuzz_face = HarfBuzz.face_create(harfbuzz_blob, 0)
        FontManager.fonts[name]['harfbuzz_font'] = HarfBuzz.font_create(harfbuzz_face)
        HarfBuzz.font_set_scale(FontManager.fonts[name]['harfbuzz_font'], size * 64, size * 64)
        FontManager.fonts[name]['char_extents'] = dict()
        FontManager.fonts[name]['surface_cache'] = dict()

    def get_fontname_from_node(node=None):
        if node == None: return 'book'

        if node.is_subscript() or node.is_superscript():
            return 'math_small'
        if node.in_fraction():
            return 'math_small'
        if node.type == 'char' and CharacterDB.is_mathsymbol(node.value):
            return 'math'
        if node.value != None and node.is_char() and node.value.isnumeric():
            return 'math'

        if node.is_char() and CharacterDB.is_emoji(node.value):
            return 'emojis'

        if node.get_paragraph_style().startswith('h'):
            return node.get_paragraph_style()

        if 'bold' in node.tags and 'italic' not in node.tags: return 'bold'
        if 'bold' in node.tags and 'italic' in node.tags: return 'bolditalic'
        if 'bold' not in node.tags and 'italic' in node.tags: return 'italic'

        return 'book'

    def get_descend(fontname='book'):
        return FontManager.fonts[fontname]['descend']

    def get_ascend(fontname='book'):
        return FontManager.fonts[fontname]['ascend']

    def get_padding_top(fontname='book'):
        return FontManager.fonts[fontname]['padding_top']

    def get_padding_bottom(fontname='book'):
        return FontManager.fonts[fontname]['padding_bottom']

    def measure_single(char, fontname='book'):
        if char not in FontManager.fonts[fontname]['char_extents']:
            FontManager.load_glyph(char, fontname=fontname)

        return FontManager.fonts[fontname]['char_extents'][char]

    @timer.timer
    def measure(text, fontname='book'):
        harfbuzz_buffer = FontManager.harfbuzz_buffer
        HarfBuzz.buffer_reset(harfbuzz_buffer)
        HarfBuzz.buffer_add_utf8(harfbuzz_buffer, text.encode('utf8'), 0, -1)
        HarfBuzz.buffer_guess_segment_properties(harfbuzz_buffer)
        HarfBuzz.shape(FontManager.fonts[fontname]['harfbuzz_font'], harfbuzz_buffer, FontManager.harfbuzz_features)
        positions = HarfBuzz.buffer_get_glyph_positions(harfbuzz_buffer)

        result = []
        for pos, char in zip(positions, text):
            if char not in FontManager.fonts[fontname]['char_extents']:
                FontManager.load_glyph(char, fontname=fontname)
            extents = FontManager.fonts[fontname]['char_extents'][char][:]
            extents[0] = int(pos.x_advance / 64)
            result.append(extents)

        return result
 
    def get_surface(char, fontname='book'):
        if char not in FontManager.fonts[fontname]['surface_cache']:
            FontManager.load_glyph(char, fontname=fontname)

        return FontManager.fonts[fontname]['surface_cache'][char]

    def load_glyph(char, fontname='book'):
        if fontname == 'emojis':
            FontManager.load_emoji(char)
        else:
            FontManager.load_glyph_from_font(char, fontname)

    def load_emoji(char):
        if char not in FontManager.fonts['emojis']['char_extents']:
            FontManager.fonts['emojis']['face'].load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
            FontManager.fonts['emojis']['face'].glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

            width = FontManager.fonts['emojis']['face'].glyph.advance.x
            height = FontManager.fonts['emojis']['line_height']
            left = 0
            top = -FontManager.fonts['emojis']['ascend']

            viewport = Rsvg.Rectangle()
            viewport.x = 0
            viewport.y = 0
            viewport.width = width
            viewport.height = height

            surface = cairo.ImageSurface(cairo.Format.ARGB32, int(width), int(height))
            ctx = cairo.Context(surface)

            res_path = ServiceLocator.get_resources_path()
            filename = 'emoji_u' + hex(ord(char))[2:] + '.svg'
            rsvg_handle = Rsvg.Handle.new_from_file(os.path.join(res_path, 'fonts/Noto_Color_Emoji/svg', filename))
            rsvg_handle.render_document(ctx, viewport)

            FontManager.fonts['emojis']['char_extents'][char] = [width, height, left, top]
            FontManager.fonts['emojis']['surface_cache'][char] = surface

    def load_glyph_from_font(char, fontname='book'):
        if char not in FontManager.fonts[fontname]['char_extents']:
            FontManager.fonts[fontname]['face'].load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
            FontManager.fonts[fontname]['face'].glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

            width = FontManager.fonts[fontname]['face'].glyph.advance.x
            height = FontManager.fonts[fontname]['line_height']
            left = FontManager.fonts[fontname]['face'].glyph.bitmap_left
            top = -FontManager.fonts[fontname]['face'].glyph.bitmap_top

            FontManager.fonts[fontname]['char_extents'][char] = [width, height, left, top]
            if FontManager.fonts[fontname]['face'].glyph.bitmap.width > 0:
                FontManager.fonts[fontname]['surface_cache'][char] = FontManager.fonts[fontname]['face'].glyph.bitmap.make_image_surface()
            else:
                FontManager.fonts[fontname]['surface_cache'][char] = None


