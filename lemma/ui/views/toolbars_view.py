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
from gi.repository import Gtk, GLib

from lemma.ui.popovers.popover_manager import PopoverManager
from lemma.services.layout_info import LayoutInfo


class ToolBarsView(Gtk.ActionBar):

    def __init__(self):
        Gtk.ActionBar.__init__(self)
        self.add_css_class('toolbar')

        self.mode_stack = Gtk.Stack()
        self.pack_start(self.mode_stack)

        self.toolbar_main = ToolBarMain()
        self.mode_stack.add_named(self.toolbar_main, 'main')

        self.toolbar_widget_resizable = ToolBarWidgetResizable()
        self.mode_stack.add_named(self.toolbar_widget_resizable, 'widget_resizable')

        self.toolbar_right = ToolBarRight()
        self.pack_end(self.toolbar_right)


class ToolBarRight(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.edit_menu_button = Gtk.Button.new_from_icon_name('document-edit-symbolic')
        self.edit_menu_button.set_can_focus(False)
        self.edit_menu_button.set_tooltip_text(_('Edit Menu'))
        self.edit_menu_button.add_css_class('flat')
        self.edit_menu_button.set_action_name('win.show-edit-menu')

        self.redo_button = Gtk.Button.new_from_icon_name('edit-redo-symbolic')
        self.redo_button.set_action_name('win.redo')
        self.redo_button.set_can_focus(False)
        self.redo_button.set_tooltip_text(_('Redo') + ' (Shift+Ctrl+Z)')

        self.undo_button = Gtk.Button.new_from_icon_name('edit-undo-symbolic')
        self.undo_button.set_action_name('win.undo')
        self.undo_button.set_can_focus(False)
        self.undo_button.set_tooltip_text(_('Undo') + ' (Ctrl+Z)')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.edit_menu_button)
        box.append(self.redo_button)
        box.append(self.undo_button)
        self.append(box)
        self.append(Gtk.Separator())

        self.symbols_sidebar_toggle = Gtk.Button()
        self.symbols_sidebar_toggle.set_tooltip_text(_('Symbols Sidebar'))
        self.symbols_sidebar_toggle.set_icon_name('insert-symbols-symbolic')
        self.symbols_sidebar_toggle.set_can_focus(False)
        self.symbols_sidebar_toggle.add_css_class('flat')

        self.emoji_sidebar_toggle = Gtk.Button()
        self.emoji_sidebar_toggle.set_tooltip_text(_('Emoji Sidebar'))
        self.emoji_sidebar_toggle.set_icon_name('sentiment-very-satisfied-symbolic')
        self.emoji_sidebar_toggle.set_can_focus(False)
        self.emoji_sidebar_toggle.add_css_class('flat')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.symbols_sidebar_toggle)
        box.append(self.emoji_sidebar_toggle)
        self.append(box)


