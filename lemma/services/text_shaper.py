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
gi.require_version('HarfBuzz', '0.0')
from gi.repository import HarfBuzz

import lib.freetype2.freetype2 as freetype2
import lib.fontconfig.fontconfig as fontconfig
import lemma.services.timer as timer


class TextShaper():

    fonts = dict()
    harfbuzz_buffer = HarfBuzz.buffer_create()
    harfbuzz_features = [HarfBuzz.feature_from_string(b'liga 0')[1], HarfBuzz.feature_from_string(b'kern 1')[1]]

    def add_font(name, filename, size, ascend, descend, padding_top, padding_bottom):
        fontconfig.Config.get_current().app_font_add_file(filename)

        TextShaper.fonts[name] = dict()
        TextShaper.fonts[name]['filename'] = filename
        face = freetype2.get_default_lib().new_face(filename)
        face.set_char_size(size=size, resolution=72)
        TextShaper.fonts[name]['face'] = face
        TextShaper.fonts[name]['ascend'] = ascend
        TextShaper.fonts[name]['descend'] = -descend
        TextShaper.fonts[name]['line_height'] = TextShaper.fonts[name]['ascend'] - TextShaper.fonts[name]['descend']
        TextShaper.fonts[name]['padding_top'] = padding_top
        TextShaper.fonts[name]['padding_bottom'] = padding_bottom
        harfbuzz_blob = HarfBuzz.blob_create_from_file_or_fail(filename)
        harfbuzz_face = HarfBuzz.face_create(harfbuzz_blob, 0)
        TextShaper.fonts[name]['harfbuzz_font'] = HarfBuzz.font_create(harfbuzz_face)
        HarfBuzz.font_set_scale(TextShaper.fonts[name]['harfbuzz_font'], size * 64, size * 64)
        TextShaper.fonts[name]['char_extents'] = dict()

    def get_descend(fontname='book'):
        return TextShaper.fonts[fontname]['descend']

    def get_ascend(fontname='book'):
        return TextShaper.fonts[fontname]['ascend']

    def get_padding_top(fontname='book'):
        return TextShaper.fonts[fontname]['padding_top']

    def get_padding_bottom(fontname='book'):
        return TextShaper.fonts[fontname]['padding_bottom']

    def measure_single(char, fontname='book'):
        if char not in TextShaper.fonts[fontname]['char_extents']:
            TextShaper.load_glyph(char, fontname)

        return TextShaper.fonts[fontname]['char_extents'][char]

    @timer.timer
    def measure(text, fontname='book'):
        harfbuzz_buffer = TextShaper.harfbuzz_buffer
        HarfBuzz.buffer_reset(harfbuzz_buffer)
        HarfBuzz.buffer_add_utf8(harfbuzz_buffer, text.encode('utf8'), 0, -1)
        HarfBuzz.buffer_guess_segment_properties(harfbuzz_buffer)
        HarfBuzz.shape(TextShaper.fonts[fontname]['harfbuzz_font'], harfbuzz_buffer, TextShaper.harfbuzz_features)
        positions = HarfBuzz.buffer_get_glyph_positions(harfbuzz_buffer)

        result = []
        for pos, char in zip(positions, text):
            if char not in TextShaper.fonts[fontname]['char_extents']:
                TextShaper.load_glyph(char, fontname)
            extents = TextShaper.fonts[fontname]['char_extents'][char][:]
            extents[0] = int(pos.x_advance / 64)
            result.append(extents)

        return result

    def load_glyph(char, fontname):
        if fontname == 'emojis':
            TextShaper.load_emoji(char)
        else:
            TextShaper.load_glyph_from_font(char, fontname)

    def load_emoji(char):
        TextShaper.fonts['emojis']['face'].load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
        TextShaper.fonts['emojis']['face'].glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

        width = TextShaper.fonts['emojis']['face'].glyph.advance.x
        height = TextShaper.fonts['emojis']['line_height']

        TextShaper.fonts['emojis']['char_extents'][char] = [width, height]

    def load_glyph_from_font(char, fontname):
        TextShaper.fonts[fontname]['face'].load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
        TextShaper.fonts[fontname]['face'].glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

        width = TextShaper.fonts[fontname]['face'].glyph.advance.x
        height = TextShaper.fonts[fontname]['line_height']

        TextShaper.fonts[fontname]['char_extents'][char] = [width, height]


