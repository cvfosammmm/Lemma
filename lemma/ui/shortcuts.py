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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from lemma.services.files import Files


class Shortcuts():

    defaults = dict()
    data = dict()

    def init():
        Shortcuts.defaults['close_dialog'] = 'Escape'

        Shortcuts.defaults['toggle_bold'] = '<Control>b'
        Shortcuts.defaults['toggle_italic'] = '<Control>i'
        Shortcuts.defaults['toggle_verbatim'] = '<Control>e'
        Shortcuts.defaults['toggle_highlight'] = '<Control>u'
        Shortcuts.defaults['link_popover'] = '<Control>l'
        Shortcuts.defaults['subscript'] = '<Control>minus'
        Shortcuts.defaults['superscript'] = '<Control>underscore'
        Shortcuts.defaults['toggle_checkbox'] = '<Control>m'
        Shortcuts.defaults['undo'] = '<Control>z'
        Shortcuts.defaults['redo'] = '<Control><Shift>z'
        Shortcuts.defaults['cut'] = '<Control>x'
        Shortcuts.defaults['copy'] = '<Control>c'
        Shortcuts.defaults['paste'] = '<Control>v'
        Shortcuts.defaults['select_all'] = '<Control>a'
        Shortcuts.defaults['paragraph_style_h2'] = '<Control>2'
        Shortcuts.defaults['paragraph_style_h3'] = '<Control>3'
        Shortcuts.defaults['paragraph_style_h4'] = '<Control>4'
        Shortcuts.defaults['paragraph_style_h5'] = '<Control>5'
        Shortcuts.defaults['paragraph_style_h6'] = '<Control>6'
        Shortcuts.defaults['paragraph_style_ul'] = '<Control>7'
        Shortcuts.defaults['paragraph_style_ol'] = '<Control>8'
        Shortcuts.defaults['paragraph_style_cl'] = '<Control>9'
        Shortcuts.defaults['paragraph_style_p'] = '<Control>0'
        Shortcuts.defaults['rename_document'] = 'F2'

        Shortcuts.defaults['quit'] = '<Control>q'
        Shortcuts.defaults['add_document'] = '<Control>n'
        Shortcuts.defaults['go_back'] = '<Alt>Left'
        Shortcuts.defaults['go_forward'] = '<Alt>Right'
        Shortcuts.defaults['show_shortcuts_dialog'] = '<Control>question'
        Shortcuts.defaults['show_hamburger_menu'] = 'F10'
        Shortcuts.defaults['show_document_menu'] = 'F12'
        Shortcuts.defaults['show_bookmarks'] = '<Alt>0'
        for i in range(1, 10):
            Shortcuts.defaults['activate_bookmark_' + str(i)] = '<Alt>' + str(i)

        Shortcuts.defaults['start_global_search'] = '<Control>f'
        Shortcuts.defaults['stop_global_search'] = 'Escape'
        Shortcuts.defaults['global_search_prev_result'] = 'Up'
        Shortcuts.defaults['global_search_next_result'] = 'Down'

    def new_controller():
        return ShortcutController()

    def get_trigger_string(name):
        try: value = Shortcuts.data[name]
        except KeyError:
            value = Shortcuts.defaults[name]

        return value

    def get_for_labels(name):
        try: value = Shortcuts.data[name]
        except KeyError:
            value = Shortcuts.defaults[name]

        value = value.replace('minus', '-')
        value = value.replace('underscore', '_')
        value = value.replace('question', '?')

        value = value.replace('>a', '>A')
        value = value.replace('>b', '>B')
        value = value.replace('>c', '>C')
        value = value.replace('>d', '>D')
        value = value.replace('>e', '>E')
        value = value.replace('>f', '>F')
        value = value.replace('>g', '>G')
        value = value.replace('>h', '>H')
        value = value.replace('>i', '>I')
        value = value.replace('>j', '>J')
        value = value.replace('>k', '>K')
        value = value.replace('>l', '>L')
        value = value.replace('>m', '>M')
        value = value.replace('>n', '>N')
        value = value.replace('>o', '>O')
        value = value.replace('>p', '>P')
        value = value.replace('>q', '>Q')
        value = value.replace('>r', '>R')
        value = value.replace('>s', '>S')
        value = value.replace('>t', '>T')
        value = value.replace('>u', '>U')
        value = value.replace('>v', '>V')
        value = value.replace('>w', '>W')
        value = value.replace('>x', '>X')
        value = value.replace('>y', '>Y')
        value = value.replace('>z', '>Z')

        value = value.replace('Escape', 'Esc')

        return value.replace('<Control>', 'Ctrl+').replace('<Shift>', 'Shift+').replace('<Alt>', 'Alt+')


class ShortcutController(Gtk.ShortcutController):

    def __init__(self):
        Gtk.ShortcutController.__init__(self)

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

    def add_cb(self, name, callback, data=None):
        callback_action = Gtk.CallbackAction.new(self.action, (callback, data))
        trigger_string = Shortcuts.get_trigger_string(name)

        shortcut = Gtk.Shortcut()
        shortcut.set_action(callback_action)
        shortcut.set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

        self.add_shortcut(shortcut)

    def action(self, a, b, arguments):
        callback, data = arguments
        if data != None:
            callback(data)
        else:
            callback()
        return True


