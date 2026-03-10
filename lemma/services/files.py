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

import os.path, shutil, subprocess


from lemma.services.paths import Paths


class Files():

    image_format_dict = {'BLP': '.blp', 'BMP': '.bmp', 'DIB': '.dib', 'BUFR': '.bufr', 'CUR': '.cur', 'PCX': '.pcx', 'DCX': '.dcx', 'DDS': '.dds', 'EPS': '.eps', 'FITS': '.fit', 'FLI': '.flc', 'FPX': '.fpx', 'FTEX': '.ftc', 'GBR': '.gbr', 'GIF': '.gif', 'GRIB': '.grib', 'HDF5': '.hdf', 'PNG': '.png', 'JPEG2000': '.jp2', 'ICNS': '.icns', 'ICO': '.ico', 'IM': '.im', 'IPTC': '.iim', 'JPEG': '.jpg', 'TIFF': '.tif', 'MIC': '.mic', 'MPEG': '.mpg', 'MSP': '.msp', 'PCD': '.pcd', 'PIXAR': '.pxr', 'PPM': '.ppm', 'PSD': '.psd', 'QOI': '.qoi', 'SGI': '.sgi', 'SUN': '.ras', 'TGA': '.tga', 'WEBP': '.webp', 'WMF': '.wmf', 'XBM': '.xbm', 'XPM': '.xpm'}

    def get_extension_from_image_format(image_format):
        return Files.image_format_dict[image_format]

    def add_file_with_distinct_name(document, origin):
        target = os.path.join(Paths.get_notes_folder(), str(document.id) + '_files/' + os.path.basename(origin))
        target_full = target

        count = 0
        while str(document.id) + '_files/' + os.path.basename(target_full) in document.files:
            count += 1
            root, ext = os.path.splitext(target)
            target_full = root + '~' + (str(count) if count > 0 else '') + ext

        if not os.path.exists(os.path.dirname(target_full)):
            os.makedirs(os.path.dirname(target_full))

        try:
            shutil.copyfile(origin, target_full)
        except shutil.SameFileError: pass

        return os.path.relpath(target_full, Paths.get_notes_folder())

    def open(filename):
        path = os.path.join(Paths.get_notes_folder(), filename)
        subprocess.call(['xdg-open', path])