class ToolBarMain(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.paragraph_style_menu_button_label = Gtk.Label()
        self.paragraph_style_menu_button_label.set_xalign(Gtk.Align.FILL)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        box.append(self.paragraph_style_menu_button_label)
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))

        self.paragraph_style_menu_button = Gtk.Button()
        self.paragraph_style_menu_button.set_child(box)
        self.paragraph_style_menu_button.set_can_focus(False)
        self.paragraph_style_menu_button.set_tooltip_text(_('Paragraph Style'))
        self.paragraph_style_menu_button.add_css_class('flat')
        self.paragraph_style_menu_button.set_action_name('win.show-paragraph-style-menu')

        self.append(self.paragraph_style_menu_button)

        self.tag_buttons_separator = Gtk.Separator()
        self.append(self.tag_buttons_separator)

        self.bold_button = Gtk.Button.new_from_icon_name('bold-text-symbolic')
        self.bold_button.set_action_name('win.toggle-bold')
        self.bold_button.set_can_focus(False)
        self.bold_button.set_tooltip_text(_('Bold') + ' (Ctrl+B)')

        self.italic_button = Gtk.Button.new_from_icon_name('italic-text-symbolic')
        self.italic_button.set_action_name('win.toggle-italic')
        self.italic_button.set_can_focus(False)
        self.italic_button.set_tooltip_text(_('Italic') + ' (Ctrl+I)')

        self.verbatim_button = Gtk.Button.new_from_icon_name('verbatim-text-symbolic')
        self.verbatim_button.set_action_name('win.toggle-verbatim')
        self.verbatim_button.set_can_focus(False)
        self.verbatim_button.set_tooltip_text(_('Verbatim') + ' (Ctrl+E)')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.add_css_class('highlight-tag-button')
        box.append(Gtk.Image.new_from_icon_name('highlight-text-symbolic'))

        self.highlight_button = Gtk.Button()
        self.highlight_button.set_child(box)
        self.highlight_button.add_css_class('flat')
        self.highlight_button.set_action_name('win.toggle-highlight')
        self.highlight_button.set_can_focus(False)
        self.highlight_button.set_tooltip_text(_('Highlight') + ' (Ctrl+U)')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.bold_button)
        box.append(self.italic_button)
        box.append(self.verbatim_button)
        box.append(self.highlight_button)
        self.append(box)

        self.list_buttons_separator = Gtk.Separator()
        self.append(self.list_buttons_separator)

        self.ul_button = Gtk.Button.new_from_icon_name('view-list-bullet-symbolic')
        self.ul_button.set_detailed_action_name('win.set-paragraph-style::ul')
        self.ul_button.set_can_focus(False)
        self.ul_button.set_tooltip_text(_('Bullet List') + ' (Ctrl+7)')

        self.ol_button = Gtk.Button.new_from_icon_name('view-list-ordered-symbolic')
        self.ol_button.set_detailed_action_name('win.set-paragraph-style::ol')
        self.ol_button.set_can_focus(False)
        self.ol_button.set_tooltip_text(_('Numbered List') + ' (Ctrl+8)')

        self.cl_button = Gtk.Button.new_from_icon_name('view-checklist-symbolic')
        self.cl_button.set_detailed_action_name('win.set-paragraph-style::cl')
        self.cl_button.set_can_focus(False)
        self.cl_button.set_tooltip_text(_('Checklist') + ' (Ctrl+9)')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.ul_button)
        box.append(self.ol_button)
        box.append(self.cl_button)
        self.append(box)

        self.indentation_buttons_separator = Gtk.Separator()
        self.append(self.indentation_buttons_separator)

        self.indent_less_button = Gtk.Button.new_from_icon_name('indent-less-symbolic')
        self.indent_less_button.set_action_name('win.decrease-indent')
        self.indent_less_button.set_can_focus(False)
        self.indent_less_button.set_tooltip_text(_('Decrease Indent'))

        self.indent_more_button = Gtk.Button.new_from_icon_name('indent-more-symbolic')
        self.indent_more_button.set_action_name('win.increase-indent')
        self.indent_more_button.set_can_focus(False)
        self.indent_more_button.set_tooltip_text(_('Increase Indent'))

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.indent_less_button)
        box.append(self.indent_more_button)
        self.append(box)

        self.insert_buttons_separator = Gtk.Separator()
        self.append(self.insert_buttons_separator)

        self.image_button = Gtk.Button.new_from_icon_name('insert-image-symbolic')
        self.image_button.set_action_name('win.show-insert-image-dialog')
        self.image_button.set_can_focus(False)
        self.image_button.set_tooltip_text(_('Insert Image'))

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.image_button)
        self.append(box)

        self.link_buttons_separator = Gtk.Separator()
        self.append(self.link_buttons_separator)

        self.insert_link_button = Gtk.ToggleButton()
        self.insert_link_button.set_child(Gtk.Image.new_from_icon_name('link-symbolic'))
        self.insert_link_button.set_can_focus(False)
        self.insert_link_button.add_css_class('flat')
        self.insert_link_button.set_tooltip_text(_('Insert Link') + ' (Ctrl+L)')
        self.insert_link_button.set_action_name('win.show-link-popover')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.insert_link_button)
        self.append(box)


class ToolBarWidgetResizable(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.status_label = Gtk.Label.new('')
        self.status_label.set_xalign(0)
        self.status_label.add_css_class('status')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.status_label)
        self.append(box)
        self.append(Gtk.Separator())

        self.shrink_button = Gtk.Button.new_from_icon_name('value-decrease-symbolic')
        self.shrink_button.set_action_name('win.widget-shrink')
        self.shrink_button.set_can_focus(False)
        self.shrink_button.set_tooltip_text(_('Shrink'))

        self.enlarge_button = Gtk.Button.new_from_icon_name('value-increase-symbolic')
        self.enlarge_button.set_action_name('win.widget-enlarge')
        self.enlarge_button.set_can_focus(False)
        self.enlarge_button.set_tooltip_text(_('Enlarge'))

        self.scale = Gtk.Scale()
        self.scale.set_increments(1, 1)
        self.scale.set_show_fill_level(False)
        self.scale.set_can_focus(False)
        self.scale.set_size_request(218, -1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.shrink_button)
        box.append(self.scale)
        box.append(self.enlarge_button)
        self.append(box)
        self.append(Gtk.Separator())

        self.escape_button = Gtk.Button.new_from_icon_name('remove-selection-symbolic')
        self.escape_button.set_action_name('win.remove-selection')
        self.escape_button.set_can_focus(False)
        self.escape_button.set_tooltip_text(_('Remove Selection (Esc)'))

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.escape_button)
        self.append(box)


