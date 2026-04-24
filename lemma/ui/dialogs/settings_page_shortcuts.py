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
from gi.repository import Gtk, Adw, Gdk

from lemma.services.settings import Settings
from lemma.use_cases.use_cases import UseCases
from lemma.ui.shortcuts import Shortcuts
from lemma.ui.dialogs.dialog_view_action import DialogViewAction


class PageShortcuts(object):

    def __init__(self, settings, main_window):
        self.settings = settings
        self.main_window = main_window

        self.buttons = dict()

        self.sections = list()
        self.sections.append({'title': 'Windows and Panels', 'items': ['show_hamburger_menu', 'show_document_menu', 'show_shortcuts_dialog', 'quit']})
        self.sections.append({'title': 'Documents', 'items': ['add_document', 'rename_document']})
        self.sections.append({'title': 'Navigation', 'items': ['start_global_search', 'go_back', 'go_forward', 'show_bookmarks', 'activate_bookmark_1', 'activate_bookmark_2', 'activate_bookmark_3', 'activate_bookmark_4', 'activate_bookmark_5', 'activate_bookmark_6', 'activate_bookmark_7', 'activate_bookmark_8', 'activate_bookmark_9']})
        self.sections.append({'title': 'Undo and Redo', 'items': ['undo', 'redo']})
        self.sections.append({'title': 'Copy and Paste', 'items': ['cut', 'copy', 'paste']})
        self.sections.append({'title': 'Cursor Movement', 'items': ['go_to_parent_node', 'extend_selection', 'select_all']})
        self.sections.append({'title': 'Actions', 'items': ['toggle_checkbox', 'link_popover']})
        self.sections.append({'title': 'Formatting', 'items': ['toggle_bold', 'toggle_italic', 'toggle_verbatim', 'toggle_highlight', 'paragraph_style_h2', 'paragraph_style_h3', 'paragraph_style_h4', 'paragraph_style_h5', 'paragraph_style_h6', 'paragraph_style_ul', 'paragraph_style_ol', 'paragraph_style_cl', 'paragraph_style_p']})
        self.sections.append({'title': 'Math', 'items': ['subscript', 'superscript']})

        self.view = PageShortcutsView()

    def init(self):
        is_first = True
        for section in self.sections:
            subheader = Gtk.Label.new(section['title'])
            subheader.add_css_class('settings-header')
            subheader.set_xalign(0)
            if is_first:
                subheader.add_css_class('first')
                is_first = False

            self.view.vbox.append(subheader)

            for item in section['items']:
                box = Gtk.CenterBox()
                box.set_start_widget(Gtk.Label.new(_(Shortcuts.get_title(item))))
                box.set_end_widget(Adw.ShortcutLabel.new(Shortcuts.get_trigger_string(item)))
                button = Gtk.Button()
                button.add_css_class('item')
                button.add_css_class('flat')
                button.set_child(box)
                button.connect('clicked', self.on_item_clicked, item)
                self.buttons[item] = button

                self.view.vbox.append(button)

        self.view.reset_button.connect('clicked', self.on_reset_clicked)

    def on_item_clicked(self, button, item):
        self.dialog = SetShortcutDialog(self.settings.view)
        self.dialog.cancel_button.connect('clicked', self.on_dialog_cancel_clicked)
        self.dialog.submit_button.connect('clicked', self.on_dialog_submit_clicked)
        self.dialog.shortcuts_controller.add_cb('submit_dialog', self.submit)
        self.dialog.run(item)

    def on_dialog_cancel_clicked(self, button):
        self.dialog.close()

    def on_dialog_submit_clicked(self, button):
        self.submit()

    def submit(self):
        trigger = self.dialog.trigger_string
        if trigger != '':
            sc_with_trigger = Shortcuts.get_name_by_trigger_string(trigger)
            if sc_with_trigger != None:
                Shortcuts.set_shortcut(sc_with_trigger, '')

        Shortcuts.set_shortcut(self.dialog.key, self.dialog.trigger_string)
        self.dialog.close()

        box = self.buttons[self.dialog.key].get_child()
        box.set_end_widget(Adw.ShortcutLabel.new(Shortcuts.get_trigger_string(self.dialog.key)))

    def on_reset_clicked(self, button):
        Shortcuts.reset_to_defaults()

        for key, button in self.buttons.items():
            button.get_child().set_end_widget(Adw.ShortcutLabel.new(Shortcuts.get_trigger_string(key)))


