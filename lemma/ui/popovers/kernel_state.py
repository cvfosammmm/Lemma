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

from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.code_runner import CodeRunner
from lemma.ui.popovers.popover_menu_builder import MenuBuilder
from lemma.ui.popovers.popover_templates import PopoverView
from lemma.use_cases.use_cases import UseCases


class Popover(PopoverView):

    def __init__(self):
        PopoverView.__init__(self)

        self.add_css_class('kernel-state')
        self.set_width(342)

        self.headline = Gtk.Label.new('Computation')
        self.headline.add_css_class('title-2')
        self.headline.set_xalign(0)
        self.headline.set_margin_bottom(2)
        self.add_widget(self.headline)

        self.kernel_label = Gtk.Label()
        self.kernel_label.set_markup('<b>Kernel:</b> Python3')
        self.kernel_label.set_xalign(0)
        self.kernel_label.add_css_class('status')
        self.add_widget(self.kernel_label)

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        self.status_label.add_css_class('status')
        self.add_widget(self.status_label)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.restart_kernel_button = MenuBuilder.create_button(_('Restart Kernel'))
        self.register_button_for_keyboard_navigation(self.restart_kernel_button)
        self.add_widget(self.restart_kernel_button)

        self.restart_kernel_button.connect('clicked', self.restart_kernel)

    def animate(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        running_computations = CodeRunner.get_running_computations(document.id)
        if len(running_computations) > 0:
            self.status_label.set_markup('<b>Status:</b> Busy (Running ' + str(len(running_computations)) + ' Computation' + ('s' if len(running_computations) > 1 else '') + ')')
        else:
            self.status_label.set_markup('<b>Status:</b> Idle')

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('0'):
            if state & modifiers == Gdk.ModifierType.ALT_MASK:
                UseCases.hide_popovers()

                return True

        return super().on_keypress(controller, keyval, keycode, state)

    def on_popup(self):
        self.edit_mode = False

    def on_popdown(self):
        self.edit_mode = False

    def restart_kernel(self, button):
        document = WorkspaceRepo.get_workspace().get_active_document()
        CodeRunner.restart_kernel(document.id)


