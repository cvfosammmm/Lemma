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

        self.symbols = list()
        self.symbols.append({'name': 'Greek Letters', 'symbols': ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'varGamma', 'Delta', 'varDelta', 'Theta', 'varTheta', 'Lambda', 'varLambda', 'Xi', 'varXi', 'Pi', 'varPi', 'Sigma', 'varSigma', 'Upsilon', 'varUpsilon', 'Phi', 'varPhi', 'Psi', 'varPsi', 'Omega', 'varOmega']})
        self.symbols.append({'name': 'Misc. Symbols', 'symbols': ['neg', 'infty', 'prime', 'backslash', 'emptyset', 'forall', 'exists', 'nexists', 'complement', 'bot', 'top', 'partial', 'nabla', 'mathbbN', 'mathbbZ', 'mathbbQ', 'mathbbI', 'mathbbR', 'mathbbC', 'Im', 'Re', 'aleph', 'wp', 'hbar', 'imath', 'jmath', 'ell', 'sharp', 'flat', 'natural', 'angle', 'sphericalangle', 'measuredangle', 'clubsuit', 'diamondsuit', 'heartsuit', 'spadesuit', 'eth', 'mho']})
        self.symbols.append({'name': 'Operators', 'symbols': ['pm', 'mp', 'setminus', 'cdot', 'times', 'ast', 'star', 'divideontimes', 'circ', 'bullet', 'div', 'cap', 'cup', 'uplus', 'sqcap', 'sqcup', 'triangleleft', 'triangleright', 'wr', 'bigtriangleup', 'bigtriangledown', 'vee', 'wedge', 'oplus', 'ominus', 'otimes', 'oslash', 'odot', 'circledcirc', 'circleddash', 'circledast', 'dotplus', 'leftthreetimes', 'rightthreetimes', 'ltimes', 'rtimes', 'dagger', 'ddagger', 'intercal', 'amalg']})
        self.symbols.append({'name': 'Relations', 'symbols': ['leq', 'geq', 'lneq', 'gneq', 'nleq', 'ngeq', 'nless', 'ngtr', 'll', 'gg', 'neq', 'equiv', 'approx', 'sim', 'simeq', 'cong', 'ncong', 'asymp', 'prec', 'succ', 'nprec', 'nsucc', 'preceq', 'succeq', 'subset', 'supset', 'subseteq', 'supseteq', 'subsetneq', 'supsetneq', 'nsubseteq', 'nsupseteq', 'sqsubset', 'sqsupset', 'sqsubseteq', 'sqsupseteq', 'bowtie', 'in', 'notin', 'propto', 'vdash', 'dashv', 'models', 'smile', 'frown', 'between', 'perp', 'mid', 'nmid', 'parallel', 'nparallel', 'vartriangleleft', 'vartriangleright', 'ntriangleleft', 'ntriangleright', 'trianglelefteq', 'trianglerighteq', 'ntrianglelefteq', 'ntrianglerighteq', 'multimap', 'pitchfork', 'therefore', 'because']})
        self.symbols.append({'name': 'Arrows', 'symbols': ['leftarrow', 'leftrightarrow', 'rightarrow', 'mapsto', 'longleftarrow', 'longleftrightarrow', 'longrightarrow', 'longmapsto', 'downarrow', 'updownarrow', 'uparrow', 'nwarrow', 'searrow', 'nearrow', 'swarrow', 'nleftarrow', 'nleftrightarrow', 'nrightarrow', 'hookleftarrow', 'hookrightarrow', 'twoheadleftarrow', 'twoheadrightarrow', 'leftarrowtail', 'rightarrowtail', 'Leftarrow', 'Leftrightarrow', 'Rightarrow', 'Longleftarrow', 'Longleftrightarrow', 'Longrightarrow', 'Updownarrow', 'Uparrow', 'Downarrow', 'nLeftarrow', 'nLeftrightarrow', 'nRightarrow', 'leftleftarrows', 'leftrightarrows', 'rightleftarrows', 'rightrightarrows', 'downdownarrows', 'upuparrows', 'curvearrowleft', 'curvearrowright', 'Lsh', 'Rsh', 'looparrowleft', 'looparrowright', 'leftrightsquigarrow', 'rightsquigarrow', 'Lleftarrow', 'leftharpoondown', 'rightharpoondown', 'leftharpoonup', 'rightharpoonup', 'rightleftharpoons', 'leftrightharpoons', 'downharpoonleft', 'upharpoonleft', 'downharpoonright', 'upharpoonright']})
        self.symbols.append({'name': 'Punctuation', 'symbols': ['cdotp', 'colon', 'vdots', 'cdots']})

        for section in self.symbols:
            header = Gtk.Label.new(section['name'])
            header.set_xalign(Gtk.Align.FILL)
            header.get_style_context().add_class('header')
            self.box.append(header)

            flowbox = Gtk.FlowBox()
            flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
            flowbox.set_can_focus(False)
            flowbox.set_max_children_per_line(20)
            for name in section['symbols']:
                button = Gtk.Button.new_from_icon_name('sidebar-' + name + '-symbolic')
                button.set_action_name('win.insert-symbol')
                button.set_can_focus(False)
                button.set_action_target_value(GLib.Variant('as', [name]))
                button.get_style_context().add_class('flat')
                flowbox.append(button)
            self.box.append(flowbox)

        self.set_child(self.box)


