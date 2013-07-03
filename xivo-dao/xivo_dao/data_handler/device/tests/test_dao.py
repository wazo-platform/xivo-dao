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

from hamcrest import assert_that
from hamcrest.core import equal_to
from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.devicefeatures import DeviceFeatures


class TestDeviceDao(DAOTestCase):

    tables = [
        DeviceFeatures
    ]

    def setUp(self):
        self.empty_tables()

    def test_get_no_device(self):
        self.assertRaises(LookupError, device_dao.get, '666')

    def test_get(self):
        deviceid = 'sdklfj'

        device_id = self.add_device(deviceid=deviceid)

        device = device_dao.get(device_id)

        assert_that(device.deviceid, equal_to(deviceid))

    def test_get_by_deviceid_no_device(self):
        self.assertRaises(LookupError, device_dao.get_by_deviceid, '1234')

    def test_get_by_deviceid(self):
        deviceid = 'sdklfj'

        device_id = self.add_device(deviceid=deviceid)

        device = device_dao.get_by_deviceid(deviceid)

        assert_that(device.id, equal_to(device_id))
        assert_that(device.deviceid, equal_to(deviceid))
