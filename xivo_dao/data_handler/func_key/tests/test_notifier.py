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

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import notifier

from mock import patch, Mock


class TestNotifier(TestCase):

    @patch('xivo_bus.resources.func_key.event.CreateFuncKeyEvent')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_created(self, send_bus_command, CreateFuncKeyEvent):
        new_event = CreateFuncKeyEvent.return_value = Mock()

        func_key = FuncKey(id=1,
                           type='speeddial',
                           destination='user',
                           destination_id=2)

        notifier.created(func_key)

        CreateFuncKeyEvent.assert_called_once_with(func_key.id,
                                                   func_key.type,
                                                   func_key.destination,
                                                   func_key.destination_id)

        send_bus_command.assert_called_once_with(new_event)
