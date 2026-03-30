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
from xdg.BaseDirectory import xdg_config_home


class Files():

    resources_folder = None

    image_format_dict = {'BLP': '.blp', 'BMP': '.bmp', 'DIB': '.dib', 'BUFR': '.bufr', 'CUR': '.cur', 'PCX': '.pcx', 'DCX': '.dcx', 'DDS': '.dds', 'EPS': '.eps', 'FITS': '.fit', 'FLI': '.flc', 'FPX': '.fpx', 'FTEX': '.ftc', 'GBR': '.gbr', 'GIF': '.gif', 'GRIB': '.grib', 'HDF5': '.hdf', 'PNG': '.png', 'JPEG2000': '.jp2', 'ICNS': '.icns', 'ICO': '.ico', 'IM': '.im', 'IPTC': '.iim', 'JPEG': '.jpg', 'TIFF': '.tif', 'MIC': '.mic', 'MPEG': '.mpg', 'MSP': '.msp', 'PCD': '.pcd', 'PIXAR': '.pxr', 'PPM': '.ppm', 'PSD': '.psd', 'QOI': '.qoi', 'SGI': '.sgi', 'SUN': '.ras', 'TGA': '.tga', 'WEBP': '.webp', 'WMF': '.wmf', 'XBM': '.xbm', 'XPM': '.xpm'}

    def init(resources_folder):
        Files.resources_folder = resources_folder

        pathname = Files.get_user_themes_folder()
        if not os.path.exists(pathname): os.makedirs(pathname)

        pathname = Files.get_documents_folder()
        if not os.path.exists(pathname): os.makedirs(pathname)

        pathname = Files.get_stubs_folder()
        if not os.path.exists(pathname): os.makedirs(pathname)

        pathname = Files.get_config_folder()
        if not os.path.isdir(pathname): os.makedirs(pathname)

    def get_config_folder():
        return os.path.join(xdg_config_home, 'lemma')

    def get_user_themes_folder():
        return os.path.expanduser(Files.get_config_folder() + '/themes')

    def get_resources_folder():
        return Files.resources_folder

    def get_extension_from_image_format(image_format):
        return Files.image_format_dict[image_format]

    def get_documents_folder():
        return os.path.expanduser(Files.get_config_folder() + '/notes')

    def get_stubs_folder():
        return os.path.expanduser(Files.get_config_folder() + '/stubs')

    def get_document_files_list(document_id):
        folder = os.path.join(Files.get_documents_folder(), str(document_id) + '_files')
        if not os.path.exists(folder):
            return []
        else:
            return [str(document_id) + '_files/' + direntry.name for direntry in os.scandir(folder)]

    def add_file_to_doc_folder_with_distinct_name(document, origin):
        target = os.path.join(Files.get_documents_folder(), str(document.id) + '_files/' + os.path.basename(origin))
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

        return os.path.relpath(target_full, Files.get_documents_folder())

    def open_document_file(filename):
        path = os.path.join(Files.get_documents_folder(), filename)
        subprocess.call(['xdg-open', path])

    def get_document_file_size(filename):
        path = os.path.join(Files.get_documents_folder(), filename)
        try:
            return os.path.getsize(path)
        except FileNotFoundError: return 0

    def change_document_file_name(name_from, name_to):
        origin = os.path.join(Files.get_documents_folder(), name_from)
        new_name = os.path.join(Files.get_documents_folder(), name_to)

        try:
            shutil.copyfile(origin, new_name)
        except shutil.SameFileError: pass

    def delete_document_file(filename):
        path = os.path.join(Files.get_documents_folder(), filename)
        try:
            os.remove(path)
        except FileNotFoundError: pass

    def delete_all_document_files(document_id):
        folder = os.path.join(Files.get_documents_folder(), str(document_id) + '_files')
        if os.path.exists(folder):
            shutil.rmtree(folder)


