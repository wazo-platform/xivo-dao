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

from hamcrest import assert_that, all_of, equal_to, has_items, has_property, instance_of
from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.alchemy.devicefeatures import DeviceFeatures as DeviceSchema
from xivo_dao.data_handler.device.model import Device
from sqlalchemy.exc import SQLAlchemyError
from mock import Mock, patch
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError
from xivo_dao.data_handler.line.model import LineSIP


class TestDeviceDao(DAOTestCase):

    tables = [
        DeviceSchema
    ]

    def _has_properties(self, properties):
        matchers = []
        for key, value in properties.iteritems():
            matchers.append(has_property(key, value))
        return all_of(*matchers)

    def setUp(self):
        self.empty_tables()

    def test_get_no_device(self):
        self.assertRaises(LookupError, device_dao.get, '666')

    def test_get(self):
        deviceid = 'sdklfj'

        expected_device = self.add_device(deviceid=deviceid)

        device = device_dao.get(expected_device.id)

        assert_that(device.deviceid, equal_to(deviceid))

    def test_get_by_deviceid_no_device(self):
        self.assertRaises(LookupError, device_dao.get_by_deviceid, '1234')

    def test_get_by_deviceid(self):
        deviceid = 'sdklfj'

        expected_device = self.add_device(deviceid=deviceid)

        device = device_dao.get_by_deviceid(deviceid)

        assert_that(device.id, equal_to(expected_device.id))
        assert_that(device.deviceid, equal_to(deviceid))

    def test_find_all_no_devices(self):
        expected = []

        result = device_dao.find_all()

        assert_that(result, equal_to(expected))

    def test_find_all(self):
        device1 = {
            'deviceid': 'deviceid1',
            'config': 'config1',
            'plugin': 'plugin1',
            'ip': 'ip1',
            'mac': 'mac1',
            'sn': 'sn1',
            'vendor': 'vendor1',
            'model': 'model1',
            'version': 'version1',
            'proto': 'proto1',
            'internal': 1,
            'configured': 1,
            'commented': 1,
            'description': 'description1'
        }
        device2 = {
            'deviceid': 'deviceid2',
            'config': 'config2',
            'plugin': 'plugin2',
            'ip': 'ip2',
            'mac': 'mac2',
            'sn': 'sn2',
            'vendor': 'vendor2',
            'model': 'model2',
            'version': 'version2',
            'proto': 'proto2',
            'internal': 2,
            'configured': 2,
            'commented': 2,
            'description': 'description2'
        }
        self.add_device(**device1)
        self.add_device(**device2)

        result = device_dao.find_all()

        assert_that(result, has_items(
            self._has_properties(device1),
            self._has_properties(device2),
        ))

    def test_create(self):

        device_properties = {
            'deviceid': 'deviceid1',
            'config': 'config1',
            'plugin': 'plugin1',
            'ip': 'ip1',
            'mac': 'mac1',
            'sn': 'sn1',
            'vendor': 'vendor1',
            'model': 'model1',
            'version': 'version1',
            'proto': 'proto1',
            'internal': 1,
            'configured': 1,
            'commented': 1,
            'description': 'description1'
        }

        device = Device(**device_properties)

        result = device_dao.create(device)

        assert_that(result, self._has_properties(device_properties))
        assert_that(result, has_property('id', instance_of(int)))

    @patch('xivo_dao.helpers.db_manager.AsteriskSession')
    def test_create_with_error_from_dao(self, Session):
        session = Mock()
        session.commit.side_effect = SQLAlchemyError()
        Session.return_value = session

        extension = Device(deviceid='toto')

        self.assertRaises(ElementCreationError, device_dao.create, extension)
        session.begin.assert_called_once_with()
        session.rollback.assert_called_once_with()

    def test_delete(self):
        deviceid = 'sdklfj'
        expected_extension = self.add_device(deviceid=deviceid)

        extension = device_dao.get(expected_extension.id)

        device_dao.delete(extension)

        row = self.session.query(DeviceSchema).filter(DeviceSchema.id == expected_extension.id).first()

        self.assertEquals(row, None)

    def test_delete_not_exist(self):
        extension = Device(id=1)

        self.assertRaises(ElementDeletionError, device_dao.delete, extension)
