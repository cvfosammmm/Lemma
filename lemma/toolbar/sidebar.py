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
        self.set_size_request(262, 280)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.get_style_context().add_class('tools-sidebar')

        self.header_greek = Gtk.Label.new('Greek Letters')
        self.header_greek.set_xalign(Gtk.Align.FILL)
        self.header_greek.get_style_context().add_class('header')
        self.box.append(self.header_greek)

        self.flowbox_greek = Gtk.FlowBox()
        self.flowbox_greek.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox_greek.set_can_focus(False)
        self.flowbox_greek.set_max_children_per_line(20)
        self.symbols_list = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'varGamma', 'Delta', 'varDelta', 'Theta', 'varTheta', 'Lambda', 'varLambda', 'Xi', 'varXi', 'Pi', 'varPi', 'Sigma', 'varSigma', 'Upsilon', 'varUpsilon', 'Phi', 'varPhi', 'Psi', 'varPsi', 'Omega', 'varOmega']
        for name in self.symbols_list:
            button = Gtk.Button.new_from_icon_name('sidebar-' + name + '-symbolic')
            button.set_action_name('win.insert-symbol')
            button.set_can_focus(False)
            button.set_action_target_value(GLib.Variant('as', [name]))
            button.get_style_context().add_class('flat')
            self.flowbox_greek.append(button)
        self.box.append(self.flowbox_greek)

        self.header_arrows = Gtk.Label.new('Arrows')
        self.header_arrows.set_xalign(Gtk.Align.FILL)
        self.header_arrows.get_style_context().add_class('header')
        self.box.append(self.header_arrows)

        self.flowbox_arrows = Gtk.FlowBox()
        self.flowbox_arrows.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox_arrows.set_can_focus(False)
        self.flowbox_arrows.set_max_children_per_line(20)
        self.symbols_list = ['leftarrow', 'leftrightarrow', 'rightarrow', 'mapsto', 'longleftarrow', 'longleftrightarrow', 'longrightarrow', 'longmapsto', 'downarrow', 'updownarrow', 'uparrow', 'nwarrow', 'searrow', 'nearrow', 'swarrow', 'nleftarrow', 'nleftrightarrow', 'nrightarrow', 'hookleftarrow', 'hookrightarrow', 'twoheadleftarrow', 'twoheadrightarrow', 'leftarrowtail', 'rightarrowtail', 'Leftarrow', 'Leftrightarrow', 'Rightarrow', 'Longleftarrow', 'Longleftrightarrow', 'Longrightarrow', 'Updownarrow', 'Uparrow', 'Downarrow', 'nLeftarrow', 'nLeftrightarrow', 'nRightarrow', 'leftleftarrows', 'leftrightarrows', 'rightleftarrows', 'rightrightarrows', 'downdownarrows', 'upuparrows', 'curvearrowleft', 'curvearrowright', 'Lsh', 'Rsh', 'looparrowleft', 'looparrowright', 'leftrightsquigarrow', 'rightsquigarrow', 'Lleftarrow', 'leftharpoondown', 'rightharpoondown', 'leftharpoonup', 'rightharpoonup', 'rightleftharpoons', 'leftrightharpoons', 'downharpoonleft', 'upharpoonleft', 'downharpoonright', 'upharpoonright']
        for name in self.symbols_list:
            button = Gtk.Button.new_from_icon_name('sidebar-' + name + '-symbolic')
            button.set_action_name('win.insert-symbol')
            button.set_can_focus(False)
            button.set_action_target_value(GLib.Variant('as', [name]))
            button.get_style_context().add_class('flat')
            self.flowbox_arrows.append(button)
        self.box.append(self.flowbox_arrows)

        self.set_child(self.box)


