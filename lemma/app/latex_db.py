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

    ordinary_symbols = ['𝑎', '𝑏', '𝑐', '𝑑', '𝑒', '𝑓', '𝑔', '𝑕', '𝑖', '𝑗', '𝑘', '𝑙', '𝑚', '𝑛', '𝑜', '𝑝', '𝑞', '𝑟', '𝑠', '𝑡', '𝑢', '𝑣', '𝑤', '𝑥', '𝑦', '𝑧', '𝐴', '𝐵', '𝐶', '𝐷', '𝐸', '𝐹', '𝐺', '𝐻', '𝐼', '𝐽', '𝐾', '𝐿', '𝑀', '𝑁', '𝑂', '𝑃', '𝑄', '𝑅', '𝑆', '𝑇', '𝑈', '𝑉', '𝑊', '𝑋', '𝑌', '𝑍', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', '|', '/', '\'', '@', '"']
    binary_operations = ['+', '−', '∗']
    relations = ['=', '<', '>', ':']
    latex_to_unicode = {
        'alpha': 'α',
        'beta': 'β',
        'gamma': 'γ',
        'delta': 'δ',
        'epsilon': 'ε',
        'zeta': 'ζ',
        'eta': 'η',
        'theta': 'θ',
        'vartheta': 'ϑ',
        'iota': 'ι',
        'kappa': 'κ',
        'lambda': 'λ',
        'mu': 'μ',
        'nu': 'ν',
        'xi': 'ξ',
        'pi': 'π',
        'varpi': 'ϖ',
        'rho': 'ρ',
        'varrho': 'ϱ',
        'sigma': 'σ',
        'varsigma': 'ς',
        'tau': 'τ',
        'upsilon': 'υ',
        'phi': 'ϕ',
        'varphi': 'φ',
        'chi': 'χ',
        'psi': 'ψ',
        'omega': 'ω',
        'Gamma': 'Γ',
        'Delta': 'Δ',
        'Theta': 'Θ',
        'Lambda': 'Λ',
        'Xi': 'Ξ',
        'Pi': 'Π',
        'Sigma': 'Σ',
        'Upsilon': 'Υ',
        'Phi': 'Φ',
        'Psi': 'Ψ',
        'Omega': 'Ω'
    }

    def get_unicode_from_latex_name(name):
        return LaTeXDB.latex_to_unicode[name]

    def is_mathsymbol(char):
        return char in LaTeXDB.ordinary_symbols or char in LaTeXDB.binary_operations or char in LaTeXDB.relations


