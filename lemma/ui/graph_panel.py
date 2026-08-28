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
from lemma.repos.workspace_repo import WorkspaceRepo
from lemma.repos.document_repo import DocumentRepo
from lemma.use_cases.use_cases import UseCases
import lemma.services.timer as timer


class GraphPanel(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.view = self.main_window.graph_panel

        self.current_node = None
        self.G = nx.Graph()
        self.positions = dict()
        self.titles_by_id = dict()
        self.ids_by_title = dict()
        self.width = 0
        self.height = 0
        self.hover_node = None
        self.selected_node = None

        self.view.content.set_allocate_func(self.size_allocate)
        self.view.content.set_draw_func(self.draw)

        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('enter', self.on_enter)
        self.motion_controller.connect('motion', self.on_hover)
        self.motion_controller.connect('leave', self.on_leave)
        self.view.content.add_controller(self.motion_controller)

        self.primary_click_controller = Gtk.GestureClick()
        self.primary_click_controller.set_button(1)
        self.primary_click_controller.connect('pressed', self.on_primary_button_press)
        self.primary_click_controller.connect('released', self.on_primary_button_release)
        self.view.content.add_controller(self.primary_click_controller)

        MessageBus.subscribe(self, 'new_active_document')
        MessageBus.subscribe(self, 'document_removed')
        MessageBus.subscribe(self, 'document_ast_changed')
        MessageBus.subscribe(self, 'mode_set')

        self.update()

    def animate(self):
        messages = MessageBus.get_messages(self)
        if 'new_active_document' in messages or 'document_removed' in messages or 'document_ast_changed' in messages or 'mode_set' in messages:
            self.update()
            self.view.content.queue_draw()

    @timer.timer
    def update(self):
        document = WorkspaceRepo.get_workspace().get_active_document()

        if document != None:
            self.current_node = document.id
            self.titles_by_id = {document.id: document.title}
            self.ids_by_title = {document.title: document.id}

            G = nx.Graph()
            G.add_node(self.current_node)

            for document_stub in DocumentRepo.list():
                if document.title in document_stub['links']:
                    G.add_node(document_stub['id'])
                    self.titles_by_id[document_stub['id']] = document_stub['title']
                    self.ids_by_title[document_stub['title']] = document_stub['id']
                if document_stub['title'] in document.get_links():
                    G.add_node(document_stub['id'])
                    self.titles_by_id[document_stub['id']] = document_stub['title']
                    self.ids_by_title[document_stub['title']] = document_stub['id']

            for v in G.nodes:
                if v != document.id:
                    G.add_edge(document.id, v)

            for document_stub in DocumentRepo.list():
                if document_stub['id'] not in G.nodes:
                    continue

                for title in list(document_stub['links'] & set(self.ids_by_title)):
                    G.add_edge(document_stub['id'], self.ids_by_title[title])

            pos = nx.spring_layout(G, seed=42, pos={document.id: (0, 0)}, fixed=[document.id])
            self.G = G

            total_dist = 0
            max_x = 0
            max_y = 0
            for v, vpos in pos.items():
                if v == document.id: continue

                total_dist += math.sqrt(vpos[0]**2 + vpos[1]**2)
                max_x = max(max_x, vpos[0], -vpos[0])
                max_y = max(max_y, vpos[1], -vpos[1])

            if len(self.G) > 1:
                scaling_factor_avg = (total_dist / (len(self.G) - 1)) / (math.sqrt(max(9, len(self.G))) * 0.06)
                scaling_x = min(1 / (2 * max_x), 1 / scaling_factor_avg)
                scaling_y = min(1 / (2 * max_y), 1 / scaling_factor_avg)
            else:
                scaling_x = 1
                scaling_y = 1

            self.positions = dict()
            for v, vpos in pos.items():
                self.positions[v] = (0.5 + vpos[0] * scaling_x, 0.5 + vpos[1] * scaling_y)

        else:
            self.current_node = None
            self.titles_by_id = dict()
            self.ids_by_title = dict()
            self.G = nx.Graph()
            self.positions = dict()

    def size_allocate(self, width, height, baseline):
        self.width = width - 34
        self.height = height - 40
        self.view.content.queue_draw()

    @timer.timer
    def draw(self, snapshot):
        if self.current_node == None: return

        ctx = snapshot.append_cairo(Graphene.Rect().init(0, 0, self.width + 34, self.height + 40))

        graph_panel_current_stroke = ColorManager.get_ui_color('graph_panel_current_stroke')
        graph_panel_current_fill = ColorManager.get_ui_color('graph_panel_current_fill')

        for edge in self.G.edges:
            if edge[0] == self.hover_node or edge[1] == self.hover_node:
                color = ColorManager.get_ui_color('graph_panel_edge_hover')
            else:
                color = ColorManager.get_ui_color('graph_panel_edge')

            vertex_pos_1 = self.positions[edge[0]]
            vertex_pos_2 = self.positions[edge[1]]

            Gdk.cairo_set_source_rgba(ctx, color)
            ctx.move_to(vertex_pos_1[0] * self.width + 17, vertex_pos_1[1] * self.height + 20)
            ctx.line_to(vertex_pos_2[0] * self.width + 17, vertex_pos_2[1] * self.height + 20)
            ctx.set_line_width(1)
            ctx.stroke()

        for vertex in self.G.nodes:
            if vertex == self.current_node:
                continue

            vertex_pos = self.positions[vertex]

            if vertex == self.hover_node:
                color = ColorManager.get_ui_color('graph_panel_node_normal_hover')
                size = 6
            else:
                color = ColorManager.get_ui_color('graph_panel_node_normal')
                size = 5

            Gdk.cairo_set_source_rgba(ctx, color)
            ctx.arc(vertex_pos[0] * self.width + 17, vertex_pos[1] * self.height + 20, size, 0, 2 * math.pi)
            ctx.fill()

        current_pos = self.positions[self.current_node]

        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('graph_panel_node_current'))
        ctx.arc(current_pos[0] * self.width + 17, current_pos[1] * self.height + 20, 8, 0, 2 * math.pi)
        ctx.fill()

        if self.hover_node != None:
            vertex_pos = self.positions[self.hover_node]
            text_extents = ctx.text_extents(self.titles_by_id[self.hover_node])
            hpos = max(6, min(self.width - text_extents.width + 28, vertex_pos[0] * self.width + 17 - text_extents.width / 2))
            ctx.move_to(hpos, vertex_pos[1] * self.height + 9)
            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('graph_panel_title'))
            ctx.show_text(self.titles_by_id[self.hover_node])

        self.update_pointer()

    def on_enter(self, controller, x, y):
        node = self.get_node_at_xy(x, y)
        self.set_hover_node(node)

    def on_hover(self, controller, x, y):
        node = self.get_node_at_xy(x, y)
        self.set_hover_node(node)

    def on_leave(self, controller):
        self.set_hover_node(None)

    def on_primary_button_press(self, controller, n_press, x, y):
        if n_press != 1: return

        node = self.get_node_at_xy(x, y)
        self.set_selected_node(node)

    def on_primary_button_release(self, controller, n_press, x, y):
        if n_press != 1: return

        node = self.get_node_at_xy(x, y)
        if node != None and node == self.selected_node and node != self.current_node:
            UseCases.set_active_document(node)
            self.set_hover_node(None)

        self.set_selected_node(None)

    def get_node_at_xy(self, x, y):
        for node, pos in self.positions.items():
            if abs((pos[0] * self.width + 17) - x) + abs((pos[1] * self.height + 20) - y) < 13:
                return node
        return None

    def set_hover_node(self, node):
        self.hover_node = node
        self.view.content.queue_draw()

    def set_selected_node(self, node):
        self.selected_node = node
        self.view.content.queue_draw()

    def update_pointer(self):
        if self.hover_node != None:
            self.view.content.set_cursor_from_name('pointer')
        else:
            self.view.content.set_cursor_from_name('default')


