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
from gi.repository import Gtk, Gdk, Pango

import os.path

from lemma.services.files import Files
from lemma.services.helpers import Helpers
from lemma.services.layout_info import LayoutInfo
from lemma.services.text_shaper import TextShaper
from lemma.services.text_renderer import TextRenderer
from lemma.services.color_manager import ColorManager
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.use_cases.use_cases import UseCases
from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView


class WidgetManager():

    def __init__(self, main_window, application):
        self.toolbars = dict()
        self.toolbars['attachment'] = ToolbarAttachment(main_window, application)
        self.toolbars['image'] = ToolbarImage(main_window, application)

    def animate(self):
        pass

    def has_toolbar(self, widget):
        return widget.get_type() in self.toolbars

    def get_toolbar(self, widget):
        if self.has_toolbar(widget):
            return self.toolbars[widget.get_type()]
        return None

    def update_toolbar(self, widget):
        if self.has_toolbar(widget):
            toolbar = self.toolbars[widget.get_type()]
            toolbar.update(widget)

    def draw(self, widget, ctx, offset_x, offset_y, hidpi_factor, fontname):
        if widget.get_type() == 'attachment':
            baseline = TextShaper.get_ascend(fontname) + TextShaper.get_descend(fontname)
            fg_color = ColorManager.get_ui_color_string('links')

            filename = os.path.basename(widget.get_attribute('filename'))
            dimensions = TextShaper.measure(filename, fontname)
            for char, dims in zip(filename, dimensions):
                surface, left, top = TextRenderer.get_glyph(char, fontname, fg_color, hidpi_factor)
                if surface != None:
                    ctx.set_source_surface(surface, int((offset_x) * hidpi_factor + left), int((offset_y + baseline) * hidpi_factor + top))
                    ctx.paint()
                offset_x += dims[0]

        elif widget.get_type() == 'image':
            matrix = ctx.get_matrix()
            width, height = widget.get_size()
            scaling_factor_x = width * hidpi_factor / widget.cache['original_width']
            scaling_factor_y = height * hidpi_factor / widget.cache['original_height']
            ctx.scale(scaling_factor_x, scaling_factor_y)

            ctx.set_source_surface(widget.cache['cairo_surface'], offset_x * hidpi_factor / scaling_factor_x, offset_y * hidpi_factor / scaling_factor_y)
            ctx.paint()

            ctx.set_matrix(matrix)

    def get_cursor_name(self, widget):
        if widget.get_type() == 'attachment':
            return 'pointer'
        elif widget.get_type() == 'image':
            return 'default'
        else:
            return 'default'

    def on_primary_button_press(self, widget, n_press, x, y):
        if widget.get_type() == 'attachment':
            if n_press == 2:
                Files.open_document_file(widget.get_attribute('filename'))
                return True

    def on_keypress(self, widget, keyval, keycode, keyboard_state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if widget.get_type() == 'attachment':
            match (Gdk.keyval_name(keyval).lower(), int(keyboard_state & modifiers)):
                case ('return', _) | ('kp_enter', _):
                    Files.open_document_file(widget.get_attribute('filename'))
                    return True


class ToolbarAttachment(Gtk.Box):

    def __init__(self, main_window, application):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.main_window = main_window
        self.application = application

        self.status_label = Gtk.Label.new('')
        self.status_label.set_xalign(0)
        self.status_label.add_css_class('status')

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.status_label)
        self.append(box)
        self.append(Gtk.Separator())

        self.open_button = Gtk.Button.new_with_label('Open')
        self.open_button.add_css_class('flat')
        self.open_button.set_can_focus(False)

        self.rename_button = Gtk.Button.new_with_label('Rename')
        self.rename_button.add_css_class('flat')
        self.rename_button.set_can_focus(False)

        self.copy_button = Gtk.Button.new_with_label('Copy')
        self.copy_button.set_action_name('win.copy')
        self.copy_button.add_css_class('flat')
        self.copy_button.set_can_focus(False)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.open_button)
        box.append(self.rename_button)
        box.append(self.copy_button)
        self.append(box)
        self.append(Gtk.Separator())

        self.escape_button = Gtk.Button.new_from_icon_name('remove-selection-symbolic')
        self.escape_button.set_action_name('win.remove-selection')
        self.escape_button.set_can_focus(False)
        self.escape_button.set_tooltip_text(_('Remove Selection (Esc)'))

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.escape_button)
        self.append(box)

        self.open_button.connect('clicked', self.on_open_button_clicked)
        self.rename_button.connect('clicked', self.on_rename_button_clicked)

        self.filename = None

    def update(self, widget):
        self.filename = widget.get_attribute('filename')
        status_text = os.path.basename(self.filename)
        status_text += ' (' + Helpers.filesize_to_string(Files.get_document_file_size(self.filename)) + ')'
        self.status_label.set_text(status_text)

    def on_open_button_clicked(self, button):
        if self.filename != None:
            Files.open_document_file(self.filename)

    def on_rename_button_clicked(self, button):
        self.application.document_view.view.content.grab_focus()
        self.application.scrolling.scroll_insert_on_screen(animation_type=None)

        document = WorkspaceRepo.get_workspace().get_active_document()
        scrolling_position_x, scrolling_position_y = self.application.scrolling.get_current_scrolling_offsets()

        insert = document.get_insert_node()
        x, y = document.get_absolute_xy(insert.layout)
        x -= scrolling_position_x
        y -= scrolling_position_y
        document_view = self.main_window.document_view
        document_view_allocation = document_view.compute_bounds(self.main_window).out_bounds
        x += document_view_allocation.origin.x
        y += document_view_allocation.origin.y
        x += LayoutInfo.get_document_padding_left()
        y += LayoutInfo.get_normal_document_offset()
        fontname = insert.layout['fontname']
        padding_top = TextShaper.get_padding_top(fontname)
        padding_bottom = TextShaper.get_padding_bottom(fontname)
        y += insert.layout['height'] - padding_top - padding_bottom
        x += insert.layout['width'] / 2

        orientation = 'bottom'
        if y + 260 > document_view_allocation.size.height:
            orientation = 'top'
            y -= insert.layout['height'] - padding_top - padding_bottom

        popover = self.application.popover_manager.get_popover('rename_file')
        self.application.popover_manager.show_popover_at_xy(popover, x, y, orientation)


