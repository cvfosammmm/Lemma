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
from gi.repository import Gtk, Gdk

import os.path, pickle

from lemma.services.files import Files


class Shortcuts():

    controllers = list()
    defaults = dict()
    data = dict()
    titles = dict()

    def init():
        Shortcuts.defaults['close_dialog'] = 'Escape'
        Shortcuts.defaults['submit_dialog'] = 'Return'
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
        Shortcuts.defaults['go_to_parent_node'] = '<Control>Up'
        Shortcuts.defaults['extend_selection'] = '<Control><Shift>Up'
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

        Shortcuts.titles['show_hamburger_menu'] = 'Show Global Menu'
        Shortcuts.titles['show_document_menu'] = 'Show Document Menu'
        Shortcuts.titles['show_shortcuts_dialog'] = 'Show Keyboard Shortcuts'
        Shortcuts.titles['quit'] = 'Quit the Application'
        Shortcuts.titles['add_document'] = 'Create new Document'
        Shortcuts.titles['rename_document'] = 'Rename Document'
        Shortcuts.titles['start_global_search'] = 'Search'
        Shortcuts.titles['go_back'] = 'Go Back'
        Shortcuts.titles['go_forward'] = 'Go Forward'
        Shortcuts.titles['show_bookmarks'] = 'Show Bookmarks'
        Shortcuts.titles['activate_bookmark_1'] = 'Open Bookmark 1'
        Shortcuts.titles['activate_bookmark_2'] = 'Open Bookmark 2'
        Shortcuts.titles['activate_bookmark_3'] = 'Open Bookmark 3'
        Shortcuts.titles['activate_bookmark_4'] = 'Open Bookmark 4'
        Shortcuts.titles['activate_bookmark_5'] = 'Open Bookmark 5'
        Shortcuts.titles['activate_bookmark_6'] = 'Open Bookmark 6'
        Shortcuts.titles['activate_bookmark_7'] = 'Open Bookmark 7'
        Shortcuts.titles['activate_bookmark_8'] = 'Open Bookmark 8'
        Shortcuts.titles['activate_bookmark_9'] = 'Open Bookmark 9'
        Shortcuts.titles['undo'] = 'Undo'
        Shortcuts.titles['redo'] = 'Redo'
        Shortcuts.titles['cut'] = 'Cut'
        Shortcuts.titles['copy'] = 'Copy'
        Shortcuts.titles['paste'] = 'Paste'
        Shortcuts.titles['toggle_checkbox'] = 'Toggle Checkbox'
        Shortcuts.titles['toggle_bold'] = 'Bold Text'
        Shortcuts.titles['toggle_italic'] = 'Italic Text'
        Shortcuts.titles['toggle_verbatim'] = 'Verbatim Text'
        Shortcuts.titles['toggle_highlight'] = 'Highlight Text'
        Shortcuts.titles['paragraph_style_h2'] = 'Heading 2'
        Shortcuts.titles['paragraph_style_h3'] = 'Heading 3'
        Shortcuts.titles['paragraph_style_h4'] = 'Heading 4'
        Shortcuts.titles['paragraph_style_h5'] = 'Heading 5'
        Shortcuts.titles['paragraph_style_h6'] = 'Heading 6'
        Shortcuts.titles['paragraph_style_ul'] = 'Bullet List'
        Shortcuts.titles['paragraph_style_ol'] = 'Numbered List'
        Shortcuts.titles['paragraph_style_cl'] = 'Checklist'
        Shortcuts.titles['paragraph_style_p'] = 'Normal Paragraph'
        Shortcuts.titles['subscript'] = 'Subscript'
        Shortcuts.titles['superscript'] = 'Superscript'
        Shortcuts.titles['select_all'] = 'Select All'
        Shortcuts.titles['go_to_parent_node'] = 'Go to Parent Node'
        Shortcuts.titles['extend_selection'] = 'Extend Selection'
        Shortcuts.titles['link_popover'] = 'Insert Link'

        Shortcuts.load_from_disk()

    def set_shortcut(name, trigger_string):
        Shortcuts.data[name] = trigger_string

        for controller in Shortcuts.controllers:
            controller.update_trigger(name)

        Shortcuts.save_to_disk()

    def reset_to_defaults():
        Shortcuts.data = dict()

        for controller in Shortcuts.controllers:
            controller.update_triggers()

        Shortcuts.save_to_disk()

    def new_controller():
        controller = ShortcutController()

        Shortcuts.controllers.append(controller)
        return controller

    def get_trigger_string(name):
        try: value = Shortcuts.data[name]
        except KeyError:
            value = Shortcuts.defaults[name]

        return value

    def get_name_by_trigger_string(trigger_string):
        for key in Shortcuts.defaults:
            if Shortcuts.get_trigger_string(key) == trigger_string:
                return key
        return None

    def get_title(name):
        try: value = Shortcuts.titles[name]
        except KeyError:
            value = name
        return value

    def get_for_labels(name):
        try: value = Shortcuts.data[name]
        except KeyError:
            value = Shortcuts.defaults[name]
        return Gtk.ShortcutTrigger.parse_string(value).to_label(Gdk.Display.get_default())

    def load_from_disk():
        try: filehandle = open(os.path.join(Files.get_config_folder(), 'shortcuts.pickle'), 'rb')
        except IOError: return False
        else:
            try: Shortcuts.data = pickle.load(filehandle)
            except EOFError: return False
        return True

    def save_to_disk():
        try: filehandle = open(os.path.join(Files.get_config_folder(), 'shortcuts.pickle'), 'wb')
        except IOError: return False
        else: pickle.dump(Shortcuts.data, filehandle)


class ShortcutController(Gtk.ShortcutController):

    def __init__(self):
        Gtk.ShortcutController.__init__(self)

        self.shortcuts_by_name = dict()

        self.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)

    def add_cb(self, name, callback, data=None):
        callback_action = Gtk.CallbackAction.new(self.action, (callback, data))
        trigger_string = Shortcuts.get_trigger_string(name)

        shortcut = Gtk.Shortcut()
        shortcut.set_action(callback_action)
        shortcut.set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

        self.shortcuts_by_name[name] = shortcut

        self.add_shortcut(shortcut)

    def update_trigger(self, name):
        if name in self.shortcuts_by_name:
            trigger_string = Shortcuts.get_trigger_string(name)
            self.shortcuts_by_name[name].set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

    def update_triggers(self):
        for name in self.shortcuts_by_name:
            trigger_string = Shortcuts.get_trigger_string(name)
            self.shortcuts_by_name[name].set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

    def action(self, a, b, arguments):
        callback, data = arguments
        if data != None:
            callback(data)
        else:
            callback()
        return True


