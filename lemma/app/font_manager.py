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

    def add_font(name, filename, size, line_height):
        fontconfig.Config.get_current().app_font_add_file(filename)

        FontManager.fonts[name] = dict()
        FontManager.fonts[name]['filename'] = filename
        face = freetype2.get_default_lib().new_face(filename)
        face.set_char_size(size=size, resolution=72)
        FontManager.fonts[name]['face'] = face
        FontManager.fonts[name]['ppem'] = face.size['metrics']['x_ppem']
        FontManager.fonts[name]['ppex'] = face.size['metrics']['y_ppem']
        FontManager.fonts[name]['thinspace'] = int(face.size['metrics']['x_ppem'] / 6)
        FontManager.fonts[name]['medspace'] = int(2 * face.size['metrics']['x_ppem'] / 9)
        FontManager.fonts[name]['thickspace'] = int(5 * face.size['metrics']['x_ppem'] / 18)
        FontManager.fonts[name]['line_height'] = line_height
        FontManager.fonts[name]['harfbuzz_font'] = harfbuzz.Font.ft_create(face)
        FontManager.fonts[name]['char_extents'] = dict()
        FontManager.fonts[name]['surface_cache'] = dict()

    def get_line_height(fontname='book'):
        return FontManager.fonts[fontname]['line_height']

    def get_ppem(fontname='book'):
        return FontManager.fonts[fontname]['ppem']

    def get_ppex(fontname='book'):
        return FontManager.fonts[fontname]['ppex']

    def get_thinspace(fontname='book'):
        return FontManager.fonts[fontname]['thinspace']

    def get_medspace(fontname='book'):
        return FontManager.fonts[fontname]['medspace']

    def get_thickspace(fontname='book'):
        return FontManager.fonts[fontname]['thickspace']

    def get_char_extents_single(char, fontname='book'):
        if char not in FontManager.fonts[fontname]['char_extents']:
            FontManager.load_glyph(char, fontname=fontname)

        return FontManager.fonts[fontname]['char_extents'][char]
 
    def get_char_extents_multi(text, fontname='book'):
        harfbuzz_buffer = harfbuzz.Buffer.create()
        harfbuzz_buffer.add_str(text)
        harfbuzz_buffer.guess_segment_properties()
        features = (harfbuzz.Feature(tag = harfbuzz.HB.TAG(b'liga'), value = 0), harfbuzz.Feature(tag = harfbuzz.HB.TAG(b'kern'), value = 1))
        harfbuzz.shape(FontManager.fonts[fontname]['harfbuzz_font'], harfbuzz_buffer, features)
        positions = harfbuzz_buffer.glyph_positions

        result = []
        for i, char in enumerate(text):
            if char not in FontManager.fonts[fontname]['char_extents']:
                FontManager.load_glyph(char, fontname=fontname)
            extents = FontManager.fonts[fontname]['char_extents'][char][:]
            extents[0] = int(positions[i].x_advance)
            result.append(extents)

        return result
 
    def get_surface(char, fontname='book'):
        if char not in FontManager.fonts[fontname]['surface_cache']:
            FontManager.load_glyph(char, fontname=fontname)

        return FontManager.fonts[fontname]['surface_cache'][char]

    def load_glyph(char, fontname='book'):
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


