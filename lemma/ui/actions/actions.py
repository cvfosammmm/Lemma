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
from gi.repository import Gio, GLib, GObject, Gdk

import pickle

from lemma.document.ast.services import node_inside_link
from lemma.infrastructure.service_locator import ServiceLocator
from lemma.ui.dialogs.dialog_locator import DialogLocator
from lemma.ui.popovers.popover_manager import PopoverManager


class Actions(object):

    def __init__(self, workspace, main_window):
        self.workspace = workspace
        self.main_window = main_window
        self.document_view = main_window.document_view
        self.settings = ServiceLocator.get_settings()

        self.actions = dict()
        self.add_simple_action('add-document', self.add_document)
        self.add_simple_action('import-markdown-files', self.import_markdown_files)
        self.add_simple_action('delete-document', self.delete_document)
        self.add_simple_action('rename-document', self.rename_document)
        self.add_simple_action('export-as', self.export_as)

        self.add_simple_action('go-back', self.go_back)
        self.add_simple_action('go-forward', self.go_forward)

        self.add_simple_action('undo', self.undo)
        self.add_simple_action('redo', self.redo)
        self.add_simple_action('cut', self.cut)
        self.add_simple_action('copy', self.copy)
        self.add_simple_action('paste', self.paste)
        self.add_simple_action('delete', self.delete_selection)
        self.add_simple_action('select-all', self.select_all)

        self.add_simple_action('insert-link', self.insert_link)
        self.add_simple_action('remove-link', self.remove_link)
        self.add_simple_action('insert-matharea', self.insert_matharea)
        self.add_simple_action('insert-symbol', self.insert_symbol, GLib.VariantType('as'))

        self.add_simple_action('trigger-bold-button', self.trigger_bold_button)
        self.add_simple_action('trigger-italic-button', self.trigger_italic_button)

        self.add_simple_action('toggle-tools-sidebar', self.toggle_tools_sidebar)
        self.add_simple_action('show-edit-menu', self.show_edit_menu)
        self.add_simple_action('show-document-menu', self.show_document_menu)
        self.add_simple_action('show-hamburger-menu', self.show_hamburger_menu)
        self.add_simple_action('show-shortcuts-dialog', self.show_shortcuts_dialog)
        self.add_simple_action('show-about-dialog', self.show_about_dialog)

        self.actions['quit'] = Gio.SimpleAction.new('quit', None)
        self.main_window.add_action(self.actions['quit'])

        self.update()

    def add_simple_action(self, name, callback, parameter=None):
        self.actions[name] = Gio.SimpleAction.new(name, parameter)
        self.main_window.add_action(self.actions[name])
        self.actions[name].connect('activate', callback)

    def update(self):
        active_document = self.workspace.active_document
        has_active_doc = (active_document != None)
        prev_doc = self.workspace.history.get_previous_if_any(active_document)
        next_doc = self.workspace.history.get_next_if_any(active_document)
        can_undo = has_active_doc and active_document.can_undo()
        can_redo = has_active_doc and active_document.can_redo()
        insert_in_line = has_active_doc and active_document.ast.get_insert_node().parent.is_root()
        insert_in_matharea = has_active_doc and active_document.ast.get_insert_node().parent.is_matharea()
        has_selection = has_active_doc and active_document.ast.has_selection()
        clipboard_formats = Gdk.Display.get_default().get_clipboard().get_formats().to_string()
        text_in_clipboard = 'text/plain;charset=utf-8' in clipboard_formats
        subtree_in_clipboard = 'lemma/ast' in clipboard_formats
        links_inside_selection = has_active_doc and len([node for node in active_document.ast.get_subtree(*active_document.ast.get_cursor_state()) if node.link != None]) > 0
        cursor_inside_link = has_active_doc and node_inside_link(active_document.ast.get_insert_node())

        self.actions['add-document'].set_enabled(True)
        self.actions['import-markdown-files'].set_enabled(True)
        self.actions['delete-document'].set_enabled(self.workspace.mode == 'documents' and has_active_doc)
        self.actions['rename-document'].set_enabled(self.workspace.mode == 'documents' and has_active_doc)
        self.actions['export-as'].set_enabled(self.workspace.mode == 'documents' and has_active_doc)
        self.actions['go-back'].set_enabled(self.workspace.mode == 'draft' or prev_doc != None)
        self.actions['go-forward'].set_enabled(next_doc != None)
        self.actions['undo'].set_enabled(self.workspace.mode == 'documents' and can_undo)
        self.actions['redo'].set_enabled(self.workspace.mode == 'documents' and can_redo)
        self.actions['cut'].set_enabled(self.workspace.mode == 'documents' and has_selection)
        self.actions['copy'].set_enabled(self.workspace.mode == 'documents' and has_selection)
        self.actions['paste'].set_enabled(self.workspace.mode == 'documents' and has_active_doc and (text_in_clipboard or subtree_in_clipboard))
        self.actions['delete'].set_enabled(self.workspace.mode == 'documents' and has_selection)
        self.actions['select-all'].set_enabled(self.workspace.mode == 'documents' and has_active_doc)
        self.actions['insert-matharea'].set_enabled(self.workspace.mode == 'documents' and insert_in_line)
        self.actions['insert-link'].set_enabled(self.workspace.mode == 'documents' and insert_in_line)
        self.actions['remove-link'].set_enabled(self.workspace.mode == 'documents' and (links_inside_selection or ((not has_selection) and cursor_inside_link)))
        self.actions['insert-symbol'].set_enabled(self.workspace.mode == 'documents' and insert_in_matharea)
        self.actions['trigger-bold-button'].set_enabled(True)
        self.actions['trigger-italic-button'].set_enabled(True)
        self.actions['toggle-tools-sidebar'].set_enabled(True)
        self.actions['show-edit-menu'].set_enabled(self.workspace.mode == 'documents' and has_active_doc)
        self.actions['show-document-menu'].set_enabled(self.workspace.mode == 'documents' and has_active_doc)
        self.actions['show-hamburger-menu'].set_enabled(True)
        self.actions['show-shortcuts-dialog'].set_enabled(True)
        self.actions['show-about-dialog'].set_enabled(True)

    def add_document(self, action=None, paramenter=''):
        self.workspace.enter_draft_mode()

    def import_markdown_files(self, action=None, paramenter=''):
        DialogLocator.get_dialog('import_documents').run(self.workspace)

    def delete_document(self, action=None, parameter=''):
        self.workspace.delete_document(self.workspace.active_document)

    def rename_document(self, action=None, parameter=''):
        self.document_view.init_renaming()

    def export_as(self, action=None, parameter=''):
        DialogLocator.get_dialog('export_document').run(self.workspace.active_document)

    def go_back(self, action=None, parameter=''):
        if self.workspace.mode == 'draft':
            self.workspace.leave_draft_mode()
        else:
            prev_doc = self.workspace.history.get_previous_if_any(self.workspace.active_document)
            if prev_doc != None:
                self.workspace.set_active_document(prev_doc, update_history=False)

    def go_forward(self, action=None, parameter=''):
        next_doc = self.workspace.history.get_next_if_any(self.workspace.active_document)
        if next_doc != None:
            self.workspace.set_active_document(next_doc, update_history=False)

    def undo(self, action=None, parameter=''):
        self.workspace.active_document.undo()

    def redo(self, action=None, parameter=''):
        self.workspace.active_document.redo()

    def cut(self, action=None, parameter=''):
        self.copy()
        self.delete_selection()

    def copy(self, action=None, parameter=''):
        clipboard = Gdk.Display.get_default().get_clipboard()
        ast = self.workspace.active_document.ast
        subtree = ast.get_subtree(*ast.get_cursor_state())
        chars = ''.join([node.value for node in subtree if node.is_char()])

        cp_text = Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8', GLib.Bytes(chars.encode()))
        cp_internal = Gdk.ContentProvider.new_for_bytes('lemma/ast', GLib.Bytes(pickle.dumps(subtree)))
        cp_union = Gdk.ContentProvider.new_union([cp_text, cp_internal])

        clipboard.set_content(cp_union)

    def paste(self, action=None, parameter=''):
        Gdk.Display.get_default().get_clipboard().read_async(['text/plain', 'lemma/ast'], 0, None, self.on_paste)

    def on_paste(self, clipboard, result):
        result = clipboard.read_finish(result)
        if result[1].startswith('lemma/ast'):
            subtree = pickle.loads(result[0].read_bytes(8192 * 8192, None).get_data())
            self.workspace.active_document.add_command('insert_subtree', subtree)
        elif result[1] == 'text/plain':
            text = result[0].read_bytes(8192 * 8192, None).get_data().decode('utf-8')
            self.workspace.active_document.add_command('insert_text', text)

    def delete_selection(self, action=None, parameter=''):
        self.workspace.active_document.add_command('delete')

    def select_all(self, action=None, parameter=''):
        self.workspace.active_document.add_command('select_all')

    def insert_matharea(self, action=None, parameter=''):
        self.workspace.active_document.add_command('insert_matharea')

    def insert_symbol(self, action=None, parameter=None):
        if parameter == None: return

        name = parameter[0]
        self.workspace.active_document.add_command('insert_symbol', name)

    def insert_link(self, action=None, parameter=''):
        DialogLocator.get_dialog('insert_link').run(self.workspace.active_document)

    def remove_link(self, action=None, parameter=''):
        self.workspace.active_document.add_command('remove_link')

    def trigger_bold_button(self, action=None, parameter=''):
        self.main_window.toolbar.bold_button.emit('clicked')

    def trigger_italic_button(self, action=None, parameter=''):
        self.main_window.toolbar.italic_button.emit('clicked')

    def toggle_tools_sidebar(self, action=None, parameter=''):
        toggle = self.main_window.headerbar.hb_right.tools_sidebar_toggle
        toggle.set_active(not toggle.get_active())

    def show_edit_menu(self, action=None, parameter=''):
        PopoverManager.popup_at_button('edit_menu')

    def show_document_menu(self, action=None, parameter=''):
        PopoverManager.popup_at_button('document_menu')

    def show_hamburger_menu(self, action=None, parameter=''):
        PopoverManager.popup_at_button('hamburger_menu')
        return True

    def show_shortcuts_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('keyboard_shortcuts').run()

    def show_about_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('about').run()


