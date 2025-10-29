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


class Dialog():

    def __init__(self, main_window):
        self.main_window = main_window

        data = list()

        section = {'title': 'Windows and Panels', 'items': list()}
        section['items'].append({'title': 'Show Global Menu', 'shortcut': 'F10'})
        section['items'].append({'title': 'Show Document Menu', 'shortcut': 'F12'})
        section['items'].append({'title': 'Show Symbols Sidebar', 'shortcut': '&lt;alt&gt;1'})
        section['items'].append({'title': 'Show Emojis Sidebar', 'shortcut': '&lt;alt&gt;2'})
        section['items'].append({'title': 'Show Keyboard Shortcuts', 'shortcut': '&lt;ctrl&gt;question'})
        section['items'].append({'title': 'Quit the Application', 'shortcut': '&lt;ctrl&gt;Q'})
        data.append(section)

        section = {'title': 'Documents', 'items': list()}
        section['items'].append({'title': 'Create new Document', 'shortcut': '&lt;ctrl&gt;N'})
        section['items'].append({'title': 'Rename Document', 'shortcut': 'F2'})
        data.append(section)

        section = {'title': 'Navigation', 'items': list()}
        section['items'].append({'title': 'Search', 'shortcut': '&lt;ctrl&gt;F'})
        section['items'].append({'title': 'Go Back', 'shortcut': '&lt;alt&gt;Left'})
        section['items'].append({'title': 'Go Forward', 'shortcut': '&lt;alt&gt;Right'})
        data.append(section)

        section = {'title': 'Undo and Redo', 'items': list()}
        section['items'].append({'title': 'Undo', 'shortcut': '&lt;ctrl&gt;Z'})
        section['items'].append({'title': 'Redo', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;Z'})
        data.append(section)

        section = {'title': 'Copy and Paste', 'items': list()}
        section['items'].append({'title': 'Copy', 'shortcut': '&lt;ctrl&gt;C'})
        section['items'].append({'title': 'Cut', 'shortcut': '&lt;ctrl&gt;X'})
        section['items'].append({'title': 'Paste', 'shortcut': '&lt;ctrl&gt;V'})
        data.append(section)

        section = {'title': 'Cursor Movement', 'items': list()}
        section['items'].append({'title': 'Go to Parent Node', 'shortcut': '&lt;ctrl&gt;Up'})
        section['items'].append({'title': 'Extend Selection', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;Up'})
        section['items'].append({'title': 'Select All', 'shortcut': '&lt;ctrl&gt;A'})
        section['items'].append({'title': 'Jump Left', 'shortcut': '&lt;ctrl&gt;Left'})
        section['items'].append({'title': 'Jump Right', 'shortcut': '&lt;ctrl&gt;Right'})
        section['items'].append({'title': 'Select Next Placeholder', 'shortcut': 'Tab'})
        section['items'].append({'title': 'Select Previous Placeholder', 'shortcut': '&lt;shift&gt;Tab'})
        data.append(section)

        section = {'title': 'Formatting', 'items': list()}
        section['items'].append({'title': 'Bold Text', 'shortcut': '&lt;ctrl&gt;B'})
        section['items'].append({'title': 'Italic Text', 'shortcut': '&lt;ctrl&gt;I'})
        section['items'].append({'title': 'Heading 2', 'shortcut': '&lt;ctrl&gt;2'})
        section['items'].append({'title': 'Heading 3', 'shortcut': '&lt;ctrl&gt;3'})
        section['items'].append({'title': 'Heading 4', 'shortcut': '&lt;ctrl&gt;4'})
        section['items'].append({'title': 'Heading 5', 'shortcut': '&lt;ctrl&gt;5'})
        section['items'].append({'title': 'Heading 6', 'shortcut': '&lt;ctrl&gt;6'})
        section['items'].append({'title': 'Bullet List', 'shortcut': '&lt;ctrl&gt;7'})
        section['items'].append({'title': 'Normal Paragraph', 'shortcut': '&lt;ctrl&gt;0'})
        data.append(section)

        section = {'title': 'Math', 'items': list()}
        section['items'].append({'title': 'Subscript', 'shortcut': '&lt;ctrl&gt;minus'})
        section['items'].append({'title': 'Superscript', 'shortcut': '&lt;ctrl&gt;underscore'})
        data.append(section)

        self.data = data

    def run(self):
        self.setup()
        self.view.present()

    def setup(self):
        builder_string = '''<?xml version="1.0" encoding="UTF-8"?>
<interface>

  <object class="GtkShortcutsWindow" id="shortcuts-window">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="visible">1</property>
        <property name="section-name">shortcuts</property>
        <property name="max-height">12</property>
'''

        for section in self.data:
            builder_string += '''        <child>
          <object class="GtkShortcutsGroup">
            <property name="visible">1</property>
            <property name="title" translatable="no">''' + section['title'] + '''</property>
'''

            for item in section['items']:
                builder_string += '''            <child>
              <object class="GtkShortcutsShortcut">
                <property name="visible">1</property>
                <property name="accelerator">''' + item['shortcut'] + '''</property>
                <property name="title" translatable="no">''' + item['title'] + '''</property>
              </object>
            </child>
'''

            builder_string += '''          </object>
        </child>
'''

        builder_string += '''      </object>
    </child>
  </object>

</interface>'''

        builder = Gtk.Builder.new_from_string(builder_string, -1)
        self.view = builder.get_object('shortcuts-window')
        self.view.set_transient_for(self.main_window)


