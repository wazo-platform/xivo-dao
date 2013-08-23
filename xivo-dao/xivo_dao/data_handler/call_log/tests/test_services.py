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

from hamcrest import assert_that, equal_to
from mock import Mock, patch
from unittest import TestCase
from xivo_dao.data_handler.call_log import services
from xivo_dao.data_handler.call_log.model import CallLog


class TestCallLogServices(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('xivo_dao.data_handler.call_log.dao.find_all')
    def test_find_all_not_found(self, mock_dao):
        expected_result = mock_dao.return_value = []

        result = services.find_all()

        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.data_handler.call_log.dao.find_all')
    def test_find_all_found(self, mock_dao):
        expected_result = mock_dao.return_value = \
            call_log_1, call_log_2 = [Mock(CallLog), Mock(CallLog)]

        result = services.find_all()

        assert_that(result, equal_to(expected_result))
