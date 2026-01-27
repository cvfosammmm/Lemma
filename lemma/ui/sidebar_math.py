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
gi.require_version('Adw', '1')
gi.require_version('Rsvg', '2.0')
from gi.repository import Gtk
from gi.repository import Adw
from gi.repository import Rsvg

import os.path

from lemma.services.color_manager import ColorManager
from lemma.services.message_bus import MessageBus
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.paths import Paths
from lemma.services.character_db import CharacterDB
from lemma.use_cases.use_cases import UseCases
from lemma.services.settings import Settings
import lemma.services.timer as timer


class SidebarMath(object):

    def __init__(self, main_window, application):
        self.view = main_window.tools_sidebar
        self.application = application

        self.data = dict()
        self.data['math_typesetting'] = {'title': 'Math Typesetting', 'symbols': []}
        self.data['math_typesetting']['symbols'].append(['subscript', '<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>'])
        self.data['math_typesetting']['symbols'].append(['superscript', '<placeholder marks="prev_selection"/><mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'])
        self.data['math_typesetting']['symbols'].append(['subsuperscript', '<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>'])
        self.data['math_typesetting']['symbols'].append(['fraction', '<mathfraction><mathlist><placeholder marks="prev_selection"/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathfraction>'])
        self.data['math_typesetting']['symbols'].append(['sqrt', '<mathroot><mathlist><placeholder marks="prev_selection"/><end/></mathlist><mathlist></mathlist></mathroot>'])
        self.data['math_typesetting']['symbols'].append(['nthroot', '<mathroot><mathlist><placeholder marks="prev_selection"/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathroot>'])
        self.data['math_typesetting']['symbols'].append(['sumwithindex', '∑<mathscript><mathlist><placeholder/>=<placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/>'])
        self.data['math_typesetting']['symbols'].append(['prodwithindex', '∏<mathscript><mathlist><placeholder/>=<placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/>'])
        self.data['math_typesetting']['symbols'].append(['indefint', '∫ <placeholder marks="prev_selection"/> 𝑑<placeholder/>'])
        self.data['math_typesetting']['symbols'].append(['defint', '∫<mathscript><mathlist><placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/> 𝑑<placeholder/>'])
        self.data['math_typesetting']['symbols'].append(['limitwithindex', 'lim<mathscript><mathlist><placeholder/> → <placeholder/><end/></mathlist><mathlist></mathlist></mathscript> <placeholder marks="prev_selection"/>'])

        self.data['punctuation'] = {'title': 'Punctuation', 'symbols': []}
        self.data['punctuation']['symbols'].append(['textendash', CharacterDB.get_unicode_from_latex_name('textendash')])
        self.data['punctuation']['symbols'].append(['textemdash', CharacterDB.get_unicode_from_latex_name('textemdash')])
        self.data['punctuation']['symbols'].append(['guillemetleft', CharacterDB.get_unicode_from_latex_name('guillemetleft')])
        self.data['punctuation']['symbols'].append(['guillemetright', CharacterDB.get_unicode_from_latex_name('guillemetright')])
        self.data['punctuation']['symbols'].append(['quotedblbase', CharacterDB.get_unicode_from_latex_name('quotedblbase')])
        self.data['punctuation']['symbols'].append(['textquotedblleft', CharacterDB.get_unicode_from_latex_name('textquotedblleft')])
        self.data['punctuation']['symbols'].append(['textquotedblright', CharacterDB.get_unicode_from_latex_name('textquotedblright')])
        self.data['punctuation']['symbols'].append(['cdotp', CharacterDB.get_unicode_from_latex_name('cdotp')])
        self.data['punctuation']['symbols'].append(['colon', CharacterDB.get_unicode_from_latex_name('colon')])
        self.data['punctuation']['symbols'].append(['vdots', CharacterDB.get_unicode_from_latex_name('vdots')])
        self.data['punctuation']['symbols'].append(['cdots', CharacterDB.get_unicode_from_latex_name('cdots')])

        self.data['greek_letters'] = {'title': 'Greek Letters', 'symbols': []}
        self.data['greek_letters']['symbols'].append(['alpha', CharacterDB.get_unicode_from_latex_name('alpha')])
        self.data['greek_letters']['symbols'].append(['beta', CharacterDB.get_unicode_from_latex_name('beta')])
        self.data['greek_letters']['symbols'].append(['gamma', CharacterDB.get_unicode_from_latex_name('gamma')])
        self.data['greek_letters']['symbols'].append(['delta', CharacterDB.get_unicode_from_latex_name('delta')])
        self.data['greek_letters']['symbols'].append(['epsilon', CharacterDB.get_unicode_from_latex_name('epsilon')])
        self.data['greek_letters']['symbols'].append(['zeta', CharacterDB.get_unicode_from_latex_name('zeta')])
        self.data['greek_letters']['symbols'].append(['eta', CharacterDB.get_unicode_from_latex_name('eta')])
        self.data['greek_letters']['symbols'].append(['theta', CharacterDB.get_unicode_from_latex_name('theta')])
        self.data['greek_letters']['symbols'].append(['vartheta', CharacterDB.get_unicode_from_latex_name('vartheta')])
        self.data['greek_letters']['symbols'].append(['iota', CharacterDB.get_unicode_from_latex_name('iota')])
        self.data['greek_letters']['symbols'].append(['kappa', CharacterDB.get_unicode_from_latex_name('kappa')])
        self.data['greek_letters']['symbols'].append(['lambda', CharacterDB.get_unicode_from_latex_name('lambda')])
        self.data['greek_letters']['symbols'].append(['mu', CharacterDB.get_unicode_from_latex_name('mu')])
        self.data['greek_letters']['symbols'].append(['nu', CharacterDB.get_unicode_from_latex_name('nu')])
        self.data['greek_letters']['symbols'].append(['xi', CharacterDB.get_unicode_from_latex_name('xi')])
        self.data['greek_letters']['symbols'].append(['pi', CharacterDB.get_unicode_from_latex_name('pi')])
        self.data['greek_letters']['symbols'].append(['varpi', CharacterDB.get_unicode_from_latex_name('varpi')])
        self.data['greek_letters']['symbols'].append(['rho', CharacterDB.get_unicode_from_latex_name('rho')])
        self.data['greek_letters']['symbols'].append(['varrho', CharacterDB.get_unicode_from_latex_name('varrho')])
        self.data['greek_letters']['symbols'].append(['sigma', CharacterDB.get_unicode_from_latex_name('sigma')])
        self.data['greek_letters']['symbols'].append(['varsigma', CharacterDB.get_unicode_from_latex_name('varsigma')])
        self.data['greek_letters']['symbols'].append(['tau', CharacterDB.get_unicode_from_latex_name('tau')])
        self.data['greek_letters']['symbols'].append(['upsilon', CharacterDB.get_unicode_from_latex_name('upsilon')])
        self.data['greek_letters']['symbols'].append(['phi', CharacterDB.get_unicode_from_latex_name('phi')])
        self.data['greek_letters']['symbols'].append(['varphi', CharacterDB.get_unicode_from_latex_name('varphi')])
        self.data['greek_letters']['symbols'].append(['chi', CharacterDB.get_unicode_from_latex_name('chi')])
        self.data['greek_letters']['symbols'].append(['psi', CharacterDB.get_unicode_from_latex_name('psi')])
        self.data['greek_letters']['symbols'].append(['omega', CharacterDB.get_unicode_from_latex_name('omega')])
        self.data['greek_letters']['symbols'].append(['Gamma', CharacterDB.get_unicode_from_latex_name('Gamma')])
        self.data['greek_letters']['symbols'].append(['Delta', CharacterDB.get_unicode_from_latex_name('Delta')])
        self.data['greek_letters']['symbols'].append(['Theta', CharacterDB.get_unicode_from_latex_name('Theta')])
        self.data['greek_letters']['symbols'].append(['Lambda', CharacterDB.get_unicode_from_latex_name('Lambda')])
        self.data['greek_letters']['symbols'].append(['Xi', CharacterDB.get_unicode_from_latex_name('Xi')])
        self.data['greek_letters']['symbols'].append(['Pi', CharacterDB.get_unicode_from_latex_name('Pi')])
        self.data['greek_letters']['symbols'].append(['Sigma', CharacterDB.get_unicode_from_latex_name('Sigma')])
        self.data['greek_letters']['symbols'].append(['Upsilon', CharacterDB.get_unicode_from_latex_name('Upsilon')])
        self.data['greek_letters']['symbols'].append(['Phi', CharacterDB.get_unicode_from_latex_name('Phi')])
        self.data['greek_letters']['symbols'].append(['Psi', CharacterDB.get_unicode_from_latex_name('Psi')])
        self.data['greek_letters']['symbols'].append(['Omega', CharacterDB.get_unicode_from_latex_name('Omega')])

        self.data['misc_symbols'] = {'title': 'Misc. Symbols', 'symbols': []}
        self.data['misc_symbols']['symbols'].append(['neg', CharacterDB.get_unicode_from_latex_name('neg')])
        self.data['misc_symbols']['symbols'].append(['infty', CharacterDB.get_unicode_from_latex_name('infty')])
        self.data['misc_symbols']['symbols'].append(['prime', CharacterDB.get_unicode_from_latex_name('prime')])
        self.data['misc_symbols']['symbols'].append(['backslash', CharacterDB.get_unicode_from_latex_name('backslash')])
        self.data['misc_symbols']['symbols'].append(['emptyset', CharacterDB.get_unicode_from_latex_name('emptyset')])
        self.data['misc_symbols']['symbols'].append(['forall', CharacterDB.get_unicode_from_latex_name('forall')])
        self.data['misc_symbols']['symbols'].append(['exists', CharacterDB.get_unicode_from_latex_name('exists')])
        self.data['misc_symbols']['symbols'].append(['nexists', CharacterDB.get_unicode_from_latex_name('nexists')])
        self.data['misc_symbols']['symbols'].append(['complement', CharacterDB.get_unicode_from_latex_name('complement')])
        self.data['misc_symbols']['symbols'].append(['bot', CharacterDB.get_unicode_from_latex_name('bot')])
        self.data['misc_symbols']['symbols'].append(['top', CharacterDB.get_unicode_from_latex_name('top')])
        self.data['misc_symbols']['symbols'].append(['partial', CharacterDB.get_unicode_from_latex_name('partial')])
        self.data['misc_symbols']['symbols'].append(['nabla', CharacterDB.get_unicode_from_latex_name('nabla')])
        self.data['misc_symbols']['symbols'].append(['mathbbN', CharacterDB.get_unicode_from_latex_name('mathbbN')])
        self.data['misc_symbols']['symbols'].append(['mathbbZ', CharacterDB.get_unicode_from_latex_name('mathbbZ')])
        self.data['misc_symbols']['symbols'].append(['mathbbQ', CharacterDB.get_unicode_from_latex_name('mathbbQ')])
        self.data['misc_symbols']['symbols'].append(['mathbbI', CharacterDB.get_unicode_from_latex_name('mathbbI')])
        self.data['misc_symbols']['symbols'].append(['mathbbR', CharacterDB.get_unicode_from_latex_name('mathbbR')])
        self.data['misc_symbols']['symbols'].append(['mathbbC', CharacterDB.get_unicode_from_latex_name('mathbbC')])
        self.data['misc_symbols']['symbols'].append(['Im', CharacterDB.get_unicode_from_latex_name('Im')])
        self.data['misc_symbols']['symbols'].append(['Re', CharacterDB.get_unicode_from_latex_name('Re')])
        self.data['misc_symbols']['symbols'].append(['aleph', CharacterDB.get_unicode_from_latex_name('aleph')])
        self.data['misc_symbols']['symbols'].append(['wp', CharacterDB.get_unicode_from_latex_name('wp')])
        self.data['misc_symbols']['symbols'].append(['hbar', CharacterDB.get_unicode_from_latex_name('hbar')])
        self.data['misc_symbols']['symbols'].append(['imath', CharacterDB.get_unicode_from_latex_name('imath')])
        self.data['misc_symbols']['symbols'].append(['jmath', CharacterDB.get_unicode_from_latex_name('jmath')])
        self.data['misc_symbols']['symbols'].append(['ell', CharacterDB.get_unicode_from_latex_name('ell')])
        self.data['misc_symbols']['symbols'].append(['sharp', CharacterDB.get_unicode_from_latex_name('sharp')])
        self.data['misc_symbols']['symbols'].append(['flat', CharacterDB.get_unicode_from_latex_name('flat')])
        self.data['misc_symbols']['symbols'].append(['natural', CharacterDB.get_unicode_from_latex_name('natural')])
        self.data['misc_symbols']['symbols'].append(['angle', CharacterDB.get_unicode_from_latex_name('angle')])
        self.data['misc_symbols']['symbols'].append(['sphericalangle', CharacterDB.get_unicode_from_latex_name('sphericalangle')])
        self.data['misc_symbols']['symbols'].append(['measuredangle', CharacterDB.get_unicode_from_latex_name('measuredangle')])
        self.data['misc_symbols']['symbols'].append(['clubsuit', CharacterDB.get_unicode_from_latex_name('clubsuit')])
        self.data['misc_symbols']['symbols'].append(['diamondsuit', CharacterDB.get_unicode_from_latex_name('diamondsuit')])
        self.data['misc_symbols']['symbols'].append(['heartsuit', CharacterDB.get_unicode_from_latex_name('heartsuit')])
        self.data['misc_symbols']['symbols'].append(['spadesuit', CharacterDB.get_unicode_from_latex_name('spadesuit')])
        self.data['misc_symbols']['symbols'].append(['eth', CharacterDB.get_unicode_from_latex_name('eth')])
        self.data['misc_symbols']['symbols'].append(['mho', CharacterDB.get_unicode_from_latex_name('mho')])

        self.data['operators'] = {'title': 'Operators', 'symbols': []}
        self.data['operators']['symbols'].append(['pm', CharacterDB.get_unicode_from_latex_name('pm')])
        self.data['operators']['symbols'].append(['mp', CharacterDB.get_unicode_from_latex_name('mp')])
        self.data['operators']['symbols'].append(['setminus', CharacterDB.get_unicode_from_latex_name('setminus')])
        self.data['operators']['symbols'].append(['cdot', CharacterDB.get_unicode_from_latex_name('cdot')])
        self.data['operators']['symbols'].append(['times', CharacterDB.get_unicode_from_latex_name('times')])
        self.data['operators']['symbols'].append(['ast', CharacterDB.get_unicode_from_latex_name('ast')])
        self.data['operators']['symbols'].append(['star', CharacterDB.get_unicode_from_latex_name('star')])
        self.data['operators']['symbols'].append(['divideontimes', CharacterDB.get_unicode_from_latex_name('divideontimes')])
        self.data['operators']['symbols'].append(['circ', CharacterDB.get_unicode_from_latex_name('circ')])
        self.data['operators']['symbols'].append(['bullet', CharacterDB.get_unicode_from_latex_name('bullet')])
        self.data['operators']['symbols'].append(['div', CharacterDB.get_unicode_from_latex_name('div')])
        self.data['operators']['symbols'].append(['cap', CharacterDB.get_unicode_from_latex_name('cap')])
        self.data['operators']['symbols'].append(['cup', CharacterDB.get_unicode_from_latex_name('cup')])
        self.data['operators']['symbols'].append(['uplus', CharacterDB.get_unicode_from_latex_name('uplus')])
        self.data['operators']['symbols'].append(['sqcap', CharacterDB.get_unicode_from_latex_name('sqcap')])
        self.data['operators']['symbols'].append(['sqcup', CharacterDB.get_unicode_from_latex_name('sqcup')])
        self.data['operators']['symbols'].append(['triangleleft', CharacterDB.get_unicode_from_latex_name('triangleleft')])
        self.data['operators']['symbols'].append(['triangleright', CharacterDB.get_unicode_from_latex_name('triangleright')])
        self.data['operators']['symbols'].append(['wr', CharacterDB.get_unicode_from_latex_name('wr')])
        self.data['operators']['symbols'].append(['bigtriangleup', CharacterDB.get_unicode_from_latex_name('bigtriangleup')])
        self.data['operators']['symbols'].append(['bigtriangledown', CharacterDB.get_unicode_from_latex_name('bigtriangledown')])
        self.data['operators']['symbols'].append(['vee', CharacterDB.get_unicode_from_latex_name('vee')])
        self.data['operators']['symbols'].append(['wedge', CharacterDB.get_unicode_from_latex_name('wedge')])
        self.data['operators']['symbols'].append(['oplus', CharacterDB.get_unicode_from_latex_name('oplus')])
        self.data['operators']['symbols'].append(['ominus', CharacterDB.get_unicode_from_latex_name('ominus')])
        self.data['operators']['symbols'].append(['otimes', CharacterDB.get_unicode_from_latex_name('otimes')])
        self.data['operators']['symbols'].append(['oslash', CharacterDB.get_unicode_from_latex_name('oslash')])
        self.data['operators']['symbols'].append(['odot', CharacterDB.get_unicode_from_latex_name('odot')])
        self.data['operators']['symbols'].append(['circledcirc', CharacterDB.get_unicode_from_latex_name('circledcirc')])
        self.data['operators']['symbols'].append(['circleddash', CharacterDB.get_unicode_from_latex_name('circleddash')])
        self.data['operators']['symbols'].append(['circledast', CharacterDB.get_unicode_from_latex_name('circledast')])
        self.data['operators']['symbols'].append(['dotplus', CharacterDB.get_unicode_from_latex_name('dotplus')])
        self.data['operators']['symbols'].append(['leftthreetimes', CharacterDB.get_unicode_from_latex_name('leftthreetimes')])
        self.data['operators']['symbols'].append(['rightthreetimes', CharacterDB.get_unicode_from_latex_name('rightthreetimes')])
        self.data['operators']['symbols'].append(['ltimes', CharacterDB.get_unicode_from_latex_name('ltimes')])
        self.data['operators']['symbols'].append(['rtimes', CharacterDB.get_unicode_from_latex_name('rtimes')])
        self.data['operators']['symbols'].append(['dagger', CharacterDB.get_unicode_from_latex_name('dagger')])
        self.data['operators']['symbols'].append(['ddagger', CharacterDB.get_unicode_from_latex_name('ddagger')])
        self.data['operators']['symbols'].append(['intercal', CharacterDB.get_unicode_from_latex_name('intercal')])
        self.data['operators']['symbols'].append(['amalg', CharacterDB.get_unicode_from_latex_name('amalg')])

        self.data['big_operators'] = {'title': 'Big Operators', 'symbols': []}
        self.data['big_operators']['symbols'].append(['sum', CharacterDB.get_unicode_from_latex_name('sum')])
        self.data['big_operators']['symbols'].append(['prod', CharacterDB.get_unicode_from_latex_name('prod')])
        self.data['big_operators']['symbols'].append(['coprod', CharacterDB.get_unicode_from_latex_name('coprod')])
        self.data['big_operators']['symbols'].append(['int', CharacterDB.get_unicode_from_latex_name('int')])
        self.data['big_operators']['symbols'].append(['iint', CharacterDB.get_unicode_from_latex_name('iint')])
        self.data['big_operators']['symbols'].append(['iiint', CharacterDB.get_unicode_from_latex_name('iiint')])
        self.data['big_operators']['symbols'].append(['bigcap', CharacterDB.get_unicode_from_latex_name('bigcap')])
        self.data['big_operators']['symbols'].append(['bigcup', CharacterDB.get_unicode_from_latex_name('bigcup')])
        self.data['big_operators']['symbols'].append(['bigodot', CharacterDB.get_unicode_from_latex_name('bigodot')])
        self.data['big_operators']['symbols'].append(['bigoplus', CharacterDB.get_unicode_from_latex_name('bigoplus')])
        self.data['big_operators']['symbols'].append(['bigotimes', CharacterDB.get_unicode_from_latex_name('bigotimes')])
        self.data['big_operators']['symbols'].append(['bigwedge', CharacterDB.get_unicode_from_latex_name('bigwedge')])
        self.data['big_operators']['symbols'].append(['bigvee', CharacterDB.get_unicode_from_latex_name('bigvee')])

        self.data['relations'] = {'title': 'Relations', 'symbols': []}
        self.data['relations']['symbols'].append(['leq', CharacterDB.get_unicode_from_latex_name('leq')])
        self.data['relations']['symbols'].append(['geq', CharacterDB.get_unicode_from_latex_name('geq')])
        self.data['relations']['symbols'].append(['lneq', CharacterDB.get_unicode_from_latex_name('lneq')])
        self.data['relations']['symbols'].append(['gneq', CharacterDB.get_unicode_from_latex_name('gneq')])
        self.data['relations']['symbols'].append(['nleq', CharacterDB.get_unicode_from_latex_name('nleq')])
        self.data['relations']['symbols'].append(['ngeq', CharacterDB.get_unicode_from_latex_name('ngeq')])
        self.data['relations']['symbols'].append(['nless', CharacterDB.get_unicode_from_latex_name('nless')])
        self.data['relations']['symbols'].append(['ngtr', CharacterDB.get_unicode_from_latex_name('ngtr')])
        self.data['relations']['symbols'].append(['ll', CharacterDB.get_unicode_from_latex_name('ll')])
        self.data['relations']['symbols'].append(['gg', CharacterDB.get_unicode_from_latex_name('gg')])
        self.data['relations']['symbols'].append(['neq', CharacterDB.get_unicode_from_latex_name('neq')])
        self.data['relations']['symbols'].append(['equiv', CharacterDB.get_unicode_from_latex_name('equiv')])
        self.data['relations']['symbols'].append(['approx', CharacterDB.get_unicode_from_latex_name('approx')])
        self.data['relations']['symbols'].append(['sim', CharacterDB.get_unicode_from_latex_name('sim')])
        self.data['relations']['symbols'].append(['simeq', CharacterDB.get_unicode_from_latex_name('simeq')])
        self.data['relations']['symbols'].append(['cong', CharacterDB.get_unicode_from_latex_name('cong')])
        self.data['relations']['symbols'].append(['ncong', CharacterDB.get_unicode_from_latex_name('ncong')])
        self.data['relations']['symbols'].append(['asymp', CharacterDB.get_unicode_from_latex_name('asymp')])
        self.data['relations']['symbols'].append(['prec', CharacterDB.get_unicode_from_latex_name('prec')])
        self.data['relations']['symbols'].append(['succ', CharacterDB.get_unicode_from_latex_name('succ')])
        self.data['relations']['symbols'].append(['nprec', CharacterDB.get_unicode_from_latex_name('nprec')])
        self.data['relations']['symbols'].append(['nsucc', CharacterDB.get_unicode_from_latex_name('nsucc')])
        self.data['relations']['symbols'].append(['preceq', CharacterDB.get_unicode_from_latex_name('preceq')])
        self.data['relations']['symbols'].append(['succeq', CharacterDB.get_unicode_from_latex_name('succeq')])
        self.data['relations']['symbols'].append(['subset', CharacterDB.get_unicode_from_latex_name('subset')])
        self.data['relations']['symbols'].append(['supset', CharacterDB.get_unicode_from_latex_name('supset')])
        self.data['relations']['symbols'].append(['subseteq', CharacterDB.get_unicode_from_latex_name('subseteq')])
        self.data['relations']['symbols'].append(['supseteq', CharacterDB.get_unicode_from_latex_name('supseteq')])
        self.data['relations']['symbols'].append(['subsetneq', CharacterDB.get_unicode_from_latex_name('subsetneq')])
        self.data['relations']['symbols'].append(['supsetneq', CharacterDB.get_unicode_from_latex_name('supsetneq')])
        self.data['relations']['symbols'].append(['nsubseteq', CharacterDB.get_unicode_from_latex_name('nsubseteq')])
        self.data['relations']['symbols'].append(['nsupseteq', CharacterDB.get_unicode_from_latex_name('nsupseteq')])
        self.data['relations']['symbols'].append(['sqsubset', CharacterDB.get_unicode_from_latex_name('sqsubset')])
        self.data['relations']['symbols'].append(['sqsupset', CharacterDB.get_unicode_from_latex_name('sqsupset')])
        self.data['relations']['symbols'].append(['sqsubseteq', CharacterDB.get_unicode_from_latex_name('sqsubseteq')])
        self.data['relations']['symbols'].append(['sqsupseteq', CharacterDB.get_unicode_from_latex_name('sqsupseteq')])
        self.data['relations']['symbols'].append(['bowtie', CharacterDB.get_unicode_from_latex_name('bowtie')])
        self.data['relations']['symbols'].append(['in', CharacterDB.get_unicode_from_latex_name('in')])
        self.data['relations']['symbols'].append(['notin', CharacterDB.get_unicode_from_latex_name('notin')])
        self.data['relations']['symbols'].append(['propto', CharacterDB.get_unicode_from_latex_name('propto')])
        self.data['relations']['symbols'].append(['vdash', CharacterDB.get_unicode_from_latex_name('vdash')])
        self.data['relations']['symbols'].append(['dashv', CharacterDB.get_unicode_from_latex_name('dashv')])
        self.data['relations']['symbols'].append(['models', CharacterDB.get_unicode_from_latex_name('models')])
        self.data['relations']['symbols'].append(['smile', CharacterDB.get_unicode_from_latex_name('smile')])
        self.data['relations']['symbols'].append(['frown', CharacterDB.get_unicode_from_latex_name('frown')])
        self.data['relations']['symbols'].append(['between', CharacterDB.get_unicode_from_latex_name('between')])
        self.data['relations']['symbols'].append(['perp', CharacterDB.get_unicode_from_latex_name('perp')])
        self.data['relations']['symbols'].append(['mid', CharacterDB.get_unicode_from_latex_name('mid')])
        self.data['relations']['symbols'].append(['nmid', CharacterDB.get_unicode_from_latex_name('nmid')])
        self.data['relations']['symbols'].append(['parallel', CharacterDB.get_unicode_from_latex_name('parallel')])
        self.data['relations']['symbols'].append(['nparallel', CharacterDB.get_unicode_from_latex_name('nparallel')])
        self.data['relations']['symbols'].append(['vartriangleleft', CharacterDB.get_unicode_from_latex_name('vartriangleleft')])
        self.data['relations']['symbols'].append(['vartriangleright', CharacterDB.get_unicode_from_latex_name('vartriangleright')])
        self.data['relations']['symbols'].append(['ntriangleleft', CharacterDB.get_unicode_from_latex_name('ntriangleleft')])
        self.data['relations']['symbols'].append(['ntriangleright', CharacterDB.get_unicode_from_latex_name('ntriangleright')])
        self.data['relations']['symbols'].append(['trianglelefteq', CharacterDB.get_unicode_from_latex_name('trianglelefteq')])
        self.data['relations']['symbols'].append(['trianglerighteq', CharacterDB.get_unicode_from_latex_name('trianglerighteq')])
        self.data['relations']['symbols'].append(['ntrianglelefteq', CharacterDB.get_unicode_from_latex_name('ntrianglelefteq')])
        self.data['relations']['symbols'].append(['ntrianglerighteq', CharacterDB.get_unicode_from_latex_name('ntrianglerighteq')])
        self.data['relations']['symbols'].append(['multimap', CharacterDB.get_unicode_from_latex_name('multimap')])
        self.data['relations']['symbols'].append(['pitchfork', CharacterDB.get_unicode_from_latex_name('pitchfork')])
        self.data['relations']['symbols'].append(['therefore', CharacterDB.get_unicode_from_latex_name('therefore')])
        self.data['relations']['symbols'].append(['because', CharacterDB.get_unicode_from_latex_name('because')])

        self.data['arrows'] = {'title': 'Arrows', 'symbols': []}
        self.data['arrows']['symbols'].append(['leftarrow', CharacterDB.get_unicode_from_latex_name('leftarrow')])
        self.data['arrows']['symbols'].append(['leftrightarrow', CharacterDB.get_unicode_from_latex_name('leftrightarrow')])
        self.data['arrows']['symbols'].append(['rightarrow', CharacterDB.get_unicode_from_latex_name('rightarrow')])
        self.data['arrows']['symbols'].append(['longleftarrow', CharacterDB.get_unicode_from_latex_name('longleftarrow')])
        self.data['arrows']['symbols'].append(['longleftrightarrow', CharacterDB.get_unicode_from_latex_name('longleftrightarrow')])
        self.data['arrows']['symbols'].append(['longrightarrow', CharacterDB.get_unicode_from_latex_name('longrightarrow')])
        self.data['arrows']['symbols'].append(['downarrow', CharacterDB.get_unicode_from_latex_name('downarrow')])
        self.data['arrows']['symbols'].append(['updownarrow', CharacterDB.get_unicode_from_latex_name('updownarrow')])
        self.data['arrows']['symbols'].append(['uparrow', CharacterDB.get_unicode_from_latex_name('uparrow')])
        self.data['arrows']['symbols'].append(['Leftarrow', CharacterDB.get_unicode_from_latex_name('Leftarrow')])
        self.data['arrows']['symbols'].append(['Leftrightarrow', CharacterDB.get_unicode_from_latex_name('Leftrightarrow')])
        self.data['arrows']['symbols'].append(['Rightarrow', CharacterDB.get_unicode_from_latex_name('Rightarrow')])
        self.data['arrows']['symbols'].append(['Longleftarrow', CharacterDB.get_unicode_from_latex_name('Longleftarrow')])
        self.data['arrows']['symbols'].append(['Longleftrightarrow', CharacterDB.get_unicode_from_latex_name('Longleftrightarrow')])
        self.data['arrows']['symbols'].append(['Longrightarrow', CharacterDB.get_unicode_from_latex_name('Longrightarrow')])
        self.data['arrows']['symbols'].append(['Updownarrow', CharacterDB.get_unicode_from_latex_name('Updownarrow')])
        self.data['arrows']['symbols'].append(['Uparrow', CharacterDB.get_unicode_from_latex_name('Uparrow')])
        self.data['arrows']['symbols'].append(['Downarrow', CharacterDB.get_unicode_from_latex_name('Downarrow')])
        self.data['arrows']['symbols'].append(['mapsto', CharacterDB.get_unicode_from_latex_name('mapsto')])
        self.data['arrows']['symbols'].append(['longmapsto', CharacterDB.get_unicode_from_latex_name('longmapsto')])
        self.data['arrows']['symbols'].append(['leftharpoondown', CharacterDB.get_unicode_from_latex_name('leftharpoondown')])
        self.data['arrows']['symbols'].append(['rightharpoondown', CharacterDB.get_unicode_from_latex_name('rightharpoondown')])
        self.data['arrows']['symbols'].append(['leftharpoonup', CharacterDB.get_unicode_from_latex_name('leftharpoonup')])
        self.data['arrows']['symbols'].append(['rightharpoonup', CharacterDB.get_unicode_from_latex_name('rightharpoonup')])
        self.data['arrows']['symbols'].append(['rightleftharpoons', CharacterDB.get_unicode_from_latex_name('rightleftharpoons')])
        self.data['arrows']['symbols'].append(['leftrightharpoons', CharacterDB.get_unicode_from_latex_name('leftrightharpoons')])
        self.data['arrows']['symbols'].append(['downharpoonleft', CharacterDB.get_unicode_from_latex_name('downharpoonleft')])
        self.data['arrows']['symbols'].append(['upharpoonleft', CharacterDB.get_unicode_from_latex_name('upharpoonleft')])
        self.data['arrows']['symbols'].append(['downharpoonright', CharacterDB.get_unicode_from_latex_name('downharpoonright')])
        self.data['arrows']['symbols'].append(['upharpoonright', CharacterDB.get_unicode_from_latex_name('upharpoonright')])
        self.data['arrows']['symbols'].append(['nwarrow', CharacterDB.get_unicode_from_latex_name('nwarrow')])
        self.data['arrows']['symbols'].append(['searrow', CharacterDB.get_unicode_from_latex_name('searrow')])
        self.data['arrows']['symbols'].append(['nearrow', CharacterDB.get_unicode_from_latex_name('nearrow')])
        self.data['arrows']['symbols'].append(['swarrow', CharacterDB.get_unicode_from_latex_name('swarrow')])
        self.data['arrows']['symbols'].append(['hookleftarrow', CharacterDB.get_unicode_from_latex_name('hookleftarrow')])
        self.data['arrows']['symbols'].append(['hookrightarrow', CharacterDB.get_unicode_from_latex_name('hookrightarrow')])
        self.data['arrows']['symbols'].append(['curvearrowleft', CharacterDB.get_unicode_from_latex_name('curvearrowleft')])
        self.data['arrows']['symbols'].append(['curvearrowright', CharacterDB.get_unicode_from_latex_name('curvearrowright')])
        self.data['arrows']['symbols'].append(['Lsh', CharacterDB.get_unicode_from_latex_name('Lsh')])
        self.data['arrows']['symbols'].append(['Rsh', CharacterDB.get_unicode_from_latex_name('Rsh')])
        self.data['arrows']['symbols'].append(['looparrowleft', CharacterDB.get_unicode_from_latex_name('looparrowleft')])
        self.data['arrows']['symbols'].append(['looparrowright', CharacterDB.get_unicode_from_latex_name('looparrowright')])
        self.data['arrows']['symbols'].append(['leftrightsquigarrow', CharacterDB.get_unicode_from_latex_name('leftrightsquigarrow')])
        self.data['arrows']['symbols'].append(['rightsquigarrow', CharacterDB.get_unicode_from_latex_name('rightsquigarrow')])

        self.data['delimiters'] = {'title': 'Delimiters', 'symbols': []}
        self.data['delimiters']['symbols'].append(['lparen', CharacterDB.get_unicode_from_latex_name('lparen')])
        self.data['delimiters']['symbols'].append(['rparen', CharacterDB.get_unicode_from_latex_name('rparen')])
        self.data['delimiters']['symbols'].append(['lbrack', CharacterDB.get_unicode_from_latex_name('lbrack')])
        self.data['delimiters']['symbols'].append(['rbrack', CharacterDB.get_unicode_from_latex_name('rbrack')])
        self.data['delimiters']['symbols'].append(['lbrace', CharacterDB.get_unicode_from_latex_name('lbrace')])
        self.data['delimiters']['symbols'].append(['rbrace', CharacterDB.get_unicode_from_latex_name('rbrace')])
        self.data['delimiters']['symbols'].append(['lfloor', CharacterDB.get_unicode_from_latex_name('lfloor')])
        self.data['delimiters']['symbols'].append(['rfloor', CharacterDB.get_unicode_from_latex_name('rfloor')])
        self.data['delimiters']['symbols'].append(['lceil', CharacterDB.get_unicode_from_latex_name('lceil')])
        self.data['delimiters']['symbols'].append(['rceil', CharacterDB.get_unicode_from_latex_name('rceil')])
        self.data['delimiters']['symbols'].append(['langle', CharacterDB.get_unicode_from_latex_name('langle')])
        self.data['delimiters']['symbols'].append(['rangle', CharacterDB.get_unicode_from_latex_name('rangle')])
        self.data['delimiters']['symbols'].append(['vert', CharacterDB.get_unicode_from_latex_name('vert')])
        self.data['delimiters']['symbols'].append(['Vert', CharacterDB.get_unicode_from_latex_name('Vert')])

        self.data['calligraphic_capitals'] = {'title': 'Calligraphic Capitals', 'symbols': []}
        self.data['calligraphic_capitals']['symbols'].append(['mathcalA', CharacterDB.get_unicode_from_latex_name('mathcalA')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalB', CharacterDB.get_unicode_from_latex_name('mathcalB')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalC', CharacterDB.get_unicode_from_latex_name('mathcalC')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalD', CharacterDB.get_unicode_from_latex_name('mathcalD')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalE', CharacterDB.get_unicode_from_latex_name('mathcalE')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalF', CharacterDB.get_unicode_from_latex_name('mathcalF')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalG', CharacterDB.get_unicode_from_latex_name('mathcalG')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalH', CharacterDB.get_unicode_from_latex_name('mathcalH')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalI', CharacterDB.get_unicode_from_latex_name('mathcalI')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalJ', CharacterDB.get_unicode_from_latex_name('mathcalJ')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalK', CharacterDB.get_unicode_from_latex_name('mathcalK')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalL', CharacterDB.get_unicode_from_latex_name('mathcalL')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalM', CharacterDB.get_unicode_from_latex_name('mathcalM')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalN', CharacterDB.get_unicode_from_latex_name('mathcalN')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalO', CharacterDB.get_unicode_from_latex_name('mathcalO')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalP', CharacterDB.get_unicode_from_latex_name('mathcalP')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalQ', CharacterDB.get_unicode_from_latex_name('mathcalQ')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalR', CharacterDB.get_unicode_from_latex_name('mathcalR')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalS', CharacterDB.get_unicode_from_latex_name('mathcalS')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalT', CharacterDB.get_unicode_from_latex_name('mathcalT')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalU', CharacterDB.get_unicode_from_latex_name('mathcalU')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalV', CharacterDB.get_unicode_from_latex_name('mathcalV')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalW', CharacterDB.get_unicode_from_latex_name('mathcalW')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalX', CharacterDB.get_unicode_from_latex_name('mathcalX')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalY', CharacterDB.get_unicode_from_latex_name('mathcalY')])
        self.data['calligraphic_capitals']['symbols'].append(['mathcalZ', CharacterDB.get_unicode_from_latex_name('mathcalZ')])

        self.is_active = True
        self.buttons = list()

        self.populate()

        MessageBus.subscribe(self, 'mode_set')
        MessageBus.subscribe(self, 'app_state_changed')
        MessageBus.subscribe(self, 'sidebar_visibility_changed')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'mode_set' in messages or 'app_state_changed' in messages or 'sidebar_visibility_changed' in messages:
            self.update()

    @timer.timer
    def update(self):
        document_active = WorkspaceRepo.get_workspace().get_active_document() != None

        if Settings.get_value('show_tools_sidebar') and Settings.get_value('tools_sidebar_active_tab') == 'math':
            if document_active != self.is_active:
                self.is_active = document_active

                for button in self.buttons:
                    button.set_sensitive(self.is_active)

    @timer.timer
    def populate(self):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.add_css_class('tools-sidebar')

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(box)
        self.view.add_named(scrolled_window, 'math')

        is_first = True
        for name, section in self.data.items():
            headline = Gtk.Label.new(section['title'])
            headline.set_xalign(Gtk.Align.FILL)
            headline.add_css_class('header')

            if is_first:
                headline.add_css_class('first')
                is_first = False
            box.append(headline)

            wrapbox = self.create_wrapbox(section['symbols'])
            box.append(wrapbox)

    def create_wrapbox(self, symbols):
        wrapbox = Adw.WrapBox()
        wrapbox.set_line_spacing(0)

        res_path = Paths.get_resources_folder()
        for data in symbols:
            pic = Icon(os.path.join(res_path, 'icons_sidebar', 'sidebar-' + data[0] + '-symbolic.svg'))
            button = Gtk.Button()
            button.set_child(pic)
            button.set_can_focus(False)
            button.add_css_class('flat')
            button.connect('clicked', self.on_button_clicked, data[1])
            self.buttons.append(button)
            wrapbox.append(button)

        return wrapbox

    def on_button_clicked(self, button, xml):
        self.application.document_view.view.content.grab_focus()

        UseCases.insert_xml(xml)
        UseCases.scroll_insert_on_screen(animation_type='default')


class Icon(Gtk.DrawingArea):

    def __init__(self, path):
        Gtk.DrawingArea.__init__(self)

        self.rsvg_handle = Rsvg.Handle.new_from_file(path)
        self.size = self.rsvg_handle.get_intrinsic_size_in_pixels()

        self.set_size_request(self.size[1], self.size[2])
        self.set_draw_func(self.draw)

    def draw(self, widget, ctx, width, height):
        toolbar_fg = ColorManager.get_ui_color_string('toolbar_fg')
        self.rsvg_handle.set_stylesheet(b'path, rect, text {fill: ' + toolbar_fg.encode() + b'; stroke: ' + toolbar_fg.encode() + b';}')
        self.rsvg_handle.render_cairo(ctx)


