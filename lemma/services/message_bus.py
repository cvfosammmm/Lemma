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


class MessageBus():

    subscribers_by_message_type = dict()
    messages_by_subscriber = dict()

    def add_message(change_code, parameter=None):
        if change_code in MessageBus.subscribers_by_message_type:
            subscribers = MessageBus.subscribers_by_message_type[change_code]
            for subscriber in subscribers:
                MessageBus.messages_by_subscriber[subscriber].append(change_code)

    def subscribe(subscriber, message_type):
        if message_type not in MessageBus.subscribers_by_message_type:
            MessageBus.subscribers_by_message_type[message_type] = []
        if subscriber not in MessageBus.subscribers_by_message_type[message_type]:
            MessageBus.subscribers_by_message_type[message_type].append(subscriber)
        if subscriber not in MessageBus.messages_by_subscriber:
            MessageBus.messages_by_subscriber[subscriber] = []

    def get_messages(subscriber):
        messages = MessageBus.messages_by_subscriber[subscriber]
        MessageBus.messages_by_subscriber[subscriber] = []
        return messages


