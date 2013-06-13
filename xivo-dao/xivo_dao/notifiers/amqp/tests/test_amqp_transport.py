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

import unittest
import pika

from mock import Mock, patch
from xivo_dao.notifiers.amqp.amqp_transport import AMQPTransport


class TestAMQPTransport(unittest.TestCase):

    AMQP_HOST = 'localhost'

    def setUp(self):
        self.patcher = patch('pika.BlockingConnection')
        self.blocking_connection = self.patcher.start()
        self.connection = Mock()
        self.channel = Mock()
        self.blocking_connection.return_value = self.connection
        self.connection.channel.return_value = self.channel

    def tearDown(self):
        self.patcher.stop()

    @patch('pika.ConnectionParameters')
    def test_create_and_connect(self, connection_params):
        AMQPTransport.create_and_connect('localhost', 5672, 'queue_name')

        connection_params.assert_called_once_with(host='localhost', port=5672)

    def test_connect(self):
        self._new_transport()

        self.blocking_connection.assert_called_once()
        self.connection.channel.assert_called_once()

    def test_setup_queue(self):
        result = Mock()
        result.method = Mock()
        result.method.queue = Mock()
        self.channel.queue_declare.return_value = result

        self._new_transport()

        self.channel.queue_declare.assert_called_once_with(exclusive=True)

    def test_send_request(self):
        transport = self._new_transport()
        transport._send_request('blah', None)

        self.channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='queue_name',
            properties=None,
            body='blah'
        )

    def test_close(self):
        transport = self._new_transport()
        transport.close()
        self.connection.close.assert_called_once()

    def _new_transport(self):
        params = pika.ConnectionParameters(host='localhost')
        transport = AMQPTransport(params, 'queue_name')

        return transport


if __name__ == "__main__":
    unittest.main()
