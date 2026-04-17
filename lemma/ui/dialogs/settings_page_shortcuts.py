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
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from lemma.services.settings import Settings
from lemma.use_cases.use_cases import UseCases
from lemma.ui.shortcuts import Shortcuts


class PageShortcuts(object):

    def __init__(self, settings, main_window):
        self.settings = settings
        self.main_window = main_window

        self.data = list()

        section = {'title': 'Windows and Panels', 'items': list()}
        section['items'].append(['Show Global Menu', Shortcuts.get_trigger_string('show_hamburger_menu')])
        section['items'].append(['Show Document Menu', Shortcuts.get_trigger_string('show_document_menu')])
        section['items'].append(['Show Keyboard Shortcuts', Shortcuts.get_trigger_string('show_shortcuts_dialog')])
        section['items'].append(['Quit the Application', Shortcuts.get_trigger_string('quit')])
        self.data.append(section)

        section = {'title': 'Documents', 'items': list()}
        section['items'].append(['Create new Document', Shortcuts.get_trigger_string('add_document')])
        section['items'].append(['Rename Document', Shortcuts.get_trigger_string('rename_document')])
        self.data.append(section)

        section = {'title': 'Navigation', 'items': list()}
        section['items'].append(['Search', Shortcuts.get_trigger_string('start_global_search')])
        section['items'].append(['Go Back', Shortcuts.get_trigger_string('go_back')])
        section['items'].append(['Go Forward', Shortcuts.get_trigger_string('go_forward')])
        section['items'].append(['Show Bookmarks', Shortcuts.get_trigger_string('show_bookmarks')])
        section['items'].append(['Open Bookmark 1', Shortcuts.get_trigger_string('activate_bookmark_1')])
        section['items'].append(['Open Bookmark 2', Shortcuts.get_trigger_string('activate_bookmark_2')])
        section['items'].append(['Open Bookmark 3', Shortcuts.get_trigger_string('activate_bookmark_3')])
        section['items'].append(['Open Bookmark 4', Shortcuts.get_trigger_string('activate_bookmark_4')])
        section['items'].append(['Open Bookmark 5', Shortcuts.get_trigger_string('activate_bookmark_5')])
        section['items'].append(['Open Bookmark 6', Shortcuts.get_trigger_string('activate_bookmark_6')])
        section['items'].append(['Open Bookmark 7', Shortcuts.get_trigger_string('activate_bookmark_7')])
        section['items'].append(['Open Bookmark 8', Shortcuts.get_trigger_string('activate_bookmark_8')])
        section['items'].append(['Open Bookmark 9', Shortcuts.get_trigger_string('activate_bookmark_9')])
        self.data.append(section)

        section = {'title': 'Undo and Redo', 'items': list()}
        section['items'].append(['Undo', Shortcuts.get_trigger_string('undo')])
        section['items'].append(['Redo', Shortcuts.get_trigger_string('redo')])
        self.data.append(section)

        section = {'title': 'Copy and Paste', 'items': list()}
        section['items'].append(['Cut', Shortcuts.get_trigger_string('cut')])
        section['items'].append(['Copy', Shortcuts.get_trigger_string('copy')])
        section['items'].append(['Paste', Shortcuts.get_trigger_string('paste')])
        self.data.append(section)

        section = {'title': 'Actions', 'items': list()}
        section['items'].append(['Toggle Checkbox', Shortcuts.get_trigger_string('toggle_checkbox')])
        self.data.append(section)

        section = {'title': 'Formatting', 'items': list()}
        section['items'].append(['Bold Text', Shortcuts.get_trigger_string('toggle_bold')])
        section['items'].append(['Italic Text', Shortcuts.get_trigger_string('toggle_italic')])
        section['items'].append(['Verbatim Text', Shortcuts.get_trigger_string('toggle_verbatim')])
        section['items'].append(['Highlight Text', Shortcuts.get_trigger_string('toggle_highlight')])
        section['items'].append(['Heading 2', Shortcuts.get_trigger_string('paragraph_style_h2')])
        section['items'].append(['Heading 3', Shortcuts.get_trigger_string('paragraph_style_h3')])
        section['items'].append(['Heading 4', Shortcuts.get_trigger_string('paragraph_style_h4')])
        section['items'].append(['Heading 5', Shortcuts.get_trigger_string('paragraph_style_h5')])
        section['items'].append(['Heading 6', Shortcuts.get_trigger_string('paragraph_style_h6')])
        section['items'].append(['Bullet List', Shortcuts.get_trigger_string('paragraph_style_ul')])
        section['items'].append(['Numbered List', Shortcuts.get_trigger_string('paragraph_style_ol')])
        section['items'].append(['Checklist', Shortcuts.get_trigger_string('paragraph_style_cl')])
        section['items'].append(['Normal Paragraph', Shortcuts.get_trigger_string('paragraph_style_p')])
        self.data.append(section)

        section = {'title': 'Math', 'items': list()}
        section['items'].append(['Subscript', Shortcuts.get_trigger_string('subscript')])
        section['items'].append(['Superscript', Shortcuts.get_trigger_string('superscript')])
        self.data.append(section)

        self.view = PageShortcutsView(self.data)

    def init(self):
        return
        for i, section in enumerate(self.button_list):
            for item in section:
                self.view.checkboxes[item[1]].connect('toggled', self.on_checkbutton_toggled, item[1])
                self.view.checkboxes[item[1]].set_active(Settings.get_value(item[1]))

    def on_checkbutton_toggled(self, button, key):
        UseCases.settings_set_value(key, button.get_active())


class PageShortcutsView(Gtk.Box):

    def __init__(self, data):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('settings-page')
        self.get_style_context().add_class('settings-page-shortcuts')

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        for section in data:
            subheader = Gtk.Label.new(section['title'])
            subheader.add_css_class('settings-header')
            subheader.set_xalign(0)
            self.vbox.append(subheader)

            for item in section['items']:
                box = Gtk.CenterBox()
                box.set_start_widget(Gtk.Label.new(_(item[0])))
                box.set_end_widget(Adw.ShortcutLabel.new(_(item[1])))
                box.add_css_class('item')

                self.vbox.append(box)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.append(self.scrolled_window)


