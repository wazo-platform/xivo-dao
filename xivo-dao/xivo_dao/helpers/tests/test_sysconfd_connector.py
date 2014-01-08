# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from mock import patch
from unittest import TestCase
from xivo_dao.helpers import sysconfd_connector


class TestSysconfdConnector(TestCase):

    @patch('xivo_dao.helpers.sysconfd_connector.sysconfd_conn_request')
    def test_delete_voicemail_storage(self, sysconfd_conn_request):
        sysconfd_connector.delete_voicemail_storage("default", "123")
        sysconfd_conn_request.assert_called_with('GET', '/delete_voicemail?context=default&name=123', '')

    @patch('xivo_dao.helpers.sysconfd_connector.sysconfd_conn_request')
    def test_exec_request_handlers(self, sysconfd_conn_request):
        commands = {'ctibus': [],
                    'ipbx': []}

        sysconfd_connector.exec_request_handlers(commands)

        sysconfd_conn_request.assert_any_call('POST', '/exec_request_handlers', commands)
