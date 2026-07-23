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

import os.path

from lemma.services.message_bus import MessageBus
from lemma.services.layout_info import LayoutInfo
from lemma.services.node_type_db import NodeTypeDB
from lemma.widgets.factory import WidgetFactory
from lemma.services.xml_exporter import XMLExporter
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.application_state.application_state import ApplicationState
from lemma.use_cases.use_cases import UseCases
from lemma.use_cases.queries import Queries
from lemma.services.text_shaper import TextShaper
from lemma.services.files import Files
from lemma.services.settings import Settings
from lemma.ui.shortcuts import Shortcuts
import lemma.services.xml_helpers as xml_helpers
import lemma.services.timer as timer


class Actions(object):

    def __init__(self, main_window, application):
        self.main_window = main_window
        self.application = application
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
        self.add_simple_action('extend-selection', self.extend_selection)
        self.add_simple_action('move-cursor-to-parent', self.move_cursor_to_parent)

        self.add_simple_action('open-link', self.open_link)
        self.add_simple_action('show-link-popover', self.show_link_popover)
        self.add_simple_action('remove-link', self.remove_link)
        self.add_simple_action('copy-link', self.copy_link)

        self.add_simple_action('set-paragraph-style', self.set_paragraph_style, GLib.VariantType('s'))
        self.add_simple_action('toggle-checkbox', self.toggle_checkbox)
        self.add_simple_action('toggle-bold', self.toggle_bold)
        self.add_simple_action('toggle-italic', self.toggle_italic)
        self.add_simple_action('toggle-verbatim', self.toggle_verbatim)
        self.add_simple_action('toggle-highlight', self.toggle_highlight)

        self.add_simple_action('decrease-indent', self.decrease_indent)
        self.add_simple_action('increase-indent', self.increase_indent)

        self.add_simple_action('show-insert-image-dialog', self.show_insert_image_dialog)
        self.add_simple_action('show-attach-files-dialog', self.show_attach_files_dialog)

        self.add_simple_action('subscript', self.subscript)
        self.add_simple_action('superscript', self.superscript)

        self.add_simple_action('start-global-search', self.start_global_search)
        self.add_simple_action('toggle-tools-sidebar', self.toggle_tools_sidebar, GLib.VariantType('s'))
        self.add_simple_action('show-settings-dialog', self.show_settings_dialog)
        self.add_simple_action('show-shortcuts-dialog', self.show_shortcuts_dialog)
        self.add_simple_action('show-about-dialog', self.show_about_dialog)

        self.actions['quit'] = Gio.SimpleAction.new('quit', None)
        self.main_window.add_action(self.actions['quit'])

        self.shortcut_controller = Shortcuts.new_controller()
        self.shortcut_controller.add_cb('quit', self.actions['quit'].activate)
        self.shortcut_controller.add_cb('add_document', self.actions['add-document'].activate)
        self.shortcut_controller.add_cb('start_global_search', self.actions['start-global-search'].activate)
        self.shortcut_controller.add_cb('go_back', self.actions['go-back'].activate)
        self.shortcut_controller.add_cb('go_forward', self.actions['go-forward'].activate)
        self.shortcut_controller.add_cb('show_shortcuts_dialog', self.actions['show-shortcuts-dialog'].activate)
        for i in range(1, 10):
            self.shortcut_controller.add_cb('activate_bookmark_' + str(i), self.activate_bookmark, i)
        self.main_window.add_controller(self.shortcut_controller)

        self.shortcut_controller_docview = Shortcuts.new_controller()
        self.shortcut_controller_docview.add_cb('toggle_bold', self.actions['toggle-bold'].activate)
        self.shortcut_controller_docview.add_cb('toggle_italic', self.actions['toggle-italic'].activate)
        self.shortcut_controller_docview.add_cb('toggle_verbatim', self.actions['toggle-verbatim'].activate)
        self.shortcut_controller_docview.add_cb('toggle_highlight', self.actions['toggle-highlight'].activate)
        self.shortcut_controller_docview.add_cb('link_popover', self.actions['show-link-popover'].activate)
        self.shortcut_controller_docview.add_cb('subscript', self.actions['subscript'].activate)
        self.shortcut_controller_docview.add_cb('superscript', self.actions['superscript'].activate)
        self.shortcut_controller_docview.add_cb('toggle_checkbox', self.actions['toggle-checkbox'].activate)
        self.shortcut_controller_docview.add_cb('undo', self.actions['undo'].activate)
        self.shortcut_controller_docview.add_cb('redo', self.actions['redo'].activate)
        self.shortcut_controller_docview.add_cb('cut', self.actions['cut'].activate)
        self.shortcut_controller_docview.add_cb('copy', self.actions['copy'].activate)
        self.shortcut_controller_docview.add_cb('paste', self.actions['paste'].activate)
        self.shortcut_controller_docview.add_cb('select_all', self.actions['select-all'].activate)
        self.shortcut_controller_docview.add_cb('go_to_parent_node', self.actions['move-cursor-to-parent'].activate)
        self.shortcut_controller_docview.add_cb('extend_selection', self.actions['extend-selection'].activate)
        self.shortcut_controller_docview.add_cb('rename_document', self.actions['rename-document'].activate)
        for para_style in ['h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'cl', 'p']:
            sc_name = 'paragraph_style_' + para_style
            callback = self.actions['set-paragraph-style'].activate
            self.shortcut_controller_docview.add_cb(sc_name, callback, GLib.Variant.new_string(para_style))
        self.main_window.document_view.content.add_controller(self.shortcut_controller_docview)

        Gdk.Display.get_default().get_clipboard().connect('changed', self.on_clipboard_changed)

        MessageBus.subscribe(self, 'new_active_document')
        MessageBus.subscribe(self, 'new_document')
        MessageBus.subscribe(self, 'document_removed')
        MessageBus.subscribe(self, 'document_ast_or_cursor_changed')
        MessageBus.subscribe(self, 'document_title_changed')
        MessageBus.subscribe(self, 'mode_set')

        self.update()

    def add_simple_action(self, name, callback, parameter=None):
        self.actions[name] = Gio.SimpleAction.new(name, parameter)
        self.main_window.add_action(self.actions[name])
        self.actions[name].connect('activate', callback)

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'new_active_document' in messages or 'new_document' in messages or 'document_removed' in messages or 'document_ast_or_cursor_changed' in messages or 'document_title_changed' in messages or 'mode_set' in messages:
            self.update()

    def on_clipboard_changed(self, clipboard):
        self.update()

    @timer.timer
    def update(self):
        workspace = WorkspaceRepo.get_workspace()
        document = workspace.get_active_document()

        clipboard_formats = Gdk.Display.get_default().get_clipboard().get_formats().to_string()
        text_in_clipboard = 'text/plain;charset=utf-8' in clipboard_formats
        subtree_in_clipboard = 'lemma/ast' in clipboard_formats
        image_in_clipboard = 'image/jpeg' in clipboard_formats or 'image/png' in clipboard_formats
        selected_widget = None if document == None else document.get_selected_widget()
        image_selected = selected_widget != None and selected_widget.get_type() == 'image'

        self.actions['add-document'].set_enabled(True)
        self.actions['import-markdown-files'].set_enabled(True)
        self.actions['export-bulk'].set_enabled(document != None)
        self.actions['delete-document'].set_enabled(document != None)
        self.actions['rename-document'].set_enabled(document != None)
        self.actions['export-markdown'].set_enabled(document != None)
        self.actions['export-image'].set_enabled(image_selected)
        self.actions['go-back'].set_enabled(workspace.get_mode() == 'draft' or (document != None and workspace.get_prev_id_in_history(document.id) != None))
        self.actions['go-forward'].set_enabled(document != None and workspace.get_next_id_in_history(document.id) != None)
        self.actions['undo'].set_enabled(document != None and document.can_undo())
        self.actions['redo'].set_enabled(document != None and document.can_redo())
        self.actions['cut'].set_enabled(document != None and document.has_selection())
        self.actions['copy'].set_enabled(document != None and document.has_selection())
        self.actions['paste'].set_enabled(document != None and (text_in_clipboard or subtree_in_clipboard or image_in_clipboard))
        self.actions['delete'].set_enabled(workspace.get_mode() == 'documents' and document.has_selection())
        self.actions['select-all'].set_enabled(document != None)
        self.actions['remove-selection'].set_enabled(document != None and document.has_selection())
        self.actions['extend-selection'].set_enabled(document != None)
        self.actions['move-cursor-to-parent'].set_enabled(document != None)
        self.actions['show-insert-image-dialog'].set_enabled(document != None and document.insert_parent_is_root())
        self.actions['show-attach-files-dialog'].set_enabled(document != None and document.insert_parent_is_root())
        self.actions['open-link'].set_enabled(document != None and document.cursor_inside_link())
        self.actions['remove-link'].set_enabled(document != None and (document.links_inside_selection() or document.cursor_inside_link()))
        self.actions['show-link-popover'].set_enabled(document != None and (document.insert_parent_is_root() or document.whole_selection_is_one_link() or document.cursor_inside_link()))
        self.actions['copy-link'].set_enabled(document != None and (document.whole_selection_is_one_link() or document.cursor_inside_link()))
        self.actions['subscript'].set_enabled(document != None)
        self.actions['superscript'].set_enabled(document != None)
        self.actions['set-paragraph-style'].set_enabled(document != None)
        self.actions['toggle-checkbox'].set_enabled(document != None)
        self.actions['toggle-bold'].set_enabled(document != None)
        self.actions['toggle-italic'].set_enabled(document != None)
        self.actions['toggle-verbatim'].set_enabled(document != None)
        self.actions['toggle-highlight'].set_enabled(document != None)
        self.actions['decrease-indent'].set_enabled(document != None)
        self.actions['increase-indent'].set_enabled(document != None)
        self.actions['toggle-tools-sidebar'].set_enabled(True)
        self.actions['show-settings-dialog'].set_enabled(True)
        self.actions['show-shortcuts-dialog'].set_enabled(True)
        self.actions['show-about-dialog'].set_enabled(True)

    def add_document(self, action=None, paramenter=''):
        UseCases.enter_draft_mode()

    def import_markdown_files(self, action=None, paramenter=''):
        UseCases.show_dialog('import_documents')

    def export_bulk(self, action=None, paramenter=''):
        UseCases.show_dialog('export_bulk')

    def delete_document(self, action=None, parameter=''):
        document_id = WorkspaceRepo.get_workspace().get_active_document_id()

        UseCases.delete_document(document_id)

    def rename_document(self, action=None, parameter=''):
        self.application.document_title.init_renaming()

    def export_markdown(self, action=None, parameter=''):
        document = WorkspaceRepo.get_workspace().get_active_document()

        UseCases.show_dialog('export_markdown', document)

    def export_image(self, action=None, parameter=''):
        document = WorkspaceRepo.get_workspace().get_active_document()

        UseCases.show_dialog('export_image', document.get_selected_widget())

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
        self.main_window.document_view.content.grab_focus()

        UseCases.undo()

    def redo(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.redo()

    def cut(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        self.copy()
        UseCases.delete_selection()

        UseCases.update_implicit_x_position()

    def copy(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        clipboard = Gdk.Display.get_default().get_clipboard()
        content_providers = []

        document = WorkspaceRepo.get_workspace().get_active_document()
        selected_nodes = document.get_selected_nodes()

        chars = []
        for node in selected_nodes:
            if node.type == 'char':
                chars.append(node.value)
            elif node.type == 'eol':
                chars.append('\n')
        chars = ''.join(chars)
        content_providers.append(Gdk.ContentProvider.new_for_bytes('text/plain;charset=utf-8', GLib.Bytes(chars.encode())))

        xml = ''
        nodes_by_paragraph = [[]]
        for node in selected_nodes:
            nodes_by_paragraph[-1].append(node)
            if node.type == 'eol':
                nodes_by_paragraph.append([])
        if len(nodes_by_paragraph[-1]) == 0:
            del(nodes_by_paragraph[-1])
        for nodes in nodes_by_paragraph:
            paragraph = nodes[0].paragraph()
            xml += XMLExporter.export_paragraph(nodes, paragraph.style, paragraph.indentation_level, paragraph.state)
        content_providers.append(Gdk.ContentProvider.new_for_bytes('lemma/ast', GLib.Bytes(xml.encode())))

        if (widget := document.get_selected_widget()) != None:
            provider = widget.get_clipboard_content_provider()
            if provider != None:
                content_providers.append(provider)

        cp_union = Gdk.ContentProvider.new_union(content_providers)
        clipboard.set_content(cp_union)

    def paste(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        clipboard = Gdk.Display.get_default().get_clipboard()
        if clipboard.get_formats().contain_mime_type('lemma/ast'):
            Gdk.Display.get_default().get_clipboard().read_async(['lemma/ast'], 0, None, self.on_paste_ast)
        elif clipboard.get_formats().contain_mime_type('image/png') or clipboard.get_formats().contain_mime_type('image/jpeg'):
            Gdk.Display.get_default().get_clipboard().read_texture_async(None, self.on_paste_image)
        elif clipboard.get_formats().contain_mime_type('text/uri-list'):
            Gdk.Display.get_default().get_clipboard().read_value_async(Gdk.FileList, 0, None, self.on_paste_files)
        elif clipboard.get_formats().contain_mime_type('text/plain;charset=utf-8') or clipboard.get_formats().contain_mime_type('text/plain'):
            Gdk.Display.get_default().get_clipboard().read_text_async(None, self.on_paste_text)

    def on_paste_ast(self, clipboard, result):
        result = clipboard.read_finish(result)

        xml = result[0].read_bytes(8192 * 8192, None).get_data().decode('utf8')
        UseCases.insert_xml(xml)

        UseCases.update_implicit_x_position()

    def on_paste_image(self, clipboard, result):
        document = WorkspaceRepo.get_workspace().get_active_document()

        texture = clipboard.read_texture_finish(result)
        filename = Files.get_distinct_document_file_name(document, '.png')
        Files.write_bytes_to_document_file(filename, texture.save_to_png_bytes().unref_to_data())
        image = WidgetFactory.make_widget('image', {'filename': filename})
        UseCases.add_widget(image)

        UseCases.update_implicit_x_position()

    def on_paste_files(self, clipboard, result):
        document = WorkspaceRepo.get_workspace().get_active_document()

        file_list = clipboard.read_value_finish(result)
        for file in file_list.get_files():
            origin = file.get_path()
            if os.path.isdir(origin):
                continue

            filename = Files.add_file_to_doc_folder_with_distinct_name(document, origin)
            widget = WidgetFactory.make_widget('attachment', {'filename': filename})
            UseCases.add_widget(widget)

        UseCases.update_implicit_x_position()

    def on_paste_text(self, clipboard, result):
        text = clipboard.read_text_finish(result)
        UseCases.insert_text(text)
        UseCases.update_implicit_x_position()

    def delete(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()
        UseCases.delete_selection()
        UseCases.update_implicit_x_position()

    def select_all(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()
        UseCases.select_all()

    def remove_selection(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()
        UseCases.remove_selection()
        UseCases.update_implicit_x_position()

    def extend_selection(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()
        UseCases.extend_selection()
        UseCases.update_implicit_x_position()

    def move_cursor_to_parent(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()
        UseCases.move_cursor_to_parent()
        UseCases.update_implicit_x_position()

    def subscript(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()
        prev_char = insert.prev_in_parent()
        if not document.has_selection() and prev_char != None and prev_char.type == 'char' and not NodeTypeDB.is_whitespace(prev_char):
            xml = '<mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'
        else:
            xml = '<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'
        UseCases.insert_xml(xml)
        UseCases.update_implicit_x_position()

    def superscript(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()
        insert = document.get_insert_node()
        prev_char = insert.prev_in_parent()
        if not document.has_selection() and prev_char != None and prev_char.type == 'char' and not NodeTypeDB.is_whitespace(prev_char):
            xml = '<mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'
        else:
            xml = '<placeholder marks="prev_selection"/><mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'
        UseCases.insert_xml(xml)
        UseCases.update_implicit_x_position()

    def set_paragraph_style(self, action=None, parameter=None):
        self.main_window.document_view.content.grab_focus()

        style = parameter.get_string()

        document = WorkspaceRepo.get_workspace().get_active_document()
        current_style = document.get_first_selection_bound().paragraph().style
        if current_style == style:
            style = 'p'

        UseCases.set_paragraph_style(style)

    def toggle_checkbox(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.toggle_checkbox_at_cursor()

    def toggle_bold(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.toggle_tag('bold')

    def toggle_italic(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.toggle_tag('italic')

    def toggle_verbatim(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.toggle_tag('verbatim')

    def toggle_highlight(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.toggle_tag('highlight')

    def decrease_indent(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.change_indentation_level(-1)

    def increase_indent(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        UseCases.change_indentation_level(1)

    def show_insert_image_dialog(self, action=None, parameter=''):
        UseCases.show_dialog('insert_image')

    def show_attach_files_dialog(self, action=None, parameter=''):
        UseCases.show_dialog('attach_files')

    def open_link(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()

        UseCases.open_link(document.get_insert_node().link)

    def activate_bookmark(self, button_pos):
        workspace = WorkspaceRepo.get_workspace()
        bookmarks = workspace.get_bookmarked_document_ids()

        if len(bookmarks) >= button_pos:
            document_id = bookmarks[button_pos - 1]
            UseCases.set_active_document(document_id, update_history=True)

    def show_link_popover(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()
        UseCases.scroll_insert_on_screen(animation_type=None)

        document = WorkspaceRepo.get_workspace().get_active_document()
        document_layout = document.get_layout(ApplicationState.get_preedit(), Settings.get_value('font_theme'))
        scrolling_pos_x, scrolling_pos_y = Queries.get_current_scrolling_offsets()

        insert = document.get_insert_node()
        x, y = document_layout.get_absolute_xy(document_layout.get_node_layout(insert))
        x -= scrolling_pos_x
        y -= scrolling_pos_y
        document_view = self.main_window.document_view
        document_view_allocation = document_view.compute_bounds(self.main_window).out_bounds
        x += document_view_allocation.origin.x
        y += document_view_allocation.origin.y
        x += LayoutInfo.get_document_padding_left()
        y += Queries.get_document_offset()
        fontname = document_layout.get_node_layout(insert)['fontname']
        padding_top = TextShaper.get_padding_top(fontname)
        padding_bottom = TextShaper.get_padding_bottom(fontname)
        y += document_layout.get_node_layout(insert)['height'] - padding_top - padding_bottom

        orientation = 'bottom'
        if y + 260 > document_view_allocation.size.height:
            orientation = 'top'
            y -= document_layout.get_node_layout(insert)['height'] - padding_top - padding_bottom

        if not document.has_selection() and insert.is_inside_link():
            UseCases.select_section(*insert.link_bounds())

        UseCases.show_popover('link_autocomplete', x, y, orientation)

    def copy_link(self, action=None, parameter=''):
        self.main_window.document_view.content.grab_focus()

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
        self.main_window.document_view.content.grab_focus()

        document = WorkspaceRepo.get_workspace().get_active_document()

        if document.has_selection():
            bounds = [document.get_insert_node(), document.get_selection_node()]
        elif document.get_insert_node().is_inside_link():
            bounds = document.get_insert_node().link_bounds()
        else:
            bounds = [document.get_insert_node(), document.get_selection_node()]
        UseCases.set_link(document, bounds, None)

    def start_global_search(self, action=None, parameter=''):
        search_entry = self.main_window.headerbar.hb_left.search_entry
        search_entry.grab_focus()

    def toggle_tools_sidebar(self, action=None, parameter=None):
        UseCases.toggle_tools_sidebar(parameter.get_string())

    def show_settings_dialog(self, action=None, parameter=''):
        UseCases.show_dialog('settings')

    def show_shortcuts_dialog(self, action=None, parameter=''):
        UseCases.show_dialog('settings', 'Keyboard Shortcuts')

    def show_about_dialog(self, action=None, parameter=''):
        UseCases.show_dialog('about')


