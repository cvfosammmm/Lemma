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
from gi.repository import Gtk
from gi.repository import Adw

import os.path

from lemma.services.paths import Paths
from lemma.ui.popovers.popover_manager import PopoverManager
from lemma.services.character_db import CharacterDB
import lemma.services.timer as timer


class ToolsSidebar(Gtk.Stack):

    def __init__(self):
        Gtk.Stack.__init__(self)
        self.set_size_request(266, 280)

        self.resources_folder = Paths.get_resources_folder()

        self.populate_symbols()
        self.populate_emojis()

    @timer.timer
    def populate_emojis(self):
        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.add_css_class('tools-sidebar')

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.box)
        self.add_named(scrolled_window, 'emojis')

        headline = self.create_headline('Emojis & People')
        headline.add_css_class('first')
        self.box.append(headline)

        symbols = ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '🫠', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '🥲', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🫢', '🫣', '🤫', '🤔', '🫡', '🤐', '🤨', '😑', '😶', '🫥', '😏', '😒', '🙄', '😬', '🤥', '🫨', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '🥸', '😎', '🤓', '🧐', '😕', '🫤', '😟', '🙁', '😮', '😯', '😲', '😳', '🥺', '🥹', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '💩', '🤡', '👹', '👺', '👻', '👾', '🤖', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾', '🙈', '🙉', '🙊', '💌', '💘', '💝', '💖', '💗', '💓', '💞', '💕', '💟', '💔', '🩷', '🧡', '💛', '💚', '💙', '🩵', '💜', '🤎', '🖤', '🩶', '🤍', '💋', '💯', '💢', '💥', '💫', '💦', '💨', '💬', '💭', '💤', '👋', '🤚', '🖖', '🫱', '🫲', '🫳', '🫴', '🫷', '🫸', '👌', '🤌', '🤏', '🤞', '🫰', '🤟', '🤘', '🤙', '🖕', '🫵', '👊', '🤛', '🤜', '👏', '🙌', '🫶', '👐', '🤲', '🤝', '🙏', '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👅', '👄', '🫦', '👶', '🧒', '👦', '👧', '🧑', '👱', '👨', '🧔', '👩', '🧓', '👴', '👵', '🙍', '🙎', '🙅', '🙆', '💁', '🙋', '🧏', '🙇', '🤦', '🤷', '👮', '💂', '🥷', '👷', '🫅', '🤴', '👸', '👳', '👲', '🧕', '🤵', '👰', '🤰', '🫃', '🫄', '🤱', '👼', '🎅', '🤶', '🦸', '🦹', '🧙', '🧚', '🧛', '🧜', '🧝', '🧞', '🧟', '🧌', '💆', '💇', '💏', '💑', '👤', '👥', '🫂', '👣']
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Nature')
        self.box.append(headline)

        symbols = ['🐵', '🐒', '🦍', '🦧', '🐶', '🦮', '🐩', '🐺', '🦊', '🦝', '🐱', '🦁', '🐯', '🐅', '🐆', '🐴', '🫎', '🫏', '🐎', '🦄', '🦓', '🦌', '🦬', '🐮', '🐂', '🐃', '🐄', '🐷', '🐖', '🐗', '🐽', '🐏', '🐑', '🐐', '🐪', '🐫', '🦙', '🦒', '🐘', '🦣', '🦏', '🦛', '🐭', '🐁', '🐀', '🐹', '🐰', '🐇', '🦫', '🦔', '🦇', '🐻', '🐨', '🐼', '🦥', '🦦', '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤', '🐥', '🐧', '🦅', '🦆', '🦢', '🦉', '🦤', '🪶', '🦩', '🦚', '🦜', '🪽', '🪿', '🐸', '🐊', '🐢', '🦎', '🐍', '🐲', '🐉', '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐠', '🐡', '🦈', '🐙', '🐚', '🪸', '🪼', '🦀', '🦞', '🦐', '🦑', '🦪', '🐌', '🦋', '🐛', '🐜', '🐝', '🪲', '🐞', '🦗', '🪳', '🦂', '🦟', '🪰', '🪱', '🦠', '💐', '🌸', '💮', '🪷', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷', '🪻', '🌱', '🪴', '🌲', '🌳', '🌴', '🌵', '🌾', '🌿', '🍀', '🍁', '🍂', '🍃', '🪹', '🪺', '🍄']
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Food & Drink')
        self.box.append(headline)

        symbols = ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🥭', '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🫐', '🥝', '🍅', '🫒', '🥥', '🥑', '🍆', '🥔', '🥕', '🌽', '🫑', '🥒', '🥬', '🥦', '🧄', '🧅', '🥜', '🫘', '🌰', '🫚', '🫛', '🍞', '🥐', '🥖', '🫓', '🥨', '🥯', '🥞', '🧇', '🧀', '🍖', '🍗', '🥩', '🥓', '🍔', '🍟', '🍕', '🌭', '🥪', '🌮', '🌯', '🫔', '🥙', '🧆', '🥚', '🍳', '🥘', '🍲', '🫕', '🥣', '🥗', '🍿', '🧈', '🧂', '🥫', '🍱', '🍘', '🍙', '🍚', '🍛', '🍜', '🍝', '🍠', '🍢', '🍣', '🍤', '🍥', '🥮', '🍡', '🥟', '🥠', '🥡', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰', '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍼', '🥛', '🫖', '🍵', '🍶', '🍾', '🍷', '🍹', '🍺', '🍻', '🥂', '🥃', '🫗', '🥤', '🧋', '🧃', '🧉', '🧊', '🥢', '🍴', '🥄', '🔪', '🫙', '🏺']
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Activity')
        self.box.append(headline)

        symbols = ['🥎', '🏀', '🏐', '🏈', '🏉', '🎾', '🥏', '🎳', '🏏', '🏑', '🏒', '🥍', '🏓', '🏸', '🥊', '🥋', '🥅', '🎣', '🤿', '🎽', '🎿', '🛷', '🥌', '🎯', '🪀', '🪁', '🔫', '🎱', '🔮', '🪄', '🎰', '🎲', '🧩', '🧸', '🪅', '🪩', '🪆', '🃏', '🎴', '🎨', '🧵', '🪡', '🧶', '🎤', '🎷', '🪗', '🎸', '🎹', '🎺', '🎻', '🪕', '🥁', '🪘', '🪇', '🪈', '🚶', '🧍', '🧎', '🏃', '💃', '🕺', '👯', '🧖', '🧗', '🤺', '🏇', '🚣', '🚴', '🚵', '🤸', '🤼', '🤽', '🤾', '🤹', '🧘', '🛀', '🛌', '👭', '👫', '👬' ]
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Travel & Places')
        self.box.append(headline)

        symbols = ['🚂', '🚃', '🚄', '🚅', '🚆', '🚈', '🚉', '🚊', '🚝', '🚞', '🚋', '🚌', '🚎', '🚐', '🚒', '🚓', '🚕', '🚖', '🚗', '🚙', '🛻', '🚚', '🚛', '🚜', '🛵', '🦽', '🦼', '🛺', '🛴', '🛹', '🛼', '🚏', '🛞', '🚨', '🚥', '🚦', '🛑', '🚧', '🛟', '🛶', '🚤', '🚢', '🛫', '🛬', '🪂', '💺', '🚁', '🚟', '🚠', '🚡', '🚀', '🛸', '🧳', '🛖', '🏡', '🏢', '🏣', '🏤', '🏥', '🏦', '🏨', '🏩', '🏪', '🏫', '🏬', '🏯', '🏰', '💒', '🗼', '🗽', '🕌', '🛕', '🕍', '🕋', '🌁', '🌃', '🌄', '🌅', '🌆', '🌇', '🌉', '🎠', '🛝', '🎡', '🎢', '💈', '🎪', ]
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Objects')
        self.box.append(headline)

        symbols = ['🌐', '🗾', '🧭', '🌋', '🗻', '🧱', '🪨', '🪵', '🌂', '🎃', '🎄', '🎆', '🎇', '🧨', '🎈', '🎉', '🎊', '🎋', '🎍', '🎎', '🎏', '🎐', '🎑', '🧧', '🎀', '🎁', '🎫', '🏅', '🥇', '🥈', '🥉', '🪢', '🥽', '🥼', '🦺', '👔', '👕', '👖', '🧣', '🧤', '🧥', '🧦', '👗', '👘', '🥻', '🩱', '🩲', '🩳', '👙', '👚', '🪭', '👛', '👜', '👝', '🎒', '🩴', '👞', '👟', '🥾', '🥿', '👠', '👡', '🩰', '👢', '🪮', '👑', '👒', '🎩', '🧢', '🪖', '📿', '💄', '💍', '💎', '🔇', '🔉', '🔊', '📢', '📣', '📯', '🔔', '🔕', '📱', '📲', '📞', '📠', '🔋', '🪫', '🔌', '💽', '💾', '📀', '🧮', '🎥', '📸', '📼', '🔎', '💡', '🔦', '🏮', '🪔', '📔', '📕', '📖', '📗', '📘', '📙', '📓', '📒', '📃', '📜', '📄', '📰', '📑', '🔖', '🪙', '💴', '💵', '💶', '💷', '💸', '🧾', '💹', '📧', '📨', '📩', '📮', '📝', '💼', '📁', '📂', '📅', '📆', '📇', '📈', '📉', '📊', '📌', '📍', '📎', '📏', '📐', '🔏', '🔐', '🔑', '🔨', '🪓', '🪃', '🏹', '🪚', '🔧', '🪛', '🔩', '🦯', '🔗', '🪝', '🧰', '🧲', '🪜', '🧪', '🧫', '🧬', '🔬', '🔭', '📡', '💉', '🩸', '💊', '🩹', '🩼', '🩺', '🩻', '🚪', '🛗', '🪞', '🪟', '🪑', '🚽', '🪠', '🚿', '🛁', '🪤', '🪒', '🧴', '🧷', '🧹', '🧺', '🧻', '🪣', '🧼', '🫧', '🪥', '🧽', '🧯', '🛒', '🚬', '🪦', '🧿', '🪬', '🗿', '🪧', '🪪', ]
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Symbols & Flags')
        self.box.append(headline)

        symbols = ['🌑', '🌒', '🌓', '🌔', '🌖', '🌗', '🌘', '🌙', '🌚', '🌛', '🌝', '🌞', '🪐', '🌟', '🌠', '🌌', '🌀', '🌈', '🔥', '💧', '🌊', '🏧', '🚮', '🚰', '🚻', '🚾', '🛂', '🛃', '🛄', '🛅', '🚸', '🚫', '🚳', '🚯', '🚱', '🚷', '📵', '🔞', '🔃', '🔄', '🔙', '🔚', '🔛', '🔜', '🔝', '🛐', '🕎', '🔯', '🪯', '🔀', '🔁', '🔂', '🔼', '🔽', '🎦', '🔅', '🔆', '📶', '🛜', '📳', '📴', '🟰', '💱', '💲', '🔱', '📛', '🔰', '🔟', '🔠', '🔡', '🔢', '🔣', '🔤', '🆎', '🆑', '🆒', '🆓', '🆔', '🆕', '🆖', '🆗', '🆘', '🆙', '🆚', '🈁', '🈶', '🉐', '🈹', '🈲', '🉑', '🈸', '🈴', '🈳', '🈺', '🈵', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '🟫', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '💠', '🔘', '🔳', '🔲', '🏁', '🚩', '🎌', '🏴', '🎼', '🎵', '🎶']
        wrapbox = self.create_wrapbox_for_emojis(symbols)
        self.box.append(wrapbox)

    def populate_symbols(self):
        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.add_css_class('tools-sidebar')

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.box)
        self.add_named(scrolled_window, 'math')

        headline = self.create_headline('Math Typesetting')
        headline.add_css_class('first')
        self.box.append(headline)

        symbols = []
        symbols.append(['subscript', 'win.insert-xml(\'<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist></mathlist></mathscript>\')'])
        symbols.append(['superscript', 'win.insert-xml(\'<placeholder marks="prev_selection"/><mathscript><mathlist></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>\')'])
        symbols.append(['subsuperscript', 'win.insert-xml(\'<placeholder marks="prev_selection"/><mathscript><mathlist><placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript>\')'])
        symbols.append(['fraction', 'win.insert-xml(\'<mathfraction><mathlist><placeholder marks="prev_selection"/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathfraction>\')'])
        symbols.append(['sqrt', 'win.insert-xml(\'<mathroot><mathlist><placeholder marks="prev_selection"/><end/></mathlist><mathlist></mathlist></mathroot>\')'])
        symbols.append(['nthroot', 'win.insert-xml(\'<mathroot><mathlist><placeholder marks="prev_selection"/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathroot>\')'])
        wrapbox = self.create_wrapbox_for_pictures(symbols)
        self.box.append(wrapbox)

        symbols = []
        symbols.append(['sumwithindex', 'win.insert-xml(\'∑<mathscript><mathlist><placeholder/>=<placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/>\')'])
        symbols.append(['prodwithindex', 'win.insert-xml(\'∏<mathscript><mathlist><placeholder/>=<placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/>\')'])
        symbols.append(['indefint', 'win.insert-xml(\'∫ <placeholder marks="prev_selection"/> 𝑑<placeholder/>\')'])
        symbols.append(['defint', 'win.insert-xml(\'∫<mathscript><mathlist><placeholder/><end/></mathlist><mathlist><placeholder/><end/></mathlist></mathscript> <placeholder marks="prev_selection"/> 𝑑<placeholder/>\')'])
        symbols.append(['limitwithindex', 'win.insert-xml(\'lim<mathscript><mathlist><placeholder/> → <placeholder/><end/></mathlist><mathlist></mathlist></mathscript> <placeholder marks="prev_selection"/>\')'])
        wrapbox = self.create_wrapbox_for_pictures(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Punctuation')
        self.box.append(headline)

        symbols = []
        for name in ['textendash', 'textemdash', 'guillemetleft', 'guillemetright', 'quotedblbase', 'textquotedblleft', 'textquotedblright', 'cdotp', 'colon', 'vdots', 'cdots']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Greek Letters')
        self.box.append(headline)

        symbols = []
        for name in ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Misc. Symbols')
        self.box.append(headline)

        symbols = []
        for name in ['neg', 'infty', 'prime', 'backslash', 'emptyset', 'forall', 'exists', 'nexists', 'complement', 'bot', 'top', 'partial', 'nabla', 'mathbbN', 'mathbbZ', 'mathbbQ', 'mathbbI', 'mathbbR', 'mathbbC', 'Im', 'Re', 'aleph', 'wp', 'hbar', 'imath', 'jmath', 'ell', 'sharp', 'flat', 'natural', 'angle', 'sphericalangle', 'measuredangle', 'clubsuit', 'diamondsuit', 'heartsuit', 'spadesuit', 'eth', 'mho']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Operators')
        self.box.append(headline)

        symbols = []
        for name in ['pm', 'mp', 'setminus', 'cdot', 'times', 'ast', 'star', 'divideontimes', 'circ', 'bullet', 'div', 'cap', 'cup', 'uplus', 'sqcap', 'sqcup', 'triangleleft', 'triangleright', 'wr', 'bigtriangleup', 'bigtriangledown', 'vee', 'wedge', 'oplus', 'ominus', 'otimes', 'oslash', 'odot', 'circledcirc', 'circleddash', 'circledast', 'dotplus', 'leftthreetimes', 'rightthreetimes', 'ltimes', 'rtimes', 'dagger', 'ddagger', 'intercal', 'amalg']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Big Operators')
        self.box.append(headline)

        symbols = []
        for name in ['sum', 'prod', 'coprod', 'int', 'iint', 'iiint', 'bigcap', 'bigcup', 'bigodot', 'bigoplus', 'bigotimes', 'bigwedge', 'bigvee']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Relations')
        self.box.append(headline)

        symbols = []
        for name in ['leq', 'geq', 'lneq', 'gneq', 'nleq', 'ngeq', 'nless', 'ngtr', 'll', 'gg', 'neq', 'equiv', 'approx', 'sim', 'simeq', 'cong', 'ncong', 'asymp', 'prec', 'succ', 'nprec', 'nsucc', 'preceq', 'succeq', 'subset', 'supset', 'subseteq', 'supseteq', 'subsetneq', 'supsetneq', 'nsubseteq', 'nsupseteq', 'sqsubset', 'sqsupset', 'sqsubseteq', 'sqsupseteq', 'bowtie', 'in', 'notin', 'propto', 'vdash', 'dashv', 'models', 'smile', 'frown', 'between', 'perp', 'mid', 'nmid', 'parallel', 'nparallel', 'vartriangleleft', 'vartriangleright', 'ntriangleleft', 'ntriangleright', 'trianglelefteq', 'trianglerighteq', 'ntrianglelefteq', 'ntrianglerighteq', 'multimap', 'pitchfork', 'therefore', 'because']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Arrows')
        self.box.append(headline)

        symbols = []
        for name in ['leftarrow', 'leftrightarrow', 'rightarrow', 'longleftarrow', 'longleftrightarrow', 'longrightarrow', 'downarrow', 'updownarrow', 'uparrow', 'Leftarrow', 'Leftrightarrow', 'Rightarrow', 'Longleftarrow', 'Longleftrightarrow', 'Longrightarrow', 'Updownarrow', 'Uparrow', 'Downarrow', 'mapsto', 'longmapsto', 'leftharpoondown', 'rightharpoondown', 'leftharpoonup', 'rightharpoonup', 'rightleftharpoons', 'leftrightharpoons', 'downharpoonleft', 'upharpoonleft', 'downharpoonright', 'upharpoonright', 'nwarrow', 'searrow', 'nearrow', 'swarrow', 'hookleftarrow', 'hookrightarrow', 'curvearrowleft', 'curvearrowright', 'Lsh', 'Rsh', 'looparrowleft', 'looparrowright', 'leftrightsquigarrow', 'rightsquigarrow']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Delimiters')
        self.box.append(headline)

        symbols = []
        for name in ['lparen', 'rparen', 'lbrack', 'rbrack', 'lbrace', 'rbrace', 'lfloor', 'rfloor', 'lceil', 'rceil', 'langle', 'rangle', 'vert', 'Vert']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        self.box.append(wrapbox)

        headline = self.create_headline('Calligraphic Capitals')
        self.box.append(headline)

        symbols = []
        for name in ['mathcalA', 'mathcalB', 'mathcalC', 'mathcalD', 'mathcalE', 'mathcalF', 'mathcalG', 'mathcalH', 'mathcalI', 'mathcalJ', 'mathcalK', 'mathcalL', 'mathcalM', 'mathcalN', 'mathcalO', 'mathcalP', 'mathcalQ', 'mathcalR', 'mathcalS', 'mathcalT', 'mathcalU', 'mathcalV', 'mathcalW', 'mathcalX', 'mathcalY', 'mathcalZ']:
            symbols.append([name, 'win.insert-xml::' + CharacterDB.get_unicode_from_latex_name(name)])
        wrapbox = self.create_wrapbox(symbols)
        wrapbox.add_css_class('mathcal')
        self.box.append(wrapbox)

    def create_headline(self, name):
        header = Gtk.Label.new(name)
        header.set_xalign(Gtk.Align.FILL)
        header.add_css_class('header')

        return header

    def create_wrapbox(self, symbols):
        wrapbox = Adw.WrapBox()
        wrapbox.set_line_spacing(0)

        for data in symbols:
            image = Gtk.Image.new_from_icon_name('sidebar-' + data[0] + '-symbolic')
            image.set_valign(Gtk.Align.CENTER)
            image.set_halign(Gtk.Align.CENTER)
            button = Gtk.Button()
            button.set_child(image)
            button.set_detailed_action_name(data[1])
            button.set_can_focus(False)
            button.add_css_class('flat')
            wrapbox.append(button)

        return wrapbox

    def create_wrapbox_for_pictures(self, symbols):
        wrapbox = Adw.WrapBox()
        wrapbox.set_line_spacing(0)

        for data in symbols:
            pic = Gtk.Picture.new_for_filename(os.path.join(self.resources_folder, 'icons_extra', 'sidebar-' + data[0] + '-symbolic.svg'))
            pic.set_valign(Gtk.Align.CENTER)
            pic.set_halign(Gtk.Align.CENTER)
            button = Gtk.Button()
            button.set_child(pic)
            button.set_detailed_action_name(data[1])
            button.set_can_focus(False)
            button.add_css_class('flat')
            wrapbox.append(button)

        return wrapbox

    def create_wrapbox_for_emojis(self, symbols):
        wrapbox = Adw.WrapBox()
        wrapbox.set_line_spacing(0)
        wrapbox.add_css_class('emoji')

        res_path = Paths.get_resources_folder()
        for symbol in symbols:
            filename = 'emoji_u' + hex(ord(symbol))[2:] + '.png'
            pic = Gtk.Image.new_from_file(os.path.join(res_path, 'fonts/Noto_Color_Emoji/png', filename))
            pic.set_valign(Gtk.Align.CENTER)
            pic.set_halign(Gtk.Align.CENTER)
            pic.set_pixel_size(22)
            button = Gtk.Button()
            button.set_child(pic)
            button.set_detailed_action_name('win.insert-xml::' + symbol)
            button.set_can_focus(False)
            button.add_css_class('flat')
            wrapbox.append(button)

        return wrapbox


