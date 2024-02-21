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

import lib.freetype2.freetype2 as freetype2
import lib.harfpy.harfbuzz as harfbuzz
import lib.fontconfig.fontconfig as fontconfig


class FontManager():

    fonts = dict()
    face = None
    char_extents = dict()
    surface_cache = dict()
    line_height = 0

    def add_font(name, filename):
        FontManager.fonts[name] = filename
        fontconfig.Config.get_current().app_font_add_file(filename)

    def set_text_font(name, size):
        filename = FontManager.fonts[name]
        FontManager.face = freetype2.get_default_lib().new_face(filename)
        FontManager.face.set_char_size(size=size, resolution=72)
        FontManager.line_height = FontManager.face.height // 72 + 8
        FontManager.harfbuzz_font = harfbuzz.Font.ft_create(FontManager.face)

    def get_char_extents_single(char):
        if char not in FontManager.char_extents:
            FontManager.load_glyph(char)

        return FontManager.char_extents[char]
 
    def get_char_extents_multi(text):
        harfbuzz_buffer = harfbuzz.Buffer.create()
        harfbuzz_buffer.add_str(text)
        harfbuzz_buffer.guess_segment_properties()
        features = (harfbuzz.Feature(tag = harfbuzz.HB.TAG(b'liga'), value = 0), harfbuzz.Feature(tag = harfbuzz.HB.TAG(b'kern'), value = 1))
        harfbuzz.shape(FontManager.harfbuzz_font, harfbuzz_buffer, features)
        positions = harfbuzz_buffer.glyph_positions

        result = []
        for i, char in enumerate(text):
            if char not in FontManager.char_extents:
                FontManager.load_glyph(char)
            extents = FontManager.char_extents[char][:]
            extents[0] = int(positions[i].x_advance)
            result.append(extents)

        return result
 
    def get_surface(char):
        if char not in FontManager.surface_cache:
            FontManager.load_glyph(char)

        return FontManager.surface_cache[char]

    def load_glyph(char):
        if char not in FontManager.char_extents:
            #FontManager.face.load_char(ord(char), freetype2.FT.LOAD_FORCE_AUTOHINT)
            FontManager.face.load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
            FontManager.face.glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

            width = FontManager.face.glyph.advance.x
            height = FontManager.line_height
            left = FontManager.face.glyph.bitmap_left
            top = - FontManager.face.glyph.bitmap_top

            FontManager.char_extents[char] = [width, height, left, top]
            if FontManager.face.glyph.bitmap.width > 0:
                FontManager.surface_cache[char] = FontManager.face.glyph.bitmap.make_image_surface()
            else:
                FontManager.surface_cache[char] = None


