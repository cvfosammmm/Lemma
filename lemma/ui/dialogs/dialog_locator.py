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

import lemma.ui.dialogs.about as about
import lemma.ui.dialogs.export_bulk as export_bulk
import lemma.ui.dialogs.export_markdown as export_markdown
import lemma.ui.dialogs.import_documents as import_documents
import lemma.ui.dialogs.insert_image as insert_image
import lemma.ui.dialogs.keyboard_shortcuts as keyboard_shortcuts
import lemma.ui.dialogs.settings as settings


class DialogLocator():

    dialogs = dict()

    def init_dialogs(main_window):
        DialogLocator.dialogs['about'] = about.Dialog(main_window)
        DialogLocator.dialogs['export_bulk'] = export_bulk.Dialog(main_window)
        DialogLocator.dialogs['export_markdown'] = export_markdown.Dialog(main_window)
        DialogLocator.dialogs['import_documents'] = import_documents.Dialog(main_window)
        DialogLocator.dialogs['insert_image'] = insert_image.Dialog(main_window)
        DialogLocator.dialogs['keyboard_shortcuts'] = keyboard_shortcuts.Dialog(main_window)
        DialogLocator.dialogs['settings'] = settings.Dialog(main_window)

    def get_dialog(dialog_type):
        return DialogLocator.dialogs[dialog_type]


