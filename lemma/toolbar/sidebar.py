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

from lemma.popovers.popover_manager import PopoverManager


class ToolsSidebar(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_size_request(248, 280)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.get_style_context().add_class('tools-sidebar')

        self.header = Gtk.CenterBox()
        self.header.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.header.get_style_context().add_class('header')
        self.header.set_start_widget(Gtk.Label.new('Greek Letters'))

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_can_focus(False)
        self.flowbox.set_row_spacing(1)
        self.flowbox.set_column_spacing(1)
        self.flowbox.set_max_children_per_line(20)

        self.symbols_list = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'varGamma', 'Delta', 'varDelta', 'Theta', 'varTheta', 'Lambda', 'varLambda', 'Xi', 'varXi', 'Pi', 'varPi', 'Sigma', 'varSigma', 'Upsilon', 'varUpsilon', 'Phi', 'varPhi', 'Psi', 'varPsi', 'Omega', 'varOmega']
        for name in self.symbols_list:
            button = Gtk.Button.new_from_icon_name('sidebar-' + name + '-symbolic')
            button.set_action_name('win.insert-symbol')
            button.set_can_focus(False)
            button.set_action_target_value(GLib.Variant('as', [name]))
            button.get_style_context().add_class('flat')
            self.flowbox.append(button)

        self.box.append(self.header)
        self.box.append(self.flowbox)

        self.set_child(self.box)


