# -*- coding: utf-8 -*-
#
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

from .. import notifier
from mock import Mock, patch
from unittest import TestCase

ULE_ID = 1
USER_ID = 2
LINE_ID = 3
EXTENSION_ID = 4
MAIN_USER = True
MAIN_LINE = True

SYSCONFD_DATA = {
    'ctibus': [
        'xivo[user,edit,%s]' % USER_ID,
        'xivo[phone,edit,%s]' % LINE_ID
    ],
    'dird': [],
    'ipbx': ['dialplan reload'],
    'agentbus': []
}

ULE = Mock(id=ULE_ID,
           user_id=USER_ID,
           line_id=LINE_ID,
           extension_id=EXTENSION_ID,
           main_user=MAIN_USER,
           main_line=MAIN_LINE)


class TestUserLinkNotifier(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('xivo_dao.data_handler.user_line_extension.command.CreateUserLineExtensionCommand')
    @patch('xivo_dao.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_created(self, send_bus_command, exec_request_handlers, command_init):
        new_command = command_init.return_value = Mock()

        notifier.created(ULE)

        exec_request_handlers.assert_called_once_with(SYSCONFD_DATA)
        command_init.assert_called_once_with(ULE_ID,
                                             USER_ID,
                                             LINE_ID,
                                             EXTENSION_ID,
                                             MAIN_USER,
                                             MAIN_LINE)
        send_bus_command.assert_called_once_with(new_command)

    @patch('xivo_dao.data_handler.user_line_extension.command.EditUserLineExtensionCommand')
    @patch('xivo_dao.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_edited(self, send_bus_command, exec_request_handlers, command_init):
        new_command = command_init.return_value = Mock()

        notifier.edited(ULE)

        exec_request_handlers.assert_called_once_with(SYSCONFD_DATA)
        command_init.assert_called_once_with(ULE_ID,
                                             USER_ID,
                                             LINE_ID,
                                             EXTENSION_ID,
                                             MAIN_USER,
                                             MAIN_LINE)
        send_bus_command.assert_called_once_with(new_command)

    @patch('xivo_dao.data_handler.user_line_extension.command.DeleteUserLineExtensionCommand')
    @patch('xivo_dao.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_dao.helpers.bus_manager.send_bus_command')
    def test_deleted(self, send_bus_command, exec_request_handlers, command_init):
        new_command = command_init.return_value = Mock()

        notifier.deleted(ULE)

        exec_request_handlers.assert_called_once_with(SYSCONFD_DATA)
        command_init.assert_called_once_with(ULE_ID,
                                             USER_ID,
                                             LINE_ID,
                                             EXTENSION_ID,
                                             MAIN_USER,
                                             MAIN_LINE)
        send_bus_command.assert_called_once_with(new_command)
