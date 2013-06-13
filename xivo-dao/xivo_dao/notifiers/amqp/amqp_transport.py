# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import pika


class AMQPTransport(object):

    @classmethod
    def create_and_connect(cls, host, port):
        connection_params = pika.ConnectionParameters(host=host, port=port)
        return cls(connection_params)

    def __init__(self, connection_params):
        self._connect(connection_params)
        self._setup_exchange()

    def _connect(self, params):
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def _setup_exchange(self):
        self._channel.exchange_declare(exchange='notifier',
                                       type='fanout')

    def send(self, request):
        self._send_request(request)

    def _send_request(self, request):
        self._channel.basic_publish(
            exchange='notifier',
            routing_key='',
            body=request
        )

    def close(self):
        self._connection.close()
        self._channel = None
        self._connection = None
