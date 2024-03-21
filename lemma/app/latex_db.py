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


class LaTeXDB(object):

    alphabetical_symbols = {'𝑎', '𝑏', '𝑐', '𝑑', '𝑒', '𝑓', '𝑔', '\u210E', '𝑖', '𝑗', '𝑘', '𝑙', '𝑚', '𝑛', '𝑜', '𝑝', '𝑞', '𝑟', '𝑠', '𝑡', '𝑢', '𝑣', '𝑤', '𝑥', '𝑦', '𝑧', '𝐴', '𝐵', '𝐶', '𝐷', '𝐸', '𝐹', '𝐺', '𝐻', '𝐼', '𝐽', '𝐾', '𝐿', '𝑀', '𝑁', '𝑂', '𝑃', '𝑄', '𝑅', '𝑆', '𝑇', '𝑈', '𝑉', '𝑊', '𝑋', '𝑌', '𝑍', '𝛼', '𝛽', '𝛾', '𝛿', '𝜀', '𝜁', '𝜂', '𝜃', '𝜄', '𝜅', '𝜆', '𝜇', '𝜈', '𝜉', '𝜊', '𝜋', '𝜌', '𝜍', '𝜎', '𝜏', '𝜐', '𝜑', '𝜒', '𝜓', '𝜔', '𝜕', '𝜖', '𝜗', '𝜘', '𝜙', '𝜚', '𝜛', '𝛢', '𝛣', '𝛤', '𝛥', '𝛦', '𝛧', '𝛨', '𝛩', '𝛪', '𝛫', '𝛬', '𝛭', '𝛮', '𝛯', '𝛰', '𝛱', '𝛲', '𝛳', '𝛴', '𝛵', '𝛶', '𝛷', '𝛸', '𝛹', '𝛺', 'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω', 'ϊ', 'ϋ', 'ό', 'ύ', 'ώ', 'Ϗ', 'ϐ', 'ϑ', 'ϒ', 'ϓ', 'ϔ', 'ϕ', 'ϖ', 'ϗ', 'Ϙ', 'ϙ', 'Ϛ', 'ϛ', 'Ϝ', 'ϝ', 'Ϟ', 'ϟ', 'Ϡ', 'ϡ', 'Ϣ', 'ϣ', 'Ϥ', 'ϥ', 'Ϧ', 'ϧ', 'Ϩ', 'ϩ', 'Ϫ', 'ϫ', 'Ϭ', 'ϭ', 'Ϯ', 'ϯ', 'ϰ', 'ϱ', 'ϲ', 'ϳ', 'ϴ', 'ϵ', 'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω'}
    ordinary_symbols = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', '|', '/', '′', '@', '"'}
    binary_operations = {'+', '−', '∗'}
    relations = {'=', '<', '>', ':', '⁐', '←', '↑', '→', '↓', '↔', '↕', '↖', '↗', '↘', '↙', '↚', '↛', '↜', '↝', '↞', '↟', '↠', '↡', '↢', '↣', '↤', '↥', '↦', '↧', '↨', '↩', '↪', '↫', '↬', '↭', '↮', '↯', '↰', '↱', '↲', '↳', '↶', '↷', '↼', '↽', '↾', '↿', '⇀', '⇁', '⇂', '⇃', '⇄', '⇅', '⇆', '⇇', '⇈', '⇉', '⇊', '⇋', '⇌', '⇍', '⇎', '⇏', '⇐', '⇑', '⇒', '⇓', '⇔', '⇕', '⇖', '⇗', '⇘', '⇙', '⇚', '⇛', '⇜', '⇝', '⇤', '⇥', '⇴', '⇵', '⇶', '⇷', '⇸', '⇹', '⇺', '⇻', '⇼', '⇽', '⇾', '⇿', '⟵', '⟶', '⟷', '⟸', '⟹', '⟺', '⟻', '⟼'}
    punctuation_marks = {',', ';'}
    opening_symbols = {'(', '[', '{'}
    closing_symbols = {')', ']', '}'}
    latex_to_unicode = {
        'alpha': '𝛼',
        'beta': '𝛽',
        'gamma': '𝛾',
        'delta': '𝛿',
        'epsilon': '𝜖',
        'varepsilon': '𝜀',
        'zeta': '𝜁',
        'eta': '𝜂',
        'theta': '𝜃',
        'vartheta': '𝜗',
        'iota': '𝜄',
        'kappa': '𝜅',
        'lambda': '𝜆',
        'mu': '𝜇',
        'nu': '𝜈',
        'xi': '𝜉',
        'pi': '𝜋',
        'varpi': '𝜛',
        'rho': '𝜌',
        'varrho': '𝜚',
        'sigma': '𝜎',
        'varsigma': '𝜍',
        'tau': '𝜏',
        'upsilon': '𝜐',
        'phi': '𝜙',
        'varphi': '𝜑',
        'chi': '𝜒',
        'psi': '𝜓',
        'omega': '𝜔',
        'Gamma': 'Γ',
        'varGamma': '𝛤',
        'Delta': 'Δ',
        'varDelta': '𝛥',
        'Theta': 'Θ',
        'varTheta': '𝛩',
        'Lambda': 'Λ',
        'varLambda': '𝛬',
        'Xi': 'Ξ',
        'varXi': '𝛯',
        'Pi': 'Π',
        'varPi': '𝛱',
        'Sigma': 'Σ',
        'varSigma': '𝛴',
        'Upsilon': 'Υ',
        'varUpsilon': '𝛶',
        'Phi': 'Φ',
        'varPhi': '𝛷',
        'Psi': 'Ψ',
        'varPsi': '𝛹',
        'Omega': 'Ω',
        'varOmega': '𝛺',
        'leftarrow': '←',
        'leftrightarrow': '↔',
        'rightarrow': '→',
        'mapsto': '↦',
        'longleftarrow': '⟵',
        'longleftrightarrow': '⟷',
        'longrightarrow': '⟶',
        'longmapsto': '⟼',
        'downarrow': '↓',
        'updownarrow': '↕',
        'uparrow': '↑',
        'nwarrow': '↖',
        'searrow': '↘',
        'nearrow': '↗',
        'swarrow': '↙',
        'nleftarrow': '↚',
        'nleftrightarrow': '↮',
        'nrightarrow': '↛',
        'hookleftarrow': '↩',
        'hookrightarrow': '↪',
        'twoheadleftarrow': '↞',
        'twoheadrightarrow': '↠',
        'leftarrowtail': '↢',
        'rightarrowtail': '↣',
        'Leftarrow': '⇐',
        'Leftrightarrow': '⇔',
        'Rightarrow': '⇒',
        'Longleftarrow': '⟸',
        'Longleftrightarrow': '⟺',
        'Longrightarrow': '⟹',
        'Updownarrow': '⇕',
        'Uparrow': '⇑',
        'Downarrow': '⇓',
        'nLeftarrow': '⇍',
        'nLeftrightarrow': '⇎',
        'nRightarrow': '⇏',
        'leftleftarrows': '⇇',
        'leftrightarrows': '⇆',
        'rightleftarrows': '⇄',
        'rightrightarrows': '⇉',
        'downdownarrows': '⇊',
        'upuparrows': '⇈',
        'curvearrowleft': '↶',
        'curvearrowright': '↷',
        'Lsh': '↰',
        'Rsh': '↱',
        'looparrowleft': '↫',
        'looparrowright': '↬',
        'leftrightsquigarrow': '↭',
        'leftsquigarrow': '⇜',
        'rightsquigarrow': '⇝',
        'Lleftarrow': '⇚',
        'leftharpoondown': '↽',
        'rightharpoondown': '⇁',
        'leftharpoonup': '↼',
        'rightharpoonup': '⇀',
        'rightleftharpoons': '⇌',
        'leftrightharpoons': '⇋',
        'downharpoonleft': '⇃',
        'upharpoonleft': '↿',
        'downharpoonright': '⇂',
        'upharpoonright': '↾'
    }

    def get_unicode_from_latex_name(name):
        return LaTeXDB.latex_to_unicode[name]

    def is_mathsymbol(char):
        return char in LaTeXDB.ordinary_symbols or char in LaTeXDB.binary_operations or char in LaTeXDB.relations or char in LaTeXDB.punctuation_marks or char in LaTeXDB.opening_symbols or char in LaTeXDB.closing_symbols or char in LaTeXDB.alphabetical_symbols

    def is_ordinary_symbol(char):
        return char in LaTeXDB.ordinary_symbols or char in LaTeXDB.alphabetical_symbols

    def is_binary_operation(char):
        return char in LaTeXDB.binary_operations

    def is_relation(char):
        return char in LaTeXDB.relations

    def is_punctuation_mark(char):
        return char in LaTeXDB.punctuation_marks

    def is_opening_symbol(char):
        return char in LaTeXDB.opening_symbols

    def is_closing_symbol(char):
        return char in LaTeXDB.closing_symbols


