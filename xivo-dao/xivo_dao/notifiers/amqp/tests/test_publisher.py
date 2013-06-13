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
from mock import Mock, patch, ANY
from xivo_dao.notifiers.amqp.amqp_transport import AMQPTransport
from xivo_dao.notifiers.amqp.marshaler import Marshaler
from xivo_dao.notifiers.amqp.publisher import AMQPPublisher


class TestAMQPPublisher(unittest.TestCase):

    def setUp(self):
        self.marshaler = Mock(Marshaler)
        self.transport = Mock(AMQPTransport)
        self.publisher = AMQPPublisher()
        self.publisher._marshaler = self.marshaler
        self.publisher._transport = self.transport

    @patch('xivo_dao.notifiers.amqp.publisher.AMQPTransport')
    def test_connect_no_transport(self, amqp_transport_constructor):
        hostname = 'localhost'
        port = 5672

        publisher = AMQPPublisher()
        publisher.connect(hostname, port)
        amqp_transport_constructor.create_and_connect.assert_called_once_with(hostname, port)

    def test_connect_already_connected(self):
        hostname = 'localhost'
        port = 5672

        publisher = AMQPPublisher()
        publisher.connect(hostname, port)
        self.assertRaises(Exception, publisher.connect, hostname, port)

    @patch('xivo_dao.notifiers.amqp.amqp_transport.AMQPTransport')
    def test_close_transport_with_no_connection(self, amqp_transport):
        client = AMQPPublisher()
        client.close()
        self.assertFalse(amqp_transport.create_and_connect.called)

    @patch('xivo_dao.notifiers.amqp.publisher.AMQPTransport')
    def test_connect_and_close_opens_and_closes_transport(self, amqp_transport_constructor):
        transport = Mock()
        amqp_transport_constructor.create_and_connect.return_value = transport

        publisher = AMQPPublisher()
        publisher.connect()
        publisher.close()

        amqp_transport_constructor.create_and_connect.assert_called_once_with(ANY, ANY)
        transport.close.assert_called_once_with()

    def test_execute_command(self):
        command = Mock()
        request = Mock()
        self.marshaler.marshal_command.return_value = request

        self.publisher._fetch_response = False
        self.publisher.execute_command(command)

        self.marshaler.marshal_command.assert_called_once_with(command)
        self.transport.send.assert_called_once_with(request)
