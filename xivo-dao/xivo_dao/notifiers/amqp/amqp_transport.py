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
    def create_and_connect(cls, host, port, queue_name):
        connection_params = pika.ConnectionParameters(host=host, port=port)
        return cls(connection_params, queue_name)

    def __init__(self, connection_params, queue_name):
        self._connect(connection_params)
        self._queue_name = queue_name
        self._setup_queue()

    def _connect(self, params):
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def _setup_queue(self):
        self._channel.queue_declare(exclusive=True)

    def send(self, request):
        self._send_request(request, None)

    def _send_request(self, request, properties):
        self._channel.basic_publish(
            exchange='',
            routing_key=self._queue_name,
            properties=properties,
            body=request
        )

    def close(self):
        self._connection.close()
        self._channel = None
        self._connection = None
