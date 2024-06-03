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


class ToolsSidebar(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_size_request(262, 280)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.add_css_class('tools-sidebar')

        self.symbols = list()
        self.symbols.append({'id': 'greek', 'name': 'Greek Letters', 'symbols': ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']})
        self.symbols.append({'id': 'misc', 'name': 'Misc. Symbols', 'symbols': ['neg', 'infty', 'prime', 'backslash', 'emptyset', 'forall', 'exists', 'nexists', 'complement', 'bot', 'top', 'partial', 'nabla', 'mathbbN', 'mathbbZ', 'mathbbQ', 'mathbbI', 'mathbbR', 'mathbbC', 'Im', 'Re', 'aleph', 'wp', 'hbar', 'imath', 'jmath', 'ell', 'sharp', 'flat', 'natural', 'angle', 'sphericalangle', 'measuredangle', 'clubsuit', 'diamondsuit', 'heartsuit', 'spadesuit', 'eth', 'mho']})
        self.symbols.append({'id': 'operators', 'name': 'Operators', 'symbols': ['pm', 'mp', 'setminus', 'cdot', 'times', 'ast', 'star', 'divideontimes', 'circ', 'bullet', 'div', 'cap', 'cup', 'uplus', 'sqcap', 'sqcup', 'triangleleft', 'triangleright', 'wr', 'bigtriangleup', 'bigtriangledown', 'vee', 'wedge', 'oplus', 'ominus', 'otimes', 'oslash', 'odot', 'circledcirc', 'circleddash', 'circledast', 'dotplus', 'leftthreetimes', 'rightthreetimes', 'ltimes', 'rtimes', 'dagger', 'ddagger', 'intercal', 'amalg']})
        self.symbols.append({'id': 'relations', 'name': 'Relations', 'symbols': ['leq', 'geq', 'lneq', 'gneq', 'nleq', 'ngeq', 'nless', 'ngtr', 'll', 'gg', 'neq', 'equiv', 'approx', 'sim', 'simeq', 'cong', 'ncong', 'asymp', 'prec', 'succ', 'nprec', 'nsucc', 'preceq', 'succeq', 'subset', 'supset', 'subseteq', 'supseteq', 'subsetneq', 'supsetneq', 'nsubseteq', 'nsupseteq', 'sqsubset', 'sqsupset', 'sqsubseteq', 'sqsupseteq', 'bowtie', 'in', 'notin', 'propto', 'vdash', 'dashv', 'models', 'smile', 'frown', 'between', 'perp', 'mid', 'nmid', 'parallel', 'nparallel', 'vartriangleleft', 'vartriangleright', 'ntriangleleft', 'ntriangleright', 'trianglelefteq', 'trianglerighteq', 'ntrianglelefteq', 'ntrianglerighteq', 'multimap', 'pitchfork', 'therefore', 'because']})
        self.symbols.append({'id': 'arrows', 'name': 'Arrows', 'symbols': ['leftarrow', 'leftrightarrow', 'rightarrow', 'longleftarrow', 'longleftrightarrow', 'longrightarrow', 'downarrow', 'updownarrow', 'uparrow', 'Leftarrow', 'Leftrightarrow', 'Rightarrow', 'Longleftarrow', 'Longleftrightarrow', 'Longrightarrow', 'Updownarrow', 'Uparrow', 'Downarrow', 'mapsto', 'longmapsto', 'leftharpoondown', 'rightharpoondown', 'leftharpoonup', 'rightharpoonup', 'rightleftharpoons', 'leftrightharpoons', 'downharpoonleft', 'upharpoonleft', 'downharpoonright', 'upharpoonright' , 'nwarrow', 'searrow', 'nearrow', 'swarrow', 'hookleftarrow', 'hookrightarrow', 'curvearrowleft', 'curvearrowright', 'Lsh', 'Rsh', 'looparrowleft', 'looparrowright', 'leftrightsquigarrow', 'rightsquigarrow']})
        self.symbols.append({'id': 'delimiters', 'name': 'Delimiters', 'symbols': ['lparen', 'rparen', 'lbrack', 'rbrack', 'lbrace', 'rbrace', 'lfloor', 'rfloor', 'lceil', 'rceil', 'langle', 'rangle', 'vert', 'Vert']})
        self.symbols.append({'id': 'punctuation', 'name': 'Punctuation', 'symbols': ['cdotp', 'colon', 'vdots', 'cdots']})
        self.symbols.append({'id': 'mathcal', 'name': 'Calligraphic Capitals', 'symbols': ['mathcalA', 'mathcalB', 'mathcalC', 'mathcalD', 'mathcalE', 'mathcalF', 'mathcalG', 'mathcalH', 'mathcalI', 'mathcalJ', 'mathcalK', 'mathcalL', 'mathcalM', 'mathcalN', 'mathcalO', 'mathcalP', 'mathcalQ', 'mathcalR', 'mathcalS', 'mathcalT', 'mathcalU', 'mathcalV', 'mathcalW', 'mathcalX', 'mathcalY', 'mathcalZ']})

        for section in self.symbols:
            header = Gtk.Label.new(section['name'])
            header.set_xalign(Gtk.Align.FILL)
            header.add_css_class('header')
            self.box.append(header)

            flowbox = Gtk.FlowBox()
            flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
            flowbox.set_can_focus(False)
            flowbox.add_css_class(section['id'])
            flowbox.set_max_children_per_line(20)
            for name in section['symbols']:
                button = Gtk.Button.new_from_icon_name('sidebar-' + name + '-symbolic')
                button.set_action_name('win.insert-symbol')
                button.set_can_focus(False)
                button.set_action_target_value(GLib.Variant('as', [name]))
                button.add_css_class('flat')
                flowbox.append(button)
            self.box.append(flowbox)

        self.set_child(self.box)


