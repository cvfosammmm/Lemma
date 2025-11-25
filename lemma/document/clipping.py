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

import time, os.path

from lemma.services.layout_info import LayoutInfo
from lemma.application_state.application_state import ApplicationState


class Clipping(object):

    def __init__(self, document):
        self.document = document

        self.prev_x, self.prev_y = 0, 0
        self.target_x, self.target_y = 0, 0

        self.last_scroll_scheduled = time.time()
        self.last_scroll_animation_type = None

        # these factors correspond to a spring animation with damping factor of 1, mass of 0.2 and stiffness of 350.
        # values are measured every 16 milliseconds.
        self.animation_factors_default = [0.14521632886418778, 0.38680949651114804, 0.5961508878602289, 0.7471932740676479, 0.8469876969721808, 0.9095846909702064, 0.9475247122520112, 0.9699664865615893, 0.9830014314472356, 0.9904664008194531, 0.9946935799717825, 0.9970653570501354, 0.9983859489194434, 0.9991164990228094, 0.9995184028082745, 1]

        self.animation_factors_decelerate = [0.0, 0.06199636747598371, 0.12014927262467011, 0.17469699073964112, 0.2258630252471631, 0.27385702348751123, 0.31887563572246785, 0.36110332088868463, 0.40071310239839775, 0.4378672770843073, 0.4727180801934477, 0.5054083091547894, 0.5360719086763932, 0.5648345195694895, 0.591813993548231, 0.6171208761144554, 0.6408588595060257, 0.6631252075646573, 0.6840111542640804, 0.7036022775314649, 0.7219788498938017, 0.7392161673859745, 0.7553848580681896, 0.7705511714168795, 0.7847772497748297, 0.7981213829727649, 0.8106382471656801, 0.8223791288625243, 0.8333921350671701, 0.8437223903917062, 0.8534122219496949, 0.8625013327869832, 0.871026964560675, 0.8790240501328287, 0.8865253567041134, 0.8935616200739007, 0.9001616705769069, 0.9063525512123981, 0.91215962844998, 0.917606696165988, 0.9227160731363435, 0.9275086944853453, 0.9320041974650973, 0.9362210019170423, 0.9401763857452885, 0.9438865557109685, 0.947366713837705, 0.9506311197002733, 0.9536931488516794, 0.9565653476280548, 0.9592594845559228, 0.9617865985724751, 0.9641570442564326, 0.9663805342548213, 0.9684661790795032, 0.9704225244365203, 0.9722575862412101, 0.9739788834625586, 0.9755934689313691, 0.9771079582384816, 0.9785285568414455, 0.979861085490717, 0.9811110040795602, 0.9822834340153744, 0.9833831792041116, 0.9844147457337654, 0.9853823603375849, 0.9862899877126596, 0.9871413467648417, 0.9879399258465626, 0.988688997049985, 0.9893916296140478, 0.9900507025003449, 0.9906689161893605, 0.9912488037453996, 0.9917927411955463, 0.9923029572651805, 0.9927815425099413, 0.9932304578815544, 0.9936515427626212, 0.9940465225032924, 0.994417015490705, 0.9947645397801501, 0.9950905193151411, 0.9953962897618709, 0.9956831039819594, 0.9959521371659206, 0.9962044916483798, 0.9964412014247709, 0.9966632363880219, 0.9968715063025881, 0.9970668645321131, 0.9972501115359957, 0.9974219981491864, 0.9975832286586527, 0.9977344636891193, 0.9978763229099085, 0.9980093875739666, 0.9981342028994872, 0.9982512803038837, 0.9983610994992674, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    def set_target(self, x, y, animation_type=None):
        self.prev_x = self.target_x
        self.prev_y = self.target_y

        self.target_x = x
        self.target_y = y

        self.last_scroll_scheduled = time.time()
        self.last_scroll_animation_type = animation_type

    def get_target_offsets(self):
        return (self.target_x, self.target_y)

    def get_current_offsets(self):
        time_since_last_scroll = time.time() - self.last_scroll_scheduled

        if self.last_scroll_animation_type == 'default' and time_since_last_scroll < 0.2:
            proximity = self.animation_factors_default[int(time_since_last_scroll * 64)]
            x = self.prev_x + proximity * (self.target_x - self.prev_x)
            y = self.prev_y + proximity * (self.target_y - self.prev_y)

        elif self.last_scroll_animation_type == 'decelerate' and time_since_last_scroll < 1.8:
            proximity = self.animation_factors_decelerate[int(time_since_last_scroll * 64)]
            x = self.prev_x + proximity * (self.target_x - self.prev_x)
            y = self.prev_y + proximity * (self.target_y - self.prev_y)

        else:
            x = self.target_x
            y = self.target_y

        max_y = max(0, LayoutInfo.get_normal_document_offset() + ApplicationState.get_value('title_buttons_height') + self.document.get_height() + LayoutInfo.get_document_padding_bottom() - ApplicationState.get_value('document_view_height'))
        max_x = max(0, LayoutInfo.get_document_padding_left() + self.document.get_width() - ApplicationState.get_value('document_view_width'))

        x = min(max_x, max(0, x))
        y = min(max_y, max(0, y))

        return (x, y)

    def get_state(self):
        return self.target_x, self.target_y, self.prev_x, self.prev_y, self.last_scroll_scheduled, self.last_scroll_animation_type

    def set_state(self, state):
        self.target_x, self.target_y, self.prev_x, self.prev_y, self.last_scroll_scheduled, self.last_scroll_animation_type = state


