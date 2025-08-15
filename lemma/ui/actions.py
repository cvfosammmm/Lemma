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

from urllib.parse import urlparse

from lemma.application_state.application_state import ApplicationState
from lemma.ui.dialogs.dialog_locator import DialogLocator
from lemma.services.layout_info import LayoutInfo
from lemma.services.node_type_db import NodeTypeDB
from lemma.services.xml_exporter import XMLExporter
from lemma.history.history import History
from lemma.use_cases.use_cases import UseCases
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class Actions(object):

    def __init__(self, main_window, application, model_state):
        self.main_window = main_window
        self.application = application
        self.model_state = model_state

        self.actions = dict()
        self.add_simple_action('add-document', self.add_document)
        self.add_simple_action('import-markdown-files', self.import_markdown_files)
        self.add_simple_action('export-bulk', self.export_bulk)
        self.add_simple_action('delete-document', self.delete_document)
        self.add_simple_action('rename-document', self.rename_document)
        self.add_simple_action('export-markdown', self.export_markdown)
        self.add_simple_action('export-html', self.export_html)

        self.add_simple_action('go-back', self.go_back)
        self.add_simple_action('go-forward', self.go_forward)

        self.add_simple_action('undo', self.undo)
        self.add_simple_action('redo', self.redo)
        self.add_simple_action('cut', self.cut)
        self.add_simple_action('copy', self.copy)
        self.add_simple_action('paste', self.paste)
        self.add_simple_action('delete', self.delete)
        self.add_simple_action('select-all', self.select_all)
        self.add_simple_action('remove-selection', self.remove_selection)

        self.add_simple_action('open-link', self.open_link)
        self.add_simple_action('insert-link', self.insert_link)
        self.add_simple_action('remove-link', self.remove_link)
        self.add_simple_action('edit-link', self.edit_link)
        self.add_simple_action('copy-link', self.copy_link)
        self.add_simple_action('insert-xml', self.insert_xml, GLib.VariantType('s'))

        self.add_simple_action('set-paragraph-style', self.set_paragraph_style, GLib.VariantType('s'))
        self.add_simple_action('toggle-bold', self.toggle_bold)
        self.add_simple_action('toggle-italic', self.toggle_italic)

        self.add_simple_action('show-insert-image-dialog', self.show_insert_image_dialog)

        self.add_simple_action('widget-shrink', self.widget_shrink)
        self.add_simple_action('widget-enlarge', self.widget_enlarge)

        self.add_simple_action('subscript', self.subscript)
        self.add_simple_action('superscript', self.superscript)

        self.add_simple_action('start-global-search', self.start_global_search)
        self.add_simple_action('toggle-symbols-sidebar', self.toggle_symbols_sidebar)
        self.add_simple_action('toggle-emojis-sidebar', self.toggle_emojis_sidebar)
        self.add_simple_action('show-paragraph-style-menu', self.show_paragraph_style_menu)
        self.add_simple_action('show-edit-menu', self.show_edit_menu)
        self.add_simple_action('show-document-menu', self.show_document_menu)
        self.add_simple_action('show-hamburger-menu', self.show_hamburger_menu)
        self.add_simple_action('show-settings-dialog', self.show_settings_dialog)
        self.add_simple_action('show-shortcuts-dialog', self.show_shortcuts_dialog)
        self.add_simple_action('show-about-dialog', self.show_about_dialog)

        self.actions['quit'] = Gio.SimpleAction.new('quit', None)
        self.main_window.add_action(self.actions['quit'])

    def add_simple_action(self, name, callback, parameter=None):
        self.actions[name] = Gio.SimpleAction.new(name, parameter)
        self.main_window.add_action(self.actions[name])
        self.actions[name].connect('activate', callback)

    @timer.timer
    def update(self):
        self.actions['add-document'].set_enabled(True)
        self.actions['import-markdown-files'].set_enabled(True)
        self.actions['export-bulk'].set_enabled(self.model_state.has_active_doc)
        self.actions['delete-document'].set_enabled(self.model_state.has_active_doc)
        self.actions['rename-document'].set_enabled(self.model_state.has_active_doc)
        self.actions['export-markdown'].set_enabled(self.model_state.has_active_doc)
        self.actions['export-html'].set_enabled(self.model_state.has_active_doc)
        self.actions['go-back'].set_enabled(self.model_state.mode == 'draft' or self.model_state.prev_doc != None)
        self.actions['go-forward'].set_enabled(self.model_state.next_doc != None)
        self.actions['undo'].set_enabled(self.model_state.has_active_doc and self.model_state.can_undo)
        self.actions['redo'].set_enabled(self.model_state.has_active_doc and self.model_state.can_redo)
        self.actions['cut'].set_enabled(self.model_state.has_active_doc and self.model_state.has_selection)
        self.actions['copy'].set_enabled(self.model_state.has_active_doc and self.model_state.has_selection)
        self.actions['paste'].set_enabled(self.model_state.has_active_doc and (self.model_state.text_in_clipboard or self.model_state.subtree_in_clipboard))
        self.actions['delete'].set_enabled(self.model_state.mode == 'documents' and self.model_state.has_selection)
        self.actions['select-all'].set_enabled(self.model_state.has_active_doc)
        self.actions['remove-selection'].set_enabled(self.model_state.has_active_doc and self.model_state.has_selection)
        self.actions['insert-link'].set_enabled(self.model_state.has_active_doc and self.model_state.insert_in_line)
        self.actions['show-insert-image-dialog'].set_enabled(self.model_state.has_active_doc and self.model_state.insert_in_line)
        self.actions['widget-shrink'].set_enabled(self.model_state.has_active_doc and not self.model_state.selected_widget_is_min)
        self.actions['widget-enlarge'].set_enabled(self.model_state.has_active_doc and not self.model_state.selected_widget_is_max)
        self.actions['open-link'].set_enabled(self.model_state.open_link_active)
        self.actions['remove-link'].set_enabled(self.model_state.remove_link_active)
        self.actions['edit-link'].set_enabled(self.model_state.edit_link_active)
        self.actions['copy-link'].set_enabled(self.model_state.copy_link_active)
        self.actions['subscript'].set_enabled(self.model_state.has_active_doc)
        self.actions['superscript'].set_enabled(self.model_state.has_active_doc)
        self.actions['insert-xml'].set_enabled(self.model_state.has_active_doc)
        self.actions['set-paragraph-style'].set_enabled(self.model_state.has_active_doc)
        self.actions['toggle-bold'].set_enabled(self.model_state.has_active_doc)
        self.actions['toggle-italic'].set_enabled(self.model_state.has_active_doc)
        self.actions['toggle-symbols-sidebar'].set_enabled(True)
        self.actions['show-paragraph-style-menu'].set_enabled(self.model_state.has_active_doc)
        self.actions['show-edit-menu'].set_enabled(self.model_state.has_active_doc)
        self.actions['show-document-menu'].set_enabled(self.model_state.has_active_doc)
        self.actions['show-hamburger-menu'].set_enabled(True)
        self.actions['show-settings-dialog'].set_enabled(True)
        self.actions['show-shortcuts-dialog'].set_enabled(True)
        self.actions['show-about-dialog'].set_enabled(True)

    def add_document(self, action=None, paramenter=''):
        UseCases.enter_draft_mode()

    def import_markdown_files(self, action=None, paramenter=''):
        DialogLocator.get_dialog('import_documents').run()

    def export_bulk(self, action=None, paramenter=''):
        DialogLocator.get_dialog('export_bulk').run()

    def delete_document(self, action=None, parameter=''):
        UseCases.delete_document(History.get_active_document())

    def rename_document(self, action=None, parameter=''):
        self.application.document_view.init_renaming()

    def export_markdown(self, action=None, parameter=''):
        DialogLocator.get_dialog('export_markdown').run(History.get_active_document())

    def export_html(self, action=None, parameter=''):
        DialogLocator.get_dialog('export_html').run(History.get_active_document())

    def go_back(self, action=None, parameter=''):
        mode = ApplicationState.get_value('mode')
        if mode == 'draft':
            UseCases.leave_draft_mode()
        else:
            prev_doc = History.get_previous_if_any(History.get_active_document())
            if prev_doc != None:
                UseCases.set_active_document(prev_doc, update_history=False, scroll_to_top=False)

    def go_forward(self, action=None, parameter=''):
        next_doc = History.get_next_if_any(History.get_active_document())
        if next_doc != None:
            UseCases.set_active_document(next_doc, update_history=False, scroll_to_top=False)

    def undo(self, action=None, parameter=''):
        UseCases.undo()

    def redo(self, action=None, parameter=''):
        UseCases.redo()

    def cut(self, action=None, parameter=''):
        self.copy()
        UseCases.delete_selection()

    def copy(self, action=None, parameter=''):
        clipboard = Gdk.Display.get_default().get_clipboard()
        ast = History.get_active_document().ast
        cursor = History.get_active_document().cursor
        subtree = ast.get_subtree(*cursor.get_state())

        chars = []
        for node in subtree:
            if node.type == 'char':
                chars.append(node.value)
            elif node.type == 'eol':
                chars.append('\n')
        chars = ''.join(chars)

        xml = XMLExporter.export(subtree)

        cp_text = Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8', GLib.Bytes(chars.encode()))
        cp_internal = Gdk.ContentProvider.new_for_bytes('lemma/ast', GLib.Bytes(xml.encode()))
        cp_union = Gdk.ContentProvider.new_union([cp_text, cp_internal])

        clipboard.set_content(cp_union)

    def paste(self, action=None, parameter=''):
        clipboard = Gdk.Display.get_default().get_clipboard()
        if clipboard.get_formats().contain_mime_type('lemma/ast'):
            Gdk.Display.get_default().get_clipboard().read_async(['lemma/ast'], 0, None, self.on_paste_ast)
        else:
            Gdk.Display.get_default().get_clipboard().read_async(['text/plain', 'text/plain;charset=utf-8'], 0, None, self.on_paste)

    def on_paste_ast(self, clipboard, result):
        result = clipboard.read_finish(result)
        document = History.get_active_document()

        xml = result[0].read_bytes(8192 * 8192, None).get_data().decode('utf8')
        UseCases.insert_xml(xml)

    def on_paste(self, clipboard, result):
        result = clipboard.read_finish(result)
        document = History.get_active_document()

        if result[1].startswith('text/plain'):
            text = result[0].read_bytes(8192 * 8192, None).get_data().decode('unicode_escape')

            tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
            link_at_cursor = ApplicationState.get_value('link_at_cursor')

            if len(text) < 2000:
                stext = text.strip()
                parsed_url = urlparse(stext)
                if parsed_url.scheme in ['http', 'https'] and '.' in parsed_url.netloc:
                    text = xml_helpers.escape(stext)
                    xml = xml_helpers.embellish_with_link_and_tags(text, text, tags_at_cursor)
                    UseCases.insert_xml(xml)
                    return

            text = xml_helpers.escape(text)
            xml = xml_helpers.embellish_with_link_and_tags(text, link_at_cursor, tags_at_cursor)
            UseCases.insert_xml(xml)

    def delete(self, action=None, parameter=''):
        UseCases.delete()

    def select_all(self, action=None, parameter=''):
        UseCases.select_all()

    def remove_selection(self, action=None, parameter=''):
        UseCases.remove_selection()

    def insert_xml(self, action=None, parameter=None):
        UseCases.insert_xml(parameter.get_string())

    def subscript(self, action=None, parameter=''):
        document = History.get_active_document()
        insert = document.cursor.get_insert_node()
        prev_char = insert.prev_in_parent()
        if not document.cursor.has_selection() and prev_char != None and prev_char.type == 'char' and not NodeTypeDB.is_whitespace(prev_char):
            xml = '<mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'
        else:
            xml = '<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'
        UseCases.insert_xml(xml)

    def superscript(self, action=None, parameter=''):
        document = History.get_active_document()
        insert = document.cursor.get_insert_node()
        prev_char = insert.prev_in_parent()
        if not document.cursor.has_selection() and prev_char != None and prev_char.type == 'char' and not NodeTypeDB.is_whitespace(prev_char):
            xml = '<mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'
        else:
            xml = '<placeholder marks="prev_selection"/><mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'
        UseCases.insert_xml(xml)

    def set_paragraph_style(self, action=None, parameter=None):
        UseCases.set_paragraph_style(parameter.get_string())

    def toggle_bold(self, action=None, parameter=''):
        document = History.get_active_document()
        if document.cursor.has_selection():
            UseCases.toggle_tag('bold')
        else:
            UseCases.app_state_set_value('tags_at_cursor', ApplicationState.get_value('tags_at_cursor') ^ {'bold'})

    def toggle_italic(self, action=None, parameter=''):
        document = History.get_active_document()
        if document.cursor.has_selection():
            UseCases.toggle_tag('italic')
        else:
            UseCases.app_state_set_value('tags_at_cursor', ApplicationState.get_value('tags_at_cursor') ^ {'italic'})

    def show_insert_image_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('insert_image').run()

    def widget_shrink(self, action=None, parameter=None):
        document = History.get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        UseCases.resize_widget(selected_nodes[0].value.get_width() - 1)

    def widget_enlarge(self, action=None, parameter=None):
        document = History.get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        UseCases.resize_widget(selected_nodes[0].value.get_width() + 1)

    def open_link(self, action=None, parameter=''):
        document = History.get_active_document()

        UseCases.open_link(document.cursor.get_insert_node().link)

    def insert_link(self, action=None, parameter=''):
        UseCases.show_insert_link_popover(self.main_window)

    def edit_link(self, action=None, parameter=''):
        UseCases.show_insert_link_popover(self.main_window)

    def copy_link(self, action=None, parameter=''):
        clipboard = Gdk.Display.get_default().get_clipboard()
        ast = History.get_active_document().ast
        cursor = History.get_active_document().cursor
        node = cursor.get_insert_node()

        if node.link != None:
            cp_text = Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8', GLib.Bytes(node.link.encode()))
            cp_union = Gdk.ContentProvider.new_union([cp_text])

            clipboard.set_content(cp_union)

    def remove_link(self, action=None, parameter=''):
        document = History.get_active_document()

        if document.cursor.has_selection():
            bounds = [document.cursor.get_insert_node(), document.cursor.get_selection_node()]
        elif document.cursor.get_insert_node().is_inside_link():
            bounds = document.cursor.get_insert_node().link_bounds()
        else:
            bounds = [document.cursor.get_insert_node(), document.cursor.get_selection_node()]
        UseCases.set_link(document, bounds, None)

    def start_global_search(self, action=None, parameter=''):
        search_entry = self.main_window.headerbar.hb_left.search_entry
        search_entry.grab_focus()

    def toggle_symbols_sidebar(self, action=None, parameter=None):
        toggle_button = self.main_window.toolbar.toolbar_right.symbols_sidebar_toggle
        if toggle_button.get_active():
            UseCases.hide_tools_sidebar()
        else:
            UseCases.show_tools_sidebar('math')

    def toggle_emojis_sidebar(self, action=None, parameter=None):
        toggle_button = self.main_window.toolbar.toolbar_right.emoji_sidebar_toggle
        if toggle_button.get_active():
            UseCases.hide_tools_sidebar()
        else:
            UseCases.show_tools_sidebar('emojis')

    def show_paragraph_style_menu(self, action=None, parameter=''):
        button = self.main_window.toolbar.toolbar_main.paragraph_style_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y
        UseCases.show_popover('paragraph_style', x, y, 'top')

    def show_edit_menu(self, action=None, parameter=''):
        button = self.main_window.toolbar.toolbar_right.edit_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y
        UseCases.show_popover('edit_menu', x, y, 'top')

    def show_document_menu(self, action=None, parameter=''):
        button = self.main_window.headerbar.hb_right.document_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height
        UseCases.show_popover('document_menu', x, y, 'bottom')

    def show_hamburger_menu(self, action=None, parameter=''):
        button = self.main_window.headerbar.hb_left.hamburger_menu_button
        allocation = button.compute_bounds(self.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height
        UseCases.show_popover('hamburger_menu', x, y, 'bottom')

    def show_settings_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('settings').run()

    def show_shortcuts_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('keyboard_shortcuts').run()

    def show_about_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('about').run()


