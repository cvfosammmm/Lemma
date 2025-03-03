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

import os.path

from lemma.infrastructure.service_locator import ServiceLocator
from lemma.ui.popovers.popover_manager import PopoverManager
from lemma.db.character_db import CharacterDB


class ToolsSidebar(Gtk.Stack):

    def __init__(self):
        Gtk.Stack.__init__(self)
        self.set_size_request(262, 280)

        self.resources_path = ServiceLocator.get_resources_path()

        self.populate_symbols()
        self.populate_emojis()

    def populate_emojis(self):
        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.add_css_class('tools-sidebar')

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.box)
        self.add_named(scrolled_window, 'emojis')

        self.add_headline('Emojis & People', 'first')
        symbols = ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '🫠', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '🥲', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🫢', '🫣', '🤫', '🤔', '🫡', '🤐', '🤨', '😑', '😶', '🫥', '😏', '😒', '🙄', '😬', '🤥', '🫨', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '🥸', '😎', '🤓', '🧐', '😕', '🫤', '😟', '🙁', '😮', '😯', '😲', '😳', '🥺', '🥹', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '💩', '🤡', '👹', '👺', '👻', '👾', '🤖', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾', '🙈', '🙉', '🙊', '💌', '💘', '💝', '💖', '💗', '💓', '💞', '💕', '💟', '💔', '🩷', '🧡', '💛', '💚', '💙', '🩵', '💜', '🤎', '🖤', '🩶', '🤍', '💋', '💯', '💢', '💥', '💫', '💦', '💨', '💬', '💭', '💤', '👋', '🤚', '🖖', '🫱', '🫲', '🫳', '🫴', '🫷', '🫸', '👌', '🤌', '🤏', '🤞', '🫰', '🤟', '🤘', '🤙', '🖕', '🫵', '👊', '🤛', '🤜', '👏', '🙌', '🫶', '👐', '🤲', '🤝', '🙏', '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👅', '👄', '🫦', '👶', '🧒', '👦', '👧', '🧑', '👱', '👨', '🧔', '👩', '🧓', '👴', '👵', '🙍', '🙎', '🙅', '🙆', '💁', '🙋', '🧏', '🙇', '🤦', '🤷', '👮', '💂', '🥷', '👷', '🫅', '🤴', '👸', '👳', '👲', '🧕', '🤵', '👰', '🤰', '🫃', '🫄', '🤱', '👼', '🎅', '🤶', '🦸', '🦹', '🧙', '🧚', '🧛', '🧜', '🧝', '🧞', '🧟', '🧌', '💆', '💇', '💏', '💑', '👤', '👥', '🫂', '👣']
        self.add_flowbox_for_emojis(symbols)

        self.add_headline('Nature')
        symbols = ['🐵', '🐒', '🦍', '🦧', '🐶', '🦮', '🐩', '🐺', '🦊', '🦝', '🐱', '🦁', '🐯', '🐅', '🐆', '🐴', '🫎', '🫏', '🐎', '🦄', '🦓', '🦌', '🦬', '🐮', '🐂', '🐃', '🐄', '🐷', '🐖', '🐗', '🐽', '🐏', '🐑', '🐐', '🐪', '🐫', '🦙', '🦒', '🐘', '🦣', '🦏', '🦛', '🐭', '🐁', '🐀', '🐹', '🐰', '🐇', '🦫', '🦔', '🦇', '🐻', '🐨', '🐼', '🦥', '🦦', '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤', '🐥', '🐧', '🦅', '🦆', '🦢', '🦉', '🦤', '🪶', '🦩', '🦚', '🦜', '🪽', '🪿', '🐸', '🐊', '🐢', '🦎', '🐍', '🐲', '🐉', '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐠', '🐡', '🦈', '🐙', '🐚', '🪸', '🪼', '🦀', '🦞', '🦐', '🦑', '🦪', '🐌', '🦋', '🐛', '🐜', '🐝', '🪲', '🐞', '🦗', '🪳', '🦂', '🦟', '🪰', '🪱', '🦠', '💐', '🌸', '💮', '🪷', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷', '🪻', '🌱', '🪴', '🌲', '🌳', '🌴', '🌵', '🌾', '🌿', '🍀', '🍁', '🍂', '🍃', '🪹', '🪺', '🍄']
        self.add_flowbox_for_emojis(symbols)

        self.add_headline('Food & Drink')
        symbols = ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🥭', '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🫐', '🥝', '🍅', '🫒', '🥥', '🥑', '🍆', '🥔', '🥕', '🌽', '🫑', '🥒', '🥬', '🥦', '🧄', '🧅', '🥜', '🫘', '🌰', '🫚', '🫛', '🍞', '🥐', '🥖', '🫓', '🥨', '🥯', '🥞', '🧇', '🧀', '🍖', '🍗', '🥩', '🥓', '🍔', '🍟', '🍕', '🌭', '🥪', '🌮', '🌯', '🫔', '🥙', '🧆', '🥚', '🍳', '🥘', '🍲', '🫕', '🥣', '🥗', '🍿', '🧈', '🧂', '🥫', '🍱', '🍘', '🍙', '🍚', '🍛', '🍜', '🍝', '🍠', '🍢', '🍣', '🍤', '🍥', '🥮', '🍡', '🥟', '🥠', '🥡', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰', '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍼', '🥛', '🫖', '🍵', '🍶', '🍾', '🍷', '🍹', '🍺', '🍻', '🥂', '🥃', '🫗', '🥤', '🧋', '🧃', '🧉', '🧊', '🥢', '🍴', '🥄', '🔪', '🫙', '🏺']
        self.add_flowbox_for_emojis(symbols)

        self.add_headline('Activity')
        symbols = ['🥎', '🏀', '🏐', '🏈', '🏉', '🎾', '🥏', '🎳', '🏏', '🏑', '🏒', '🥍', '🏓', '🏸', '🥊', '🥋', '🥅', '🎣', '🤿', '🎽', '🎿', '🛷', '🥌', '🎯', '🪀', '🪁', '🔫', '🎱', '🔮', '🪄', '🎰', '🎲', '🧩', '🧸', '🪅', '🪩', '🪆', '🃏', '🎴', '🎨', '🧵', '🪡', '🧶', '🎤', '🎷', '🪗', '🎸', '🎹', '🎺', '🎻', '🪕', '🥁', '🪘', '🪇', '🪈', '🚶', '🧍', '🧎', '🏃', '💃', '🕺', '👯', '🧖', '🧗', '🤺', '🏇', '🚣', '🚴', '🚵', '🤸', '🤼', '🤽', '🤾', '🤹', '🧘', '🛀', '🛌', '👭', '👫', '👬' ]
        self.add_flowbox_for_emojis(symbols)

        self.add_headline('Travel & Places')
        symbols = ['🚂', '🚃', '🚄', '🚅', '🚆', '🚈', '🚉', '🚊', '🚝', '🚞', '🚋', '🚌', '🚎', '🚐', '🚒', '🚓', '🚕', '🚖', '🚗', '🚙', '🛻', '🚚', '🚛', '🚜', '🛵', '🦽', '🦼', '🛺', '🛴', '🛹', '🛼', '🚏', '🛞', '🚨', '🚥', '🚦', '🛑', '🚧', '🛟', '🛶', '🚤', '🚢', '🛫', '🛬', '🪂', '💺', '🚁', '🚟', '🚠', '🚡', '🚀', '🛸', '🧳', '🛖', '🏡', '🏢', '🏣', '🏤', '🏥', '🏦', '🏨', '🏩', '🏪', '🏫', '🏬', '🏯', '🏰', '💒', '🗼', '🗽', '🕌', '🛕', '🕍', '🕋', '🌁', '🌃', '🌄', '🌅', '🌆', '🌇', '🌉', '🎠', '🛝', '🎡', '🎢', '💈', '🎪', ]
        self.add_flowbox_for_emojis(symbols)

        self.add_headline('Objects')
        symbols = ['🌐', '🗾', '🧭', '🌋', '🗻', '🧱', '🪨', '🪵', '🌂', '🎃', '🎄', '🎆', '🎇', '🧨', '🎈', '🎉', '🎊', '🎋', '🎍', '🎎', '🎏', '🎐', '🎑', '🧧', '🎀', '🎁', '🎫', '🏅', '🥇', '🥈', '🥉', '🪢', '🥽', '🥼', '🦺', '👔', '👕', '👖', '🧣', '🧤', '🧥', '🧦', '👗', '👘', '🥻', '🩱', '🩲', '🩳', '👙', '👚', '🪭', '👛', '👜', '👝', '🎒', '🩴', '👞', '👟', '🥾', '🥿', '👠', '👡', '🩰', '👢', '🪮', '👑', '👒', '🎩', '🧢', '🪖', '📿', '💄', '💍', '💎', '🔇', '🔉', '🔊', '📢', '📣', '📯', '🔔', '🔕', '📱', '📲', '📞', '📠', '🔋', '🪫', '🔌', '💽', '💾', '📀', '🧮', '🎥', '📸', '📼', '🔎', '💡', '🔦', '🏮', '🪔', '📔', '📕', '📖', '📗', '📘', '📙', '📓', '📒', '📃', '📜', '📄', '📰', '📑', '🔖', '🪙', '💴', '💵', '💶', '💷', '💸', '🧾', '💹', '📧', '📨', '📩', '📮', '📝', '💼', '📁', '📂', '📅', '📆', '📇', '📈', '📉', '📊', '📌', '📍', '📎', '📏', '📐', '🔏', '🔐', '🔑', '🔨', '🪓', '🪃', '🏹', '🪚', '🔧', '🪛', '🔩', '🦯', '🔗', '🪝', '🧰', '🧲', '🪜', '🧪', '🧫', '🧬', '🔬', '🔭', '📡', '💉', '🩸', '💊', '🩹', '🩼', '🩺', '🩻', '🚪', '🛗', '🪞', '🪟', '🪑', '🚽', '🪠', '🚿', '🛁', '🪤', '🪒', '🧴', '🧷', '🧹', '🧺', '🧻', '🪣', '🧼', '🫧', '🪥', '🧽', '🧯', '🛒', '🚬', '🪦', '🧿', '🪬', '🗿', '🪧', '🪪', ]
        self.add_flowbox_for_emojis(symbols)

        self.add_headline('Symbols & Flags')
        symbols = ['🌑', '🌒', '🌓', '🌔', '🌖', '🌗', '🌘', '🌙', '🌚', '🌛', '🌝', '🌞', '🪐', '🌟', '🌠', '🌌', '🌀', '🌈', '🔥', '💧', '🌊', '🏧', '🚮', '🚰', '🚻', '🚾', '🛂', '🛃', '🛄', '🛅', '🚸', '🚫', '🚳', '🚯', '🚱', '🚷', '📵', '🔞', '🔃', '🔄', '🔙', '🔚', '🔛', '🔜', '🔝', '🛐', '🕎', '🔯', '🪯', '🔀', '🔁', '🔂', '🔼', '🔽', '🎦', '🔅', '🔆', '📶', '🛜', '📳', '📴', '🟰', '💱', '💲', '🔱', '📛', '🔰', '🔟', '🔠', '🔡', '🔢', '🔣', '🔤', '🆎', '🆑', '🆒', '🆓', '🆔', '🆕', '🆖', '🆗', '🆘', '🆙', '🆚', '🈁', '🈶', '🉐', '🈹', '🈲', '🉑', '🈸', '🈴', '🈳', '🈺', '🈵', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '🟫', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '💠', '🔘', '🔳', '🔲', '🏁', '🚩', '🎌', '🏴', '🎼', '🎵', '🎶']
        self.add_flowbox_for_emojis(symbols)

    def populate_symbols(self):
        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.add_css_class('tools-sidebar')

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.box)
        self.add_named(scrolled_window, 'math')

        self.add_headline('Math Typesetting', 'first')

        symbols = []
        symbols.append(['subscript', 'win.insert-xml(\'<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder marks="new_selection_bound"/><end marks="new_insert"/></mathlist><mathlist></mathlist></mathscript>\')'])
        symbols.append(['superscript', 'win.insert-xml(\'<placeholder marks="prev_selection"/><mathscript><mathlist></mathlist><mathlist><placeholder marks="new_selection_bound"/><end marks="new_insert"/></mathlist></mathscript>\')'])
        symbols.append(['subsuperscript', 'win.insert-xml(\'<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder marks="new_selection_bound"/><end marks="new_insert"/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>\')'])
        symbols.append(['fraction', 'win.insert-xml(\'<mathfraction><mathlist><placeholder marks="prev_selection new_selection_bound"/><end marks="new_insert"/></mathlist><mathlist><placeholder/><end/></mathlist></mathfraction>\')'])
        symbols.append(['sqrt', 'win.insert-xml(\'<mathroot><mathlist><placeholder marks="new_selection_bound prev_selection"/><end marks="new_insert"/></mathlist><mathlist></mathlist></mathroot>\')'])
        symbols.append(['nthroot', 'win.insert-xml(\'<mathroot><mathlist><placeholder marks="new_selection_bound prev_selection"/><end marks="new_insert"/></mathlist><mathlist><placeholder/><end/></mathlist></mathroot>\')'])
        self.add_flowbox(symbols)

        symbols = []
        symbols.append(['sumwithindex', 'win.insert-xml(\'∑<mathscript><mathlist><placeholder/>=<placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/>\')'])
        symbols.append(['prodwithindex', 'win.insert-xml(\'∏<mathscript><mathlist><placeholder/>=<placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/>\')'])
        symbols.append(['indefint', 'win.insert-xml(\'∫ <placeholder marks="prev_selection"/> 𝑑<placeholder/>\')'])
        symbols.append(['defint', 'win.insert-xml(\'∫<mathscript><mathlist><placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/> 𝑑<placeholder/>\')'])
        symbols.append(['limitwithindex', 'win.insert-xml(\'lim<mathscript><mathlist><placeholder/> → <placeholder/><end/></mathlist><mathlist></mathlist></mathscript> <placeholder marks="prev_selection"/>\')'])
        self.add_flowbox_for_pictures(symbols)

        self.add_headline('Punctuation')

        symbols = []
        for name in ['textendash', 'textemdash', 'guillemetleft', 'guillemetright', 'quotedblbase', 'textquotedblleft', 'textquotedblright', 'cdotp', 'colon', 'vdots', 'cdots']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Greek Letters')

        symbols = []
        for name in ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Misc. Symbols')

        symbols = []
        for name in ['neg', 'infty', 'prime', 'backslash', 'emptyset', 'forall', 'exists', 'nexists', 'complement', 'bot', 'top', 'partial', 'nabla', 'mathbbN', 'mathbbZ', 'mathbbQ', 'mathbbI', 'mathbbR', 'mathbbC', 'Im', 'Re', 'aleph', 'wp', 'hbar', 'imath', 'jmath', 'ell', 'sharp', 'flat', 'natural', 'angle', 'sphericalangle', 'measuredangle', 'clubsuit', 'diamondsuit', 'heartsuit', 'spadesuit', 'eth', 'mho']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Operators')

        symbols = []
        for name in ['pm', 'mp', 'setminus', 'cdot', 'times', 'ast', 'star', 'divideontimes', 'circ', 'bullet', 'div', 'cap', 'cup', 'uplus', 'sqcap', 'sqcup', 'triangleleft', 'triangleright', 'wr', 'bigtriangleup', 'bigtriangledown', 'vee', 'wedge', 'oplus', 'ominus', 'otimes', 'oslash', 'odot', 'circledcirc', 'circleddash', 'circledast', 'dotplus', 'leftthreetimes', 'rightthreetimes', 'ltimes', 'rtimes', 'dagger', 'ddagger', 'intercal', 'amalg']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Big Operators')

        symbols = []
        for name in ['sum', 'prod', 'coprod', 'int', 'iint', 'iiint', 'bigcap', 'bigcup', 'bigodot', 'bigoplus', 'bigotimes', 'bigwedge', 'bigvee']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Relations')

        symbols = []
        for name in ['leq', 'geq', 'lneq', 'gneq', 'nleq', 'ngeq', 'nless', 'ngtr', 'll', 'gg', 'neq', 'equiv', 'approx', 'sim', 'simeq', 'cong', 'ncong', 'asymp', 'prec', 'succ', 'nprec', 'nsucc', 'preceq', 'succeq', 'subset', 'supset', 'subseteq', 'supseteq', 'subsetneq', 'supsetneq', 'nsubseteq', 'nsupseteq', 'sqsubset', 'sqsupset', 'sqsubseteq', 'sqsupseteq', 'bowtie', 'in', 'notin', 'propto', 'vdash', 'dashv', 'models', 'smile', 'frown', 'between', 'perp', 'mid', 'nmid', 'parallel', 'nparallel', 'vartriangleleft', 'vartriangleright', 'ntriangleleft', 'ntriangleright', 'trianglelefteq', 'trianglerighteq', 'ntrianglelefteq', 'ntrianglerighteq', 'multimap', 'pitchfork', 'therefore', 'because']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Arrows')

        symbols = []
        for name in ['leftarrow', 'leftrightarrow', 'rightarrow', 'longleftarrow', 'longleftrightarrow', 'longrightarrow', 'downarrow', 'updownarrow', 'uparrow', 'Leftarrow', 'Leftrightarrow', 'Rightarrow', 'Longleftarrow', 'Longleftrightarrow', 'Longrightarrow', 'Updownarrow', 'Uparrow', 'Downarrow', 'mapsto', 'longmapsto', 'leftharpoondown', 'rightharpoondown', 'leftharpoonup', 'rightharpoonup', 'rightleftharpoons', 'leftrightharpoons', 'downharpoonleft', 'upharpoonleft', 'downharpoonright', 'upharpoonright', 'nwarrow', 'searrow', 'nearrow', 'swarrow', 'hookleftarrow', 'hookrightarrow', 'curvearrowleft', 'curvearrowright', 'Lsh', 'Rsh', 'looparrowleft', 'looparrowright', 'leftrightsquigarrow', 'rightsquigarrow']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Delimiters')

        symbols = []
        for name in ['lparen', 'rparen', 'lbrack', 'rbrack', 'lbrace', 'rbrace', 'lfloor', 'rfloor', 'lceil', 'rceil', 'langle', 'rangle', 'vert', 'Vert']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols)

        self.add_headline('Calligraphic Capitals')

        symbols = []
        for name in ['mathcalA', 'mathcalB', 'mathcalC', 'mathcalD', 'mathcalE', 'mathcalF', 'mathcalG', 'mathcalH', 'mathcalI', 'mathcalJ', 'mathcalK', 'mathcalL', 'mathcalM', 'mathcalN', 'mathcalO', 'mathcalP', 'mathcalQ', 'mathcalR', 'mathcalS', 'mathcalT', 'mathcalU', 'mathcalV', 'mathcalW', 'mathcalX', 'mathcalY', 'mathcalZ']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        self.add_flowbox(symbols, css_class='mathcal')

    def add_headline(self, name, css_class=None):
        header = Gtk.Label.new(name)
        header.set_xalign(Gtk.Align.FILL)
        header.add_css_class('header')
        if css_class:
            header.add_css_class(css_class)
        self.box.append(header)

    def add_flowbox(self, symbols, css_class=None):
        flowbox = Gtk.FlowBox()
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_can_focus(False)
        flowbox.set_max_children_per_line(20)
        if css_class:
            flowbox.add_css_class(css_class)
        for data in symbols:
            image = Gtk.Image.new_from_icon_name('sidebar-' + data[0] + '-symbolic')
            image.set_valign(Gtk.Align.CENTER)
            image.set_halign(Gtk.Align.CENTER)
            button = Gtk.Button()
            button.set_child(image)
            button.set_detailed_action_name(data[1])
            button.set_can_focus(False)
            button.add_css_class('flat')
            flowbox.append(button)
        self.box.append(flowbox)

    def add_flowbox_for_emojis(self, symbols, css_class=None):
        flowbox = Gtk.FlowBox()
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_can_focus(False)
        flowbox.set_max_children_per_line(20)
        if css_class:
            flowbox.add_css_class(css_class)

        res_path = ServiceLocator.get_resources_path()
        for symbol in symbols:
            filename = 'emoji_u' + hex(ord(symbol))[2:] + '.svg'
            pic = Gtk.Image.new_from_file(os.path.join(res_path, 'fonts/Noto_Color_Emoji/svg', filename))
            pic.set_valign(Gtk.Align.CENTER)
            pic.set_halign(Gtk.Align.CENTER)
            pic.set_pixel_size(22)
            button = Gtk.Button()
            button.set_child(pic)
            button.set_detailed_action_name('win.insert-xml::' + symbol)
            button.set_can_focus(False)
            button.add_css_class('flat')
            flowbox.append(button)
        self.box.append(flowbox)

    def add_flowbox_for_pictures(self, symbols, css_class=None):
        flowbox = Gtk.FlowBox()
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_can_focus(False)
        flowbox.set_max_children_per_line(20)
        if css_class:
            flowbox.add_css_class(css_class)
        for data in symbols:
            pic = Gtk.Picture.new_for_filename(os.path.join(self.resources_path, 'icons_extra', 'sidebar-' + data[0] + '-symbolic.svg'))
            pic.set_valign(Gtk.Align.CENTER)
            pic.set_halign(Gtk.Align.CENTER)
            button = Gtk.Button()
            button.set_child(pic)
            button.set_detailed_action_name(data[1])
            button.set_can_focus(False)
            button.add_css_class('flat')
            flowbox.append(button)
        self.box.append(flowbox)