class SetShortcutDialog(DialogViewAction):

    def __init__(self, main_dialog):
        DialogViewAction.__init__(self, main_dialog, _('Set Shortcut'), 450, 'set-shortcut-dialog', _('Set Shortcut'))
        self.add_css_class('no-border')
        self.add_css_class('set-shortcut-dialog')

        self.explainer_label = Gtk.Label()
        self.explainer_label.set_xalign(0)
        self.explainer_label.set_margin_top(6)
        self.explainer_label.add_css_class('settings-margin-box')
        self.content.append(self.explainer_label)

        self.shortcuts_label_box_inner = Gtk.CenterBox()
        self.shortcuts_label_box_outer = Gtk.CenterBox()
        self.shortcuts_label_box_outer.set_orientation(Gtk.Orientation.VERTICAL)
        self.shortcuts_label_box_outer.set_size_request(-1, 290)
        self.shortcuts_label_box_outer.set_center_widget(self.shortcuts_label_box_inner)
        self.content.append(self.shortcuts_label_box_outer)

        self.warning_label = Gtk.Label()
        self.warning_label.set_wrap(True)
        self.warning_label.set_xalign(0)
        self.warning_label.add_css_class('warning-box')

        self.warning_label_revealer = Gtk.Revealer()
        self.warning_label_revealer.set_child(self.warning_label)
        self.warning_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.warning_label_revealer.set_reveal_child(False)

        self.content.append(self.warning_label_revealer)

        self.reset_button = Gtk.Button.new_with_label('Remove')
        self.reset_button.add_css_class('destructive-action')
        self.reset_button.set_sensitive(False)
        self.reset_button.connect('clicked', self.on_reset_button_clicked)
        self.action_bar.pack_start(self.reset_button)

        self.key = None
        self.trigger_string = ''
        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.add_controller(self.key_controller)

    def run(self, key):
        self.key = key
        self.explainer_label.set_markup('Enter a new shortcut for <b>' + Shortcuts.get_title(key) + '</b>.')
        self.trigger_string = Shortcuts.get_trigger_string(key)
        self.update()
        self.present()

    def on_keypress(self, controller, keyval, keycode, keyboard_state):
        if Gdk.keyval_name(keyval).startswith('Control'): return
        if Gdk.keyval_name(keyval).startswith('Shift'): return
        if Gdk.keyval_name(keyval).startswith('Alt'): return
        if Gdk.keyval_name(keyval).startswith('Super'): return
        if Gdk.keyval_name(keyval).startswith('Return'): return

        self.trigger_string = Gtk.accelerator_name(keyval, keyboard_state)
        self.update()

        return True

    def on_reset_button_clicked(self, button):
        self.trigger_string = ''
        self.update()

    def update(self):
        if self.trigger_string != '':
            sc_with_trigger = Shortcuts.get_name_by_trigger_string(self.trigger_string)
            if sc_with_trigger != None and sc_with_trigger != self.key:
                self.warning_label.set_markup('<b>' + Shortcuts.get_for_labels(sc_with_trigger) + _('</b> is already being used for <i>') + Shortcuts.get_title(sc_with_trigger) + _('</i>. If you set it, <i>') + Shortcuts.get_title(sc_with_trigger) + _('</i> will be disabled.'))
                self.warning_label_revealer.set_reveal_child(True)
            else:
                self.warning_label_revealer.set_reveal_child(False)

            self.shortcuts_label_box_inner.set_center_widget(Adw.ShortcutLabel.new(self.trigger_string))
            self.reset_button.set_sensitive(True)
            self.submit_button.set_label(_('Set Shortcut'))
        else:
            self.warning_label_revealer.set_reveal_child(False)
            self.shortcuts_label_box_inner.set_center_widget(None)
            self.reset_button.set_sensitive(False)
            self.submit_button.set_label(_('Set No Shortcut'))


class PageShortcutsView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('settings-page')
        self.get_style_context().add_class('settings-page-shortcuts')

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.vbox)

        self.reset_button = Gtk.Button.new_with_label('Reset to Defaults')
        self.reset_button.add_css_class('destructive-action')
        self.reset_button.add_css_class('flat')

        info_label = Gtk.Label.new(_('Click on the shortcuts above to change them. You may have to restart Lemma for changes to take full effect.'))
        info_label.set_xalign(0)
        info_label.set_wrap(True)

        bottom_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        bottom_box.add_css_class('settings-bottom-box')
        bottom_box.append(info_label)
        bottom_box.append(self.reset_button)

        self.append(self.scrolled_window)
        self.append(bottom_box)


