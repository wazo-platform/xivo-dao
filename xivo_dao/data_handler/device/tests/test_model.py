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

from hamcrest import assert_that, is_not
from unittest import TestCase
from xivo_dao.data_handler.device.model import Device


class TestCallLogModel(TestCase):

    def test_is_switchboard_plugin_name(self):
        device = Device()
        device.plugin = 'xivo-aastra-switchboard'

        assert_that(device.is_switchboard())

    def test_is_switchboard_no_plugin(self):
        device = Device()

        assert_that(is_not(device.is_switchboard()))

    def test_is_switchboard_option_true(self):
        device = Device()
        device.options = {'switchboard': True}

        assert_that(device.is_switchboard())

    def test_is_switchboard_option_false(self):
        device = Device()
        device.options = {'switchboard': False}

        assert_that(is_not(device.is_switchboard()))

    def test_is_switchboard_no_option(self):
        device = Device()
        device.options = {}

        assert_that(is_not(device.is_switchboard()))
