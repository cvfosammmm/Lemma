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
from lemma.services.files import Files
from lemma.services.character_db import CharacterDB
from lemma.use_cases.use_cases import UseCases
from lemma.services.settings import Settings
import lemma.services.timer as timer


class SidebarSymbols(object):

    def __init__(self, main_window, application):
        self.main_window = main_window

        self.data = dict()
        self.data['punctuation'] = {'title': 'Punctuation', 'symbols': []}
        self.data['punctuation']['symbols'].append(['textendash', CharacterDB.get_unicode_from_latex_name('textendash')])
        self.data['punctuation']['symbols'].append(['textemdash', CharacterDB.get_unicode_from_latex_name('textemdash')])
        self.data['punctuation']['symbols'].append(['guillemetleft', CharacterDB.get_unicode_from_latex_name('guillemetleft')])
        self.data['punctuation']['symbols'].append(['guillemetright', CharacterDB.get_unicode_from_latex_name('guillemetright')])
        self.data['punctuation']['symbols'].append(['textquotedblleft', CharacterDB.get_unicode_from_latex_name('textquotedblleft')])
        self.data['punctuation']['symbols'].append(['textquotedblright', CharacterDB.get_unicode_from_latex_name('textquotedblright')])
        self.data['punctuation']['symbols'].append(['quotedblbase', CharacterDB.get_unicode_from_latex_name('quotedblbase')])
        self.data['punctuation']['symbols'].append(['textquoteleft', '‘'])
        self.data['punctuation']['symbols'].append(['textquoteright', '’'])
        self.data['punctuation']['symbols'].append(['lparen', CharacterDB.get_unicode_from_latex_name('lparen')])
        self.data['punctuation']['symbols'].append(['rparen', CharacterDB.get_unicode_from_latex_name('rparen')])
        self.data['punctuation']['symbols'].append(['lbrack', CharacterDB.get_unicode_from_latex_name('lbrack')])
        self.data['punctuation']['symbols'].append(['rbrack', CharacterDB.get_unicode_from_latex_name('rbrack')])
        self.data['punctuation']['symbols'].append(['textlbrackdbl', '⟦'])
        self.data['punctuation']['symbols'].append(['textrbrackdbl', '⟧'])
        self.data['punctuation']['symbols'].append(['textlquill', '⁅'])
        self.data['punctuation']['symbols'].append(['textrquill', '⁆'])
        self.data['punctuation']['symbols'].append(['lbrace', CharacterDB.get_unicode_from_latex_name('lbrace')])
        self.data['punctuation']['symbols'].append(['rbrace', CharacterDB.get_unicode_from_latex_name('rbrace')])
        self.data['punctuation']['symbols'].append(['vert', CharacterDB.get_unicode_from_latex_name('vert')])
        self.data['punctuation']['symbols'].append(['Vert', CharacterDB.get_unicode_from_latex_name('Vert')])
        self.data['punctuation']['symbols'].append(['cdot', CharacterDB.get_unicode_from_latex_name('cdot')])
        self.data['punctuation']['symbols'].append(['colon', CharacterDB.get_unicode_from_latex_name('colon')])
        self.data['punctuation']['symbols'].append(['cdots', '…'])
        self.data['punctuation']['symbols'].append(['textquestiondown', '¿'])
        self.data['punctuation']['symbols'].append(['textexclamdown', '¡'])
        self.data['punctuation']['symbols'].append(['textinterrobang', '‽'])
        self.data['punctuation']['symbols'].append(['textinterrobangdown', '⸘'])

        self.data['arrows'] = {'title': 'Arrows', 'symbols': []}
        self.data['arrows']['symbols'].append(['leftarrow', CharacterDB.get_unicode_from_latex_name('leftarrow')])
        self.data['arrows']['symbols'].append(['rightarrow', CharacterDB.get_unicode_from_latex_name('rightarrow')])
        self.data['arrows']['symbols'].append(['downarrow', CharacterDB.get_unicode_from_latex_name('downarrow')])
        self.data['arrows']['symbols'].append(['uparrow', CharacterDB.get_unicode_from_latex_name('uparrow')])
        self.data['arrows']['symbols'].append(['searrow', CharacterDB.get_unicode_from_latex_name('searrow')])
        self.data['arrows']['symbols'].append(['nearrow', CharacterDB.get_unicode_from_latex_name('nearrow')])

        self.data['arrows'] = {'title': 'Currency and Legal', 'symbols': []}
        self.data['arrows']['symbols'].append(['textdollar', '$'])
        self.data['arrows']['symbols'].append(['textcent', '¢'])
        self.data['arrows']['symbols'].append(['textbaht', '฿'])
        self.data['arrows']['symbols'].append(['textguarani', '₲'])
        self.data['arrows']['symbols'].append(['textwon', '₩'])
        self.data['arrows']['symbols'].append(['textyen', '¥'])
        self.data['arrows']['symbols'].append(['textdong', '₫'])
        self.data['arrows']['symbols'].append(['textnaira', '₦'])
        self.data['arrows']['symbols'].append(['textpeso', '₤'])
        self.data['arrows']['symbols'].append(['textsterling', '£'])
        self.data['arrows']['symbols'].append(['texteuro', '€'])
        self.data['arrows']['symbols'].append(['textcopyright', '©'])
        self.data['arrows']['symbols'].append(['texttrademark', '™'])
        self.data['arrows']['symbols'].append(['textservicemark', '℠'])

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
        self.data['misc_symbols']['symbols'].append(['backslash', CharacterDB.get_unicode_from_latex_name('backslash')])
        self.data['misc_symbols']['symbols'].append(['sphericalangle', CharacterDB.get_unicode_from_latex_name('sphericalangle')])
        self.data['misc_symbols']['symbols'].append(['eth', CharacterDB.get_unicode_from_latex_name('eth')])
        self.data['misc_symbols']['symbols'].append(['mho', CharacterDB.get_unicode_from_latex_name('mho')])
        self.data['misc_symbols']['symbols'].append(['pm', CharacterDB.get_unicode_from_latex_name('pm')])
        self.data['misc_symbols']['symbols'].append(['times', CharacterDB.get_unicode_from_latex_name('times')])
        self.data['misc_symbols']['symbols'].append(['ast', CharacterDB.get_unicode_from_latex_name('ast')])
        self.data['misc_symbols']['symbols'].append(['star', CharacterDB.get_unicode_from_latex_name('star')])
        self.data['misc_symbols']['symbols'].append(['circ', CharacterDB.get_unicode_from_latex_name('circ')])
        self.data['misc_symbols']['symbols'].append(['bullet', CharacterDB.get_unicode_from_latex_name('bullet')])
        self.data['misc_symbols']['symbols'].append(['div', CharacterDB.get_unicode_from_latex_name('div')])
        self.data['misc_symbols']['symbols'].append(['textdiscount', '⁒'])
        self.data['misc_symbols']['symbols'].append(['textreferencemark', '※'])
        self.data['misc_symbols']['symbols'].append(['textless', '<'])
        self.data['misc_symbols']['symbols'].append(['textgreater', '>'])
        self.data['misc_symbols']['symbols'].append(['%', '%'])
        self.data['misc_symbols']['symbols'].append(['textperthousand', '‰'])
        self.data['misc_symbols']['symbols'].append(['textpertenthousand', '‱'])
        self.data['misc_symbols']['symbols'].append(['S', '§'])
        self.data['misc_symbols']['symbols'].append(['textpilcrow', '¶'])
        self.data['misc_symbols']['symbols'].append(['textestimated', '℮'])
        self.data['misc_symbols']['symbols'].append(['textbrokenbar', '¦'])
        self.data['misc_symbols']['symbols'].append(['textfractionsolidus', '⁄'])
        self.data['misc_symbols']['symbols'].append(['textcelsius', '℃'])
        self.data['misc_symbols']['symbols'].append(['textdegree', '°'])
        self.data['misc_symbols']['symbols'].append(['textmho', '℧'])
        self.data['misc_symbols']['symbols'].append(['textohm', 'Ω'])
        self.data['misc_symbols']['symbols'].append(['textvisiblespace', '␣'])
        self.data['misc_symbols']['symbols'].append(['textrecipe', '℞'])
        self.data['misc_symbols']['symbols'].append(['textmusicalnote', '♪'])
        self.data['misc_symbols']['symbols'].append(['textordmasculine', 'º'])
        self.data['misc_symbols']['symbols'].append(['textordfeminine', 'ª'])
        self.data['misc_symbols']['symbols'].append(['textdivorced', '⚮'])
        self.data['misc_symbols']['symbols'].append(['textmarried', '⚭'])
        self.data['misc_symbols']['symbols'].append(['textdied', '✝'])
        self.data['misc_symbols']['symbols'].append(['dagger', CharacterDB.get_unicode_from_latex_name('dagger')])
        self.data['misc_symbols']['symbols'].append(['ddagger', CharacterDB.get_unicode_from_latex_name('ddagger')])

        self.is_active = True
        self.buttons = list()

        self.populate()

        MessageBus.subscribe(self, 'mode_set')
        MessageBus.subscribe(self, 'sidebar_visibility_changed')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'mode_set' in messages or 'sidebar_visibility_changed' in messages:
            self.update()

    @timer.timer
    def update(self):
        document_active = WorkspaceRepo.get_workspace().get_active_document() != None

        if Settings.get_value('show_tools_sidebar') and Settings.get_value('tools_sidebar_active_tab') == 'symbols':
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
        self.main_window.tools_sidebar.add_named(scrolled_window, 'symbols')

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

        res_path = Files.get_resources_folder()
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
        self.main_window.document_view.content.grab_focus()
        UseCases.insert_xml(xml, is_math=False)
        UseCases.update_implicit_x_position()


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


