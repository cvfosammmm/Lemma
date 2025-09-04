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
import lemma.services.timer as timer

from lemma.services.paths import Paths


class TextRenderer():

    fonts = dict()

    def add_font(name, filename, size, ascend, descend):
        TextRenderer.fonts[name] = dict()
        TextRenderer.fonts[name]['size'] = size
        TextRenderer.fonts[name]['filename'] = filename
        TextRenderer.fonts[name]['face'] = freetype2.get_default_lib().new_face(filename)
        TextRenderer.fonts[name]['ascend'] = ascend
        TextRenderer.fonts[name]['descend'] = -descend
        TextRenderer.fonts[name]['line_height'] = ascend + descend
        TextRenderer.fonts[name]['cache'] = dict()

    def get_glyph(char, fontname='book', scale=1):
        if char + '-' + str(scale) not in TextRenderer.fonts[fontname]['cache']:
            TextRenderer.load_glyph(char, fontname, scale)

        return TextRenderer.fonts[fontname]['cache'][char + '-' + str(scale)]

    def load_glyph(char, fontname, scale=1):
        if fontname == 'emojis':
            TextRenderer.load_emoji(char, scale)
        else:
            TextRenderer.load_glyph_from_font(char, fontname, scale)

    def load_emoji(char, scale):
        TextRenderer.fonts['emojis']['face'].set_char_size(size=TextRenderer.fonts['emojis']['size'] * scale, resolution=72)
        TextRenderer.fonts['emojis']['face'].load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
        TextRenderer.fonts['emojis']['face'].glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

        width = TextRenderer.fonts['emojis']['face'].glyph.advance.x
        height = TextRenderer.fonts['emojis']['line_height']
        left = 0
        top = -TextRenderer.fonts['emojis']['ascend']

        viewport = Rsvg.Rectangle()
        viewport.x = 0
        viewport.y = 0
        viewport.width = width
        viewport.height = height

        surface = cairo.ImageSurface(cairo.Format.ARGB32, int(width), int(height))
        ctx = cairo.Context(surface)

        res_path = Paths.get_resources_folder()
        filename = 'emoji_u' + hex(ord(char))[2:] + '.svg'
        rsvg_handle = Rsvg.Handle.new_from_file(os.path.join(res_path, 'fonts/Noto_Color_Emoji/svg', filename))
        rsvg_handle.render_document(ctx, viewport)

        TextRenderer.fonts['emojis']['cache'][char + '-' + str(scale)] = (surface, left, top)

    def load_glyph_from_font(char, fontname, scale):
        TextRenderer.fonts[fontname]['face'].set_char_size(size=TextRenderer.fonts[fontname]['size'] * scale, resolution=72)
        TextRenderer.fonts[fontname]['face'].load_char(ord(char), freetype2.FT.LOAD_DEFAULT)
        TextRenderer.fonts[fontname]['face'].glyph.render_glyph(freetype2.FT.RENDER_MODE_NORMAL)

        left = TextRenderer.fonts[fontname]['face'].glyph.bitmap_left
        top = -TextRenderer.fonts[fontname]['face'].glyph.bitmap_top

        if TextRenderer.fonts[fontname]['face'].glyph.bitmap.width > 0:
            TextRenderer.fonts[fontname]['cache'][char + '-' + str(scale)] = (TextRenderer.fonts[fontname]['face'].glyph.bitmap.make_image_surface(), left, top)
        else:
            TextRenderer.fonts[fontname]['cache'][char + '-' + str(scale)] = (None, 0, 0)