class ToolbarImage(Gtk.Box):

    def __init__(self, main_window, application):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.application = application

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

        self.scale.connect('change-value', self.on_widget_scale_change_value)
        self.shrink_button.connect('clicked', self.on_shrink_button_clicked)
        self.enlarge_button.connect('clicked', self.on_enlarge_button_clicked)

        self.widget = None

    def update(self, widget):
        self.widget = widget

        self.status_label.set_text(self.get_status_text(widget))
        layout = Pango.Layout(self.status_label.get_pango_context())
        layout.set_text(self.get_longest_possible_status_text(widget))
        self.status_label.set_size_request(layout.get_extents()[0].width / Pango.SCALE + 30, -1)

        width, height = widget.get_size()

        self.scale.set_range(LayoutInfo.get_min_image_size(), LayoutInfo.get_max_layout_width())
        self.scale.set_value(width)
        self.scale.clear_marks()

        orig_width = widget.cache['original_width']
        if orig_width > LayoutInfo.get_min_image_size() and orig_width < LayoutInfo.get_max_layout_width():
            self.scale.add_mark(orig_width, Gtk.PositionType.TOP)

        self.shrink_button.set_sensitive(width > LayoutInfo.get_min_image_size())
        self.enlarge_button.set_sensitive(width < LayoutInfo.get_max_layout_width())

    def get_status_text(self, widget):
        width, height = widget.get_size()
        size_string = str(width) + ' × ' + str(height)

        return widget.cache['image_format'] + _(' Image') + ' (' + size_string + ')'

    def get_longest_possible_status_text(self, widget):
        max_width = LayoutInfo.get_max_layout_width()
        max_height = int((max_width / widget.cache['original_width']) * widget.cache['original_height'])
        max_digits = len(str(max_width)) + len(str(max_height))

        return widget.cache['image_format'] + _(' Image') + ' ( × ' + max_digits * '0' + ')'

    def on_widget_scale_change_value(self, scale, scroll, value):
        UseCases.resize_widget(value)
        return True

    def on_shrink_button_clicked(self, button):
        self.application.document_view.view.content.grab_focus()

        if self.widget.get_attribute('width') != None:
            width = self.widget.get_attribute('width')
        else:
            width = min(self.widget.cache['original_width'], LayoutInfo.get_max_layout_width())

        UseCases.resize_widget(width - 1)

    def on_enlarge_button_clicked(self, button):
        self.application.document_view.view.content.grab_focus()

        width, height = widget.get_size()
        UseCases.resize_widget(width + 1)


