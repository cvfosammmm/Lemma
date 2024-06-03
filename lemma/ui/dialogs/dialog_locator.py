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

import os.path


class DialogLocator(object):

    dialogs = dict()

    def init_dialogs(main_window):
        for (path, directories, files) in os.walk(os.path.dirname(os.path.realpath(__file__))):
            if 'dialog.py' in files:
                name = os.path.basename(path)
                exec('import lemma.ui.dialogs.' + name + '.dialog as ' + name)
                exec('DialogLocator.dialogs["' + name + '"] = ' + name + '.Dialog(main_window)')

    def get_dialog(dialog_type):
        return DialogLocator.dialogs[dialog_type]


