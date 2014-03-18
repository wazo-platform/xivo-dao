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

import unittest
from xivo_dao.data_handler.configuration import services
from mock import patch
from hamcrest.core import assert_that
from hamcrest.core.core.isequal import equal_to


class TestConfiguration(unittest.TestCase):

    @patch('xivo_dao.data_handler.configuration.dao.is_live_reload_enabled')
    def test_get_live_reload_status(self, is_live_reload_enabled):
        is_live_reload_enabled.return_value = False
        expected_result = {'enabled': False}

        result = services.get_live_reload_status()

        assert_that(result, equal_to(expected_result))
        is_live_reload_enabled.assert_called_once_with()

    @patch('xivo_dao.data_handler.configuration.notifier.live_reload_status_changed')
    @patch('xivo_dao.data_handler.configuration.dao.set_live_reload_status')
    @patch('xivo_dao.data_handler.configuration.validator.validate_live_reload_data')
    def test_set_live_reload_status(self, validate_live_reload_data, set_live_reload_status, live_reload_status_changed):
        data = {'enabled': True}

        services.set_live_reload_status(data)

        validate_live_reload_data.assert_called_once_with(data)
        set_live_reload_status.assert_called_once_with(data)
        live_reload_status_changed.assert_called_once_with(data)
