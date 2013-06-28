# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.helpers.notifiers.amqp.marshaler import Marshaler
from xivo_dao.helpers.notifiers.amqp.amqp_transport import AMQPTransport


class AMQPPublisherError(Exception):

    def __init__(self, error):
        Exception.__init__(self, error)
        self.error = error


class AMQPPublisher(object):

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 5672

    def __init__(self):
        self._transport = None
        self._marshaler = Marshaler()

    def close(self):
        if self._transport is None:
            return

        self._transport.close()
        self._transport = None

    def connect(self, hostname=DEFAULT_HOST, port=DEFAULT_PORT):
        if self._transport is not None:
            raise Exception('already connected')

        self._transport = self._new_transport(hostname, port)

    def _new_transport(self, hostname, port):
        return AMQPTransport.create_and_connect(hostname, port)

    def execute_command(self, cmd, fetch_response=False):
        request = self._marshaler.marshal_command(cmd)
        self._transport.send(request)
