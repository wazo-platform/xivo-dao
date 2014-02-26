# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from mock import patch, Mock

from xivo_dao.data_handler.context.model import Context
from xivo_dao.data_handler.context import notifier


class TestContextNotifier(unittest.TestCase):

    @patch('xivo_bus.resources.context.event.CreateContextEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_created(self, send_bus_command, CreateContextEvent):
        new_event = CreateContextEvent.return_value = Mock()

        context = Context(name='foo',
                          display_name='bar',
                          type='internal',
                          description='description')

        notifier.created(context)

        CreateContextEvent.assert_called_once_with(context.name,
                                                   context.display_name,
                                                   context.description,
                                                   context.type)

        send_bus_command.assert_called_once_with(new_event)
