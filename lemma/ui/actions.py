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

from lemma.services.message_bus import MessageBus
from lemma.application_state.application_state import ApplicationState
from lemma.ui.dialogs.dialog_locator import DialogLocator
from lemma.services.layout_info import LayoutInfo
from lemma.services.node_type_db import NodeTypeDB
from lemma.widgets.image import Image
from lemma.services.xml_exporter import XMLExporter
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.use_cases.use_cases import UseCases
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class Actions(object):

    def __init__(self, main_window, application, model_state):
        self.main_window = main_window
        self.application = application
        self.model_state = model_state
        self.last_data = None

        self.actions = dict()
        self.add_simple_action('add-document', self.add_document)
        self.add_simple_action('import-markdown-files', self.import_markdown_files)
        self.add_simple_action('export-bulk', self.export_bulk)
        self.add_simple_action('delete-document', self.delete_document)
        self.add_simple_action('rename-document', self.rename_document)
        self.add_simple_action('export-markdown', self.export_markdown)
        self.add_simple_action('export-image', self.export_image)

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
        self.add_simple_action('show-link-popover', self.show_link_popover)
        self.add_simple_action('remove-link', self.remove_link)
        self.add_simple_action('copy-link', self.copy_link)

        self.add_simple_action('set-paragraph-style', self.set_paragraph_style, GLib.VariantType('s'))
        self.add_simple_action('toggle-bold', self.toggle_bold)
        self.add_simple_action('toggle-italic', self.toggle_italic)

        self.add_simple_action('decrease-indent', self.decrease_indent)
        self.add_simple_action('increase-indent', self.increase_indent)

        self.add_simple_action('show-insert-image-dialog', self.show_insert_image_dialog)

        self.add_simple_action('widget-shrink', self.widget_shrink)
        self.add_simple_action('widget-enlarge', self.widget_enlarge)

        self.add_simple_action('subscript', self.subscript)
        self.add_simple_action('superscript', self.superscript)

        self.add_simple_action('start-global-search', self.start_global_search)
        self.add_simple_action('toggle-tools-sidebar', self.toggle_tools_sidebar, GLib.VariantType('s'))
        self.add_simple_action('show-paragraph-style-menu', self.show_paragraph_style_menu)
        self.add_simple_action('show-edit-menu', self.show_edit_menu)
        self.add_simple_action('show-document-menu', self.show_document_menu)
        self.add_simple_action('show-hamburger-menu', self.show_hamburger_menu)
        self.add_simple_action('show-settings-dialog', self.show_settings_dialog)
        self.add_simple_action('show-shortcuts-dialog', self.show_shortcuts_dialog)
        self.add_simple_action('show-about-dialog', self.show_about_dialog)

        self.actions['quit'] = Gio.SimpleAction.new('quit', None)
        self.main_window.add_action(self.actions['quit'])

        Gdk.Display.get_default().get_clipboard().connect('changed', self.on_clipboard_changed)

        MessageBus.subscribe(self, 'history_changed')
        MessageBus.subscribe(self, 'new_document')
        MessageBus.subscribe(self, 'document_removed')
        MessageBus.subscribe(self, 'document_changed')
        MessageBus.subscribe(self, 'mode_set')

        self.update()

    def add_simple_action(self, name, callback, parameter=None):
        self.actions[name] = Gio.SimpleAction.new(name, parameter)
        self.main_window.add_action(self.actions[name])
        self.actions[name].connect('activate', callback)

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'history_changed' in messages or 'new_document' in messages or 'document_removed' in messages or 'document_changed' in messages or 'mode_set' in messages:
            self.update()

    def on_clipboard_changed(self, clipboard):
        self.update()

    @timer.timer
    def update(self):
        self.actions['add-document'].set_enabled(True)
        self.actions['import-markdown-files'].set_enabled(True)
        self.actions['export-bulk'].set_enabled(self.model_state.has_active_doc)
        self.actions['delete-document'].set_enabled(self.model_state.has_active_doc)
        self.actions['rename-document'].set_enabled(self.model_state.has_active_doc)
        self.actions['export-markdown'].set_enabled(self.model_state.has_active_doc)
        self.actions['export-image'].set_enabled(self.model_state.widget_selected)
        self.actions['go-back'].set_enabled(self.model_state.mode == 'draft' or self.model_state.prev_doc != None)
        self.actions['go-forward'].set_enabled(self.model_state.next_doc != None)
        self.actions['undo'].set_enabled(self.model_state.has_active_doc and self.model_state.can_undo)
        self.actions['redo'].set_enabled(self.model_state.has_active_doc and self.model_state.can_redo)
        self.actions['cut'].set_enabled(self.model_state.has_active_doc and self.model_state.has_selection)
        self.actions['copy'].set_enabled(self.model_state.has_active_doc and self.model_state.has_selection)
        self.actions['paste'].set_enabled(self.model_state.has_active_doc and (self.model_state.text_in_clipboard or self.model_state.subtree_in_clipboard or self.model_state.image_in_clipboard))
        self.actions['delete'].set_enabled(self.model_state.mode == 'documents' and self.model_state.has_selection)
        self.actions['select-all'].set_enabled(self.model_state.has_active_doc)
        self.actions['remove-selection'].set_enabled(self.model_state.has_active_doc and self.model_state.has_selection)
        self.actions['show-insert-image-dialog'].set_enabled(self.model_state.has_active_doc and self.model_state.insert_parent_is_root)
        self.actions['widget-shrink'].set_enabled(self.model_state.has_active_doc and not self.model_state.selected_widget_is_min)
        self.actions['widget-enlarge'].set_enabled(self.model_state.has_active_doc and not self.model_state.selected_widget_is_max)
        self.actions['open-link'].set_enabled(self.model_state.open_link_active)
        self.actions['remove-link'].set_enabled(self.model_state.remove_link_active)
        self.actions['show-link-popover'].set_enabled((self.model_state.has_active_doc and self.model_state.insert_parent_is_root) or self.model_state.edit_link_active)
        self.actions['copy-link'].set_enabled(self.model_state.copy_link_active)
        self.actions['subscript'].set_enabled(self.model_state.has_active_doc)
        self.actions['superscript'].set_enabled(self.model_state.has_active_doc)
        self.actions['set-paragraph-style'].set_enabled(self.model_state.has_active_doc)
        self.actions['toggle-bold'].set_enabled(self.model_state.has_active_doc)
        self.actions['toggle-italic'].set_enabled(self.model_state.has_active_doc)
        self.actions['decrease-indent'].set_enabled(self.model_state.has_active_doc)
        self.actions['increase-indent'].set_enabled(self.model_state.has_active_doc)
        self.actions['toggle-tools-sidebar'].set_enabled(True)
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
        document_id = WorkspaceRepo.get_workspace().get_active_document_id()

        UseCases.delete_document(document_id)

    def rename_document(self, action=None, parameter=''):
        self.application.document_title.init_renaming()

    def export_markdown(self, action=None, parameter=''):
        document = WorkspaceRepo.get_workspace().get_active_document()

        DialogLocator.get_dialog('export_markdown').run(document)

    def export_image(self, action=None, parameter=''):
        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        DialogLocator.get_dialog('export_image').run(selected_nodes[0].value)

    def go_back(self, action=None, parameter=''):
        workspace = WorkspaceRepo.get_workspace()

        mode = workspace.get_mode()
        if mode == 'draft':
            UseCases.leave_draft_mode()
        else:
            prev_doc = workspace.get_prev_id_in_history(workspace.get_active_document_id())
            if prev_doc != None:
                UseCases.set_active_document(prev_doc, update_history=False)

    def go_forward(self, action=None, parameter=''):
        workspace = WorkspaceRepo.get_workspace()

        next_doc = workspace.get_next_id_in_history(workspace.get_active_document_id())
        if next_doc != None:
            UseCases.set_active_document(next_doc, update_history=False)

    def undo(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.undo()

    def redo(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.redo()

    def cut(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        self.copy()
        UseCases.delete_selection()
        UseCases.scroll_insert_on_screen(animation_type='default')

    def copy(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        clipboard = Gdk.Display.get_default().get_clipboard()
        content_providers = []

        document = WorkspaceRepo.get_workspace().get_active_document()
        ast = document.ast
        cursor = document.cursor
        subtree = ast.get_subtree(*cursor.get_state())

        chars = []
        for node in subtree:
            if node.type == 'char':
                chars.append(node.value)
            elif node.type == 'eol':
                chars.append('\n')
        chars = ''.join(chars)
        content_providers.append(Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8', GLib.Bytes(chars.encode())))

        xml = ''
        nodes_by_paragraph = [[]]
        for node in subtree:
            nodes_by_paragraph[-1].append(node)
            if node.type == 'eol':
                nodes_by_paragraph.append([])
        if len(nodes_by_paragraph[-1]) == 0:
            del(nodes_by_paragraph[-1])
        for nodes in nodes_by_paragraph:
            paragraph = nodes[0].paragraph()
            xml += XMLExporter.export_paragraph(nodes, paragraph.style, paragraph.indentation_level)
        content_providers.append(Gdk.ContentProvider.new_for_bytes('lemma/ast', GLib.Bytes(xml.encode())))

        if len(subtree) == 1 and subtree[0].type == 'widget':
            data = subtree[0].value.get_data()
            content_providers.append(Gdk.ContentProvider.new_for_bytes('image/png', GLib.Bytes(data)))

        cp_union = Gdk.ContentProvider.new_union(content_providers)
        clipboard.set_content(cp_union)

    def paste(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        clipboard = Gdk.Display.get_default().get_clipboard()
        if clipboard.get_formats().contain_mime_type('lemma/ast'):
            Gdk.Display.get_default().get_clipboard().read_async(['lemma/ast'], 0, None, self.on_paste_ast)
        elif clipboard.get_formats().contain_mime_type('image/png') or clipboard.get_formats().contain_mime_type('image/jpeg'):
            Gdk.Display.get_default().get_clipboard().read_texture_async(None, self.on_paste_image)
        elif clipboard.get_formats().contain_mime_type('text/plain;charset=utf-8') or clipboard.get_formats().contain_mime_type('text/plain'):
            Gdk.Display.get_default().get_clipboard().read_text_async(None, self.on_paste_text)

    def on_paste_ast(self, clipboard, result):
        result = clipboard.read_finish(result)

        xml = result[0].read_bytes(8192 * 8192, None).get_data().decode('utf8')
        UseCases.insert_xml(xml)
        UseCases.scroll_insert_on_screen(animation_type='default')

    def on_paste_image(self, clipboard, result):
        texture = clipboard.read_texture_finish(result)
        data = texture.save_to_png_bytes().unref_to_data()
        image = Image(data)
        UseCases.add_image(image)

    def on_paste_text(self, clipboard, result):
        text = clipboard.read_text_finish(result)

        tags_at_cursor = ApplicationState.get_value('tags_at_cursor')
        link_at_cursor = ApplicationState.get_value('link_at_cursor')

        if len(text) < 2000:
            stext = text.strip()
            parsed_url = urlparse(stext)
            if parsed_url.scheme in ['http', 'https'] and '.' in parsed_url.netloc:
                text = xml_helpers.escape(stext)
                xml = xml_helpers.embellish_with_link_and_tags(text, text, tags_at_cursor)
                UseCases.insert_xml(xml)
                UseCases.scroll_insert_on_screen(animation_type='default')
                return

        text = xml_helpers.escape(text)
        xml = xml_helpers.embellish_with_link_and_tags(text, link_at_cursor, tags_at_cursor)
        UseCases.insert_xml(xml)
        UseCases.scroll_insert_on_screen(animation_type='default')

    def delete(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.delete()

    def select_all(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.select_all()

    def remove_selection(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.remove_selection()

    def subscript(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.cursor.get_insert_node()
        prev_char = insert.prev_in_parent()
        if not document.cursor.has_selection() and prev_char != None and prev_char.type == 'char' and not NodeTypeDB.is_whitespace(prev_char):
            xml = '<mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'
        else:
            xml = '<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'
        UseCases.insert_xml(xml)
        UseCases.scroll_insert_on_screen(animation_type='default')

    def superscript(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.cursor.get_insert_node()
        prev_char = insert.prev_in_parent()
        if not document.cursor.has_selection() and prev_char != None and prev_char.type == 'char' and not NodeTypeDB.is_whitespace(prev_char):
            xml = '<mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'
        else:
            xml = '<placeholder marks="prev_selection"/><mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'
        UseCases.insert_xml(xml)
        UseCases.scroll_insert_on_screen(animation_type='default')

    def set_paragraph_style(self, action=None, parameter=None):
        self.application.document_view.view.content.grab_focus()

        style = parameter.get_string()

        document = WorkspaceRepo.get_workspace().get_active_document()
        current_style = document.cursor.get_first_node().paragraph().style
        if current_style == style:
            style = 'p'

        UseCases.set_paragraph_style(style)

    def toggle_bold(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()
        if document.cursor.has_selection():
            UseCases.toggle_tag('bold')
        else:
            UseCases.app_state_set_value('tags_at_cursor', ApplicationState.get_value('tags_at_cursor') ^ {'bold'})

    def toggle_italic(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()
        if document.cursor.has_selection():
            UseCases.toggle_tag('italic')
        else:
            UseCases.app_state_set_value('tags_at_cursor', ApplicationState.get_value('tags_at_cursor') ^ {'italic'})

    def decrease_indent(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.change_indentation_level(-1)

    def increase_indent(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.change_indentation_level(1)

    def show_insert_image_dialog(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        DialogLocator.get_dialog('insert_image').run()

    def widget_shrink(self, action=None, parameter=None):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        UseCases.resize_widget(selected_nodes[0].value.get_width() - 1)

    def widget_enlarge(self, action=None, parameter=None):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        UseCases.resize_widget(selected_nodes[0].value.get_width() + 1)

    def open_link(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()

        UseCases.open_link(document.cursor.get_insert_node().link)

    def show_link_popover(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        UseCases.scroll_insert_on_screen(animation_type=None)
        UseCases.show_link_popover(self.main_window)

    def copy_link(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        clipboard = Gdk.Display.get_default().get_clipboard()
        document = WorkspaceRepo.get_workspace().get_active_document()
        ast = document.ast
        cursor = document.cursor
        node = cursor.get_insert_node()

        if node.link != None:
            cp_text = Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8', GLib.Bytes(node.link.encode()))
            cp_union = Gdk.ContentProvider.new_union([cp_text])

            clipboard.set_content(cp_union)

    def remove_link(self, action=None, parameter=''):
        self.application.document_view.view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()

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

    def toggle_tools_sidebar(self, action=None, parameter=None):
        UseCases.toggle_tools_sidebar(parameter.get_string())

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


