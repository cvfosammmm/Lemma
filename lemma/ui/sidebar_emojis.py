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

from lemma.services.message_bus import MessageBus
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.services.files import Files
from lemma.use_cases.use_cases import UseCases
from lemma.services.settings import Settings
import lemma.services.timer as timer


class SidebarEmojis(object):

    def __init__(self, main_window, application):
        self.view = main_window.tools_sidebar
        self.application = application

        self.emoji_data = dict()
        self.emoji_data['emojis_and_people'] = {'title': 'Emojis & People', 'symbols': ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '🫠', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '🥲', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🫢', '🫣', '🤫', '🤔', '🫡', '🤐', '🤨', '😑', '😶', '🫥', '😏', '😒', '🙄', '😬', '🤥', '🫨', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '🥸', '😎', '🤓', '🧐', '😕', '🫤', '😟', '🙁', '😮', '😯', '😲', '😳', '🥺', '🥹', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '💩', '🤡', '👹', '👺', '👻', '👾', '🤖', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾', '🙈', '🙉', '🙊', '💌', '💘', '💝', '💖', '💗', '💓', '💞', '💕', '💟', '💔', '🩷', '🧡', '💛', '💚', '💙', '🩵', '💜', '🤎', '🖤', '🩶', '🤍', '💋', '💯', '💢', '💥', '💫', '💦', '💨', '💬', '💭', '💤', '👋', '🤚', '🖖', '🫱', '🫲', '🫳', '🫴', '🫷', '🫸', '👌', '🤌', '🤏', '🤞', '🫰', '🤟', '🤘', '🤙', '🖕', '🫵', '👊', '🤛', '🤜', '👏', '🙌', '🫶', '👐', '🤲', '🤝', '🙏', '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👅', '👄', '🫦', '👶', '🧒', '👦', '👧', '🧑', '👱', '👨', '🧔', '👩', '🧓', '👴', '👵', '🙍', '🙎', '🙅', '🙆', '💁', '🙋', '🧏', '🙇', '🤦', '🤷', '👮', '💂', '🥷', '👷', '🫅', '🤴', '👸', '👳', '👲', '🧕', '🤵', '👰', '🤰', '🫃', '🫄', '🤱', '👼', '🎅', '🤶', '🦸', '🦹', '🧙', '🧚', '🧛', '🧜', '🧝', '🧞', '🧟', '🧌', '💆', '💇', '💏', '💑', '👤', '👥', '🫂', '👣']}
        self.emoji_data['nature'] = {'title': 'Nature', 'symbols': ['🐵', '🐒', '🦍', '🦧', '🐶', '🦮', '🐩', '🐺', '🦊', '🦝', '🐱', '🦁', '🐯', '🐅', '🐆', '🐴', '🫎', '🫏', '🐎', '🦄', '🦓', '🦌', '🦬', '🐮', '🐂', '🐃', '🐄', '🐷', '🐖', '🐗', '🐽', '🐏', '🐑', '🐐', '🐪', '🐫', '🦙', '🦒', '🐘', '🦣', '🦏', '🦛', '🐭', '🐁', '🐀', '🐹', '🐰', '🐇', '🦫', '🦔', '🦇', '🐻', '🐨', '🐼', '🦥', '🦦', '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤', '🐥', '🐧', '🦅', '🦆', '🦢', '🦉', '🦤', '🪶', '🦩', '🦚', '🦜', '🪽', '🪿', '🐸', '🐊', '🐢', '🦎', '🐍', '🐲', '🐉', '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐠', '🐡', '🦈', '🐙', '🐚', '🪸', '🪼', '🦀', '🦞', '🦐', '🦑', '🦪', '🐌', '🦋', '🐛', '🐜', '🐝', '🪲', '🐞', '🦗', '🪳', '🦂', '🦟', '🪰', '🪱', '🦠', '💐', '🌸', '💮', '🪷', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷', '🪻', '🌱', '🪴', '🌲', '🌳', '🌴', '🌵', '🌾', '🌿', '🍀', '🍁', '🍂', '🍃', '🪹', '🪺', '🍄']}
        self.emoji_data['food_and_drink'] = {'title': 'Food & Drink', 'symbols': ['🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🥭', '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🫐', '🥝', '🍅', '🫒', '🥥', '🥑', '🍆', '🥔', '🥕', '🌽', '🫑', '🥒', '🥬', '🥦', '🧄', '🧅', '🥜', '🫘', '🌰', '🫚', '🫛', '🍞', '🥐', '🥖', '🫓', '🥨', '🥯', '🥞', '🧇', '🧀', '🍖', '🍗', '🥩', '🥓', '🍔', '🍟', '🍕', '🌭', '🥪', '🌮', '🌯', '🫔', '🥙', '🧆', '🥚', '🍳', '🥘', '🍲', '🫕', '🥣', '🥗', '🍿', '🧈', '🧂', '🥫', '🍱', '🍘', '🍙', '🍚', '🍛', '🍜', '🍝', '🍠', '🍢', '🍣', '🍤', '🍥', '🥮', '🍡', '🥟', '🥠', '🥡', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰', '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍼', '🥛', '🫖', '🍵', '🍶', '🍾', '🍷', '🍹', '🍺', '🍻', '🥂', '🥃', '🫗', '🥤', '🧋', '🧃', '🧉', '🧊', '🥢', '🍴', '🥄', '🔪', '🫙', '🏺']}
        self.emoji_data['activity'] = {'title': 'Activity', 'symbols': ['🥎', '🏀', '🏐', '🏈', '🏉', '🎾', '🥏', '🎳', '🏏', '🏑', '🏒', '🥍', '🏓', '🏸', '🥊', '🥋', '🥅', '🎣', '🤿', '🎽', '🎿', '🛷', '🥌', '🎯', '🪀', '🪁', '🔫', '🎱', '🔮', '🪄', '🎰', '🎲', '🧩', '🧸', '🪅', '🪩', '🪆', '🃏', '🎴', '🎨', '🧵', '🪡', '🧶', '🎤', '🎷', '🪗', '🎸', '🎹', '🎺', '🎻', '🪕', '🥁', '🪘', '🪇', '🪈', '🚶', '🧍', '🧎', '🏃', '💃', '🕺', '👯', '🧖', '🧗', '🤺', '🏇', '🚣', '🚴', '🚵', '🤸', '🤼', '🤽', '🤾', '🤹', '🧘', '🛀', '🛌', '👭', '👫', '👬']}
        self.emoji_data['travel_and_places'] = {'title': 'Travel & Places', 'symbols': ['🚂', '🚃', '🚄', '🚅', '🚆', '🚈', '🚉', '🚊', '🚝', '🚞', '🚋', '🚌', '🚎', '🚐', '🚒', '🚓', '🚕', '🚖', '🚗', '🚙', '🛻', '🚚', '🚛', '🚜', '🛵', '🦽', '🦼', '🛺', '🛴', '🛹', '🛼', '🚏', '🛞', '🚨', '🚥', '🚦', '🛑', '🚧', '🛟', '🛶', '🚤', '🚢', '🛫', '🛬', '🪂', '💺', '🚁', '🚟', '🚠', '🚡', '🚀', '🛸', '🧳', '🛖', '🏡', '🏢', '🏣', '🏤', '🏥', '🏦', '🏨', '🏩', '🏪', '🏫', '🏬', '🏯', '🏰', '💒', '🗼', '🗽', '🕌', '🛕', '🕍', '🕋', '🌁', '🌃', '🌄', '🌅', '🌆', '🌇', '🌉', '🎠', '🛝', '🎡', '🎢', '💈', '🎪']}
        self.emoji_data['objects'] = {'title': 'Objects', 'symbols': ['🌐', '🗾', '🧭', '🌋', '🗻', '🧱', '🪨', '🪵', '🌂', '🎃', '🎄', '🎆', '🎇', '🧨', '🎈', '🎉', '🎊', '🎋', '🎍', '🎎', '🎏', '🎐', '🎑', '🧧', '🎀', '🎁', '🎫', '🏅', '🥇', '🥈', '🥉', '🪢', '🥽', '🥼', '🦺', '👔', '👕', '👖', '🧣', '🧤', '🧥', '🧦', '👗', '👘', '🥻', '🩱', '🩲', '🩳', '👙', '👚', '🪭', '👛', '👜', '👝', '🎒', '🩴', '👞', '👟', '🥾', '🥿', '👠', '👡', '🩰', '👢', '🪮', '👑', '👒', '🎩', '🧢', '🪖', '📿', '💄', '💍', '💎', '🔇', '🔉', '🔊', '📢', '📣', '📯', '🔔', '🔕', '📱', '📲', '📞', '📠', '🔋', '🪫', '🔌', '💽', '💾', '📀', '🧮', '🎥', '📸', '📼', '🔎', '💡', '🔦', '🏮', '🪔', '📔', '📕', '📖', '📗', '📘', '📙', '📓', '📒', '📃', '📜', '📄', '📰', '📑', '🔖', '🪙', '💴', '💵', '💶', '💷', '💸', '🧾', '💹', '📧', '📨', '📩', '📮', '📝', '💼', '📁', '📂', '📅', '📆', '📇', '📈', '📉', '📊', '📌', '📍', '📎', '📏', '📐', '🔏', '🔐', '🔑', '🔨', '🪓', '🪃', '🏹', '🪚', '🔧', '🪛', '🔩', '🦯', '🔗', '🪝', '🧰', '🧲', '🪜', '🧪', '🧫', '🧬', '🔬', '🔭', '📡', '💉', '🩸', '💊', '🩹', '🩼', '🩺', '🩻', '🚪', '🛗', '🪞', '🪟', '🪑', '🚽', '🪠', '🚿', '🛁', '🪤', '🪒', '🧴', '🧷', '🧹', '🧺', '🧻', '🪣', '🧼', '🫧', '🪥', '🧽', '🧯', '🛒', '🚬', '🪦', '🧿', '🪬', '🗿', '🪧', '🪪']}
        self.emoji_data['symbols_and_flags'] = {'title': 'Symbols & Flags', 'symbols': ['🌑', '🌒', '🌓', '🌔', '🌖', '🌗', '🌘', '🌙', '🌚', '🌛', '🌝', '🌞', '🪐', '🌟', '🌠', '🌌', '🌀', '🌈', '🔥', '💧', '🌊', '🏧', '🚮', '🚰', '🚻', '🚾', '🛂', '🛃', '🛄', '🛅', '🚸', '🚫', '🚳', '🚯', '🚱', '🚷', '📵', '🔞', '🔃', '🔄', '🔙', '🔚', '🔛', '🔜', '🔝', '🛐', '🕎', '🔯', '🪯', '🔀', '🔁', '🔂', '🔼', '🔽', '🎦', '🔅', '🔆', '📶', '🛜', '📳', '📴', '🟰', '💱', '💲', '🔱', '📛', '🔰', '🔟', '🔠', '🔡', '🔢', '🔣', '🔤', '🆎', '🆑', '🆒', '🆓', '🆔', '🆕', '🆖', '🆗', '🆘', '🆙', '🆚', '🈁', '🈶', '🉐', '🈹', '🈲', '🉑', '🈸', '🈴', '🈳', '🈺', '🈵', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '🟫', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '💠', '🔘', '🔳', '🔲', '🏁', '🚩', '🎌', '🏴', '🎼', '🎵', '🎶']}

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

        if Settings.get_value('show_tools_sidebar') and Settings.get_value('tools_sidebar_active_tab') == 'emojis':
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
        self.view.add_named(scrolled_window, 'emojis')

        is_first = True
        for name, section in self.emoji_data.items():
            headline = Gtk.Label.new(section['title'])
            headline.set_xalign(Gtk.Align.FILL)
            headline.add_css_class('header')

            if is_first:
                headline.add_css_class('first')
                is_first = False
            box.append(headline)

            wrapbox = self.create_wrapbox_for_emojis(section['symbols'])
            box.append(wrapbox)

    def create_wrapbox_for_emojis(self, symbols):
        wrapbox = Adw.WrapBox()
        wrapbox.set_line_spacing(0)
        wrapbox.add_css_class('emoji')

        res_path = Files.get_resources_folder()
        for symbol in symbols:
            filename = 'emoji_u' + hex(ord(symbol))[2:] + '.png'
            pic = Gtk.Image.new_from_file(os.path.join(res_path, 'fonts/Noto_Color_Emoji/png', filename))
            pic.set_valign(Gtk.Align.CENTER)
            pic.set_halign(Gtk.Align.CENTER)
            pic.set_pixel_size(22)
            button = Gtk.Button()
            button.set_child(pic)
            button.set_can_focus(False)
            button.add_css_class('flat')
            button.connect('clicked', self.on_button_clicked, symbol)
            self.buttons.append(button)
            wrapbox.append(button)

        return wrapbox

    def on_button_clicked(self, button, xml):
        self.application.document_view.view.content.grab_focus()

        UseCases.insert_xml(xml)


