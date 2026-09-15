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
from gi.repository import Gtk, Gdk, Graphene

import math
import networkx as nx

from lemma.services.color_manager import ColorManager
from lemma.services.message_bus import MessageBus
from lemma.ui.shortcuts import Shortcuts
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class Overview(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.view = self.main_window.overview
        self.toolbar = self.main_window.toolbar.toolbar_overview

        self.do_update = True
        self.do_center = True

        self.current_node = None
        self.G = nx.Graph()
        self.positions = dict()
        self.graph_width = 0
        self.graph_height = 0
        self.titles_by_id = dict()
        self.ids_by_title = dict()
        self.scaling_factor = 100
        self.hover_node = None
        self.selected_node = None

        self.view.set_draw_func(self.draw)
        self.view.set_pointer_func(self.update_pointer)

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.view.content.add_controller(self.primary_click_controller)

        self.shortcut_controller = Shortcuts.new_controller()
        self.shortcut_controller.add_cb('close_dialog', self.close_overview)
        self.shortcut_controller.add_cb('zoom_in_overview', self.zoom_in)
        self.shortcut_controller.add_cb('zoom_out_overview', self.zoom_out)
        self.shortcut_controller.add_cb('zoom_reset_overview', self.zoom_reset)
        self.view.add_controller(self.shortcut_controller)

        self.toolbar.zoom_out_button.connect('clicked', self.zoom_out)
        self.toolbar.zoom_in_button.connect('clicked', self.zoom_in)
        self.toolbar.reset_zoom_button.connect('clicked', self.zoom_reset)

        MessageBus.subscribe(self, 'document_removed')
        MessageBus.subscribe(self, 'mode_set')

        if WorkspaceRepo.get_workspace().get_mode() == 'overview':
            self.view.grab_focus()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'document_removed' in messages or 'mode_set' in messages:
            self.do_update = True

        if self.do_update and WorkspaceRepo.get_workspace().get_mode() == 'overview':
            self.update_graph()
            self.update_scale()
            self.view.content.queue_draw()
            self.do_update = False

        if 'mode_set' in messages and WorkspaceRepo.get_workspace().get_mode() == 'overview':
            self.view.grab_focus()
            self.do_center = True

        if self.do_center and self.view.view_width > 0:
            scroll_x = self.positions[self.current_node][0] * self.scaling_factor * self.view.zoom - self.view.view_width / 2
            scroll_y = self.positions[self.current_node][1] * self.scaling_factor * self.view.zoom - self.view.view_height / 2
            self.view.scroll_to(scroll_x, scroll_y)
            self.do_center = False

    @timer.timer
    def update_graph(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document != None:
            self.current_node = document.id
            self.titles_by_id = {}
            self.ids_by_title = {}

            self.G = nx.Graph()
            for document_stub in DocumentRepo.list():
                self.G.add_node(document_stub['id'])
                self.titles_by_id[document_stub['id']] = document_stub['title']
                self.ids_by_title[document_stub['title']] = document_stub['id']

            for document_stub in DocumentRepo.list():
                for title in list(document_stub['links'] & set(self.ids_by_title)):
                    self.G.add_edge(document_stub['id'], self.ids_by_title[title])

            pos = nx.spring_layout(self.G, seed=42, scale=math.sqrt(len(self.G)))

            min_x, min_y, max_x, max_y = (0, 0, 0, 0)
            for v, vpos in pos.items():
                min_x = min(min_x, vpos[0])
                min_y = min(min_y, vpos[1])
                max_x = max(max_x, vpos[0])
                max_y = max(max_y, vpos[1])
            self.graph_width = abs(max_x - min_x) + 0.1 * math.sqrt(len(self.G))
            self.graph_height = abs(max_y - min_y) + 0.1 * math.sqrt(len(self.G))

            self.positions = dict()
            for v, vpos in pos.items():
                self.positions[v] = (vpos[0] - min_x + 0.05 * math.sqrt(len(self.G)), vpos[1] - min_y + 0.05 * math.sqrt(len(self.G)))

        else:
            self.current_node = None
            self.titles_by_id = dict()
            self.ids_by_title = dict()
            self.G = nx.Graph()
            self.positions = dict()
            self.graph_width = 0
            self.graph_height = 0

    def update_scale(self):
        drawing_width = self.graph_width * self.scaling_factor
        drawing_height = self.graph_height * self.scaling_factor
        self.view.set_content_size(drawing_width, drawing_height)

    @timer.timer
    def draw(self, snapshot):
        if self.current_node == None: return

        ctx = snapshot.append_cairo(Graphene.Rect().init(0, 0, self.view.view_width, self.view.view_height))

        overview_current_stroke = ColorManager.get_ui_color('overview_current_stroke')
        overview_current_fill = ColorManager.get_ui_color('overview_current_fill')

        for edge in self.G.edges:
            if edge[0] == self.hover_node or edge[1] == self.hover_node:
                color = ColorManager.get_ui_color('overview_edge_hover')
            else:
                color = ColorManager.get_ui_color('overview_edge')

            vertex_pos_1 = self.positions[edge[0]]
            vertex_pos_2 = self.positions[edge[1]]

            Gdk.cairo_set_source_rgba(ctx, color)
            ctx.move_to(vertex_pos_1[0] * self.scaling_factor * self.view.zoom - self.view.scroll_x, vertex_pos_1[1] * self.scaling_factor * self.view.zoom - self.view.scroll_y)
            ctx.line_to(vertex_pos_2[0] * self.scaling_factor * self.view.zoom - self.view.scroll_x, vertex_pos_2[1] * self.scaling_factor * self.view.zoom - self.view.scroll_y)
            ctx.set_line_width(1)
            ctx.stroke()

        for vertex in self.G.nodes:
            vertex_pos = self.positions[vertex]

            if vertex == self.current_node:
                color = ColorManager.get_ui_color('overview_node_current')
                size = 8
            elif vertex == self.hover_node:
                color = ColorManager.get_ui_color('overview_node_normal_hover')
                size = 6
            else:
                color = ColorManager.get_ui_color('overview_node_normal')
                size = 5

            Gdk.cairo_set_source_rgba(ctx, color)
            ctx.arc(vertex_pos[0] * self.scaling_factor * self.view.zoom - self.view.scroll_x, vertex_pos[1] * self.scaling_factor * self.view.zoom - self.view.scroll_y, size, 0, 2 * math.pi)
            ctx.fill()

        if self.hover_node != None:
            vertex_pos = self.positions[self.hover_node]
            text_extents = ctx.text_extents(self.titles_by_id[self.hover_node])
            hpos = max(6, min(self.view.view_width - text_extents.width - 6, vertex_pos[0] * self.scaling_factor * self.view.zoom - self.view.scroll_x - text_extents.width / 2))
            ctx.move_to(hpos, vertex_pos[1] * self.scaling_factor * self.view.zoom - self.view.scroll_y - 12)
            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('overview_title'))
            ctx.show_text(self.titles_by_id[self.hover_node])

    def update_pointer(self):
        x = self.view.pointer_x
        y = self.view.pointer_y

        if x != None and y != None:
            node = self.get_node_at_xy(x, y)
            self.set_hover_node(node)
        else:
            self.set_hover_node(None)

        if self.hover_node != None:
            self.view.content.set_cursor_from_name('pointer')
        else:
            self.view.content.set_cursor_from_name('default')

    def on_primary_button_press(self, controller, n_press, x, y):
        if n_press != 1: return

        node = self.get_node_at_xy(x, y)
        self.set_selected_node(node)
        self.view.content.grab_focus()

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press != 1: return

        node = self.get_node_at_xy(x, y)
        if node != None and node == self.selected_node:
            UseCases.set_active_document(node)

    def get_node_at_xy(self, x, y):
        for node, pos in self.positions.items():
            if abs((pos[0] * self.scaling_factor * self.view.zoom) - self.view.scroll_x - x) + abs((pos[1] * self.scaling_factor * self.view.zoom) - self.view.scroll_y - y) < 13:
                return node
        return None

    def set_hover_node(self, node):
        self.hover_node = node

    def set_selected_node(self, node):
        self.selected_node = node

    def zoom_out(self, arg=None):
        self.view.set_zoom(self.view.zoom * 0.5)

    def zoom_in(self, arg=None):
        self.view.set_zoom(self.view.zoom * 2)

    def zoom_reset(self, arg=None):
        self.view.set_zoom(1)

    def close_overview(self, action=None, parameter=''):
        workspace = WorkspaceRepo.get_workspace()

        mode = workspace.get_mode()
        if mode == 'overview':
            UseCases.show_documents_or_welcome_page()


