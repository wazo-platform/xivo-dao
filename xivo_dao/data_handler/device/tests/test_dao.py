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

from hamcrest import assert_that, equal_to, same_instance, none, all_of, has_property, contains
from mock import Mock, patch
from urllib2 import HTTPError
from StringIO import StringIO
from contextlib import contextmanager

from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.exception import DataError
from xivo_dao.data_handler.exception import NotFoundError
from xivo_dao.data_handler.exception import InputError


class TestDeviceDao(unittest.TestCase):

    config_id = 'ad0a12fd5f244ae68a3c626789203699'

    def setUp(self):
        self.deviceid = "ad0a12fd5f244ae68a3c626789203698"

        self.provd_device = {
            u'added': u'auto',
            u'configured': True,
            u'id': self.deviceid,
            u'ip': '10.0.0.1',
            u'config': self.deviceid,
            u'mac': '00:11:22:33:44:55',
            u'model': '6731i',
            u'plugin': 'xivo-aastra-3.2.2-SP3',
            u'vendor': 'Aastra',
            u'version': '3.2.2.3077',
        }

        self.provd_config = {
            u'configdevice': u'defaultconfigdevice',
            u'deletable': True,
            u'id': self.deviceid,
            u'parent_ids': [u'base', u'defaultconfigdevice'],
            u'raw_config': {}
        }

        self.device_properties = {
            'id': self.deviceid,
            'ip': '10.0.0.1',
            'mac': '00:11:22:33:44:55',
            'model': '6731i',
            'plugin': 'xivo-aastra-3.2.2-SP3',
            'vendor': 'Aastra',
            'version': '3.2.2.3077',
            'template_id': 'defaultconfigdevice',
            'status': 'configured',
        }

        self.expected_device = Device(**self.device_properties)

    @contextmanager
    def provd_managers(self):
        config_patcher = patch('xivo_dao.helpers.provd_connector.config_manager')
        device_patcher = patch('xivo_dao.helpers.provd_connector.device_manager')
        plugin_patcher = patch('xivo_dao.helpers.provd_connector.plugin_manager')

        mock_device_manager = device_patcher.start()
        mock_config_manager = config_patcher.start()
        mock_plugin_manager = plugin_patcher.start()

        device_manager = Mock()
        config_manager = Mock()
        plugin_manager = Mock()

        mock_device_manager.return_value = device_manager
        mock_config_manager.return_value = config_manager
        mock_plugin_manager.return_value = plugin_manager

        yield (device_manager, config_manager, plugin_manager)

        config_patcher.stop()
        device_patcher.stop()
        plugin_patcher.stop()


class TestDeviceDaoGetFind(TestDeviceDao):

    @patch('xivo_dao.data_handler.device.provd_converter.to_model')
    @patch('xivo_dao.data_handler.device.dao.fetch_device_and_config')
    def test_get_no_device(self, fetch_device_and_config, to_model):
        fetch_device_and_config.return_value = None, None

        self.assertRaises(NotFoundError, device_dao.get, self.deviceid)
        fetch_device_and_config.assert_called_once_with(self.deviceid)
        assert_that(to_model.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.device.provd_converter.to_model')
    @patch('xivo_dao.data_handler.device.dao.fetch_device_and_config')
    def test_get(self, fetch_device_and_config, to_model):
        fetch_device_and_config.return_value = self.provd_device, self.provd_config
        expected_device = to_model.return_value = Mock(Device)

        device = device_dao.get(self.deviceid)

        fetch_device_and_config.assert_called_once_with(self.deviceid)
        to_model.assert_called_once_with(self.provd_device, self.provd_config)
        assert_that(device, same_instance(expected_device))

    def test_fetch_device_and_config_when_device_and_config_exist(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            expected_device = device_manager.get.return_value = {'id': self.deviceid,
                                                                 'config': self.config_id}
            expected_config = config_manager.get.return_value = Mock()
            device, config = device_dao.fetch_device_and_config(self.deviceid)

            assert_that(device, same_instance(expected_device))
            assert_that(config, same_instance(expected_config))
            device_manager.get.assert_called_once_with(self.deviceid)
            config_manager.get.assert_called_once_with(self.config_id)

    def test_fetch_device_and_config_when_device_exists_and_references_inexistant_config(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = {'id': self.deviceid,
                                               'config': self.config_id}
            config_manager.get.side_effect = HTTPError('', 404, '', '', StringIO(''))

            self.assertRaises(NotFoundError, device_dao.fetch_device_and_config, self.deviceid)

            device_manager.get.assert_called_once_with(self.deviceid)
            config_manager.get.assert_called_once_with(self.config_id)

    def test_fetch_device_and_config_when_device_exists_and_references_no_config(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            expected_device = device_manager.get.return_value = {'id': self.deviceid}

            device, config = device_dao.fetch_device_and_config(self.deviceid)

            assert_that(device, same_instance(expected_device))
            assert_that(config, none())
            device_manager.get.assert_called_once_with(self.deviceid)
            assert_that(config_manager.find.call_count, equal_to(0))

    def test_fetch_device_and_config_when_device_does_not_exist(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.side_effect = HTTPError('', 404, '', '', StringIO(''))

            device, config = device_dao.fetch_device_and_config(self.deviceid)

            assert_that(device, none())
            assert_that(config, none())
            device_manager.get.assert_called_once_with(self.deviceid)
            assert_that(config_manager.find.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.device.provd_converter.to_model')
    @patch('xivo_dao.data_handler.device.dao.fetch_device_and_config')
    def test_find_not_found(self, fetch_device_and_config, to_model):
        fetch_device_and_config.return_value = None, None
        to_model.return_value = Mock(Device)

        result = device_dao.find(self.deviceid)

        fetch_device_and_config.assert_called_once_with(self.deviceid)
        assert_that(to_model.call_count, equal_to(0))
        assert_that(result, none())

    @patch('xivo_dao.data_handler.device.provd_converter.to_model')
    @patch('xivo_dao.data_handler.device.dao.fetch_device_and_config')
    def test_find_found(self, fetch_device_and_config, to_model):
        device, config = fetch_device_and_config.return_value = (Mock(), Mock())
        model = to_model.return_value = Mock(Device)

        result = device_dao.find(self.deviceid)

        assert_that(result, same_instance(model))
        fetch_device_and_config.assert_called_once_with(self.deviceid)
        to_model.assert_called_once_with(device, config)


class TestDeviceDaoFindAll(TestDeviceDao):

    @patch('xivo_dao.data_handler.device.dao.find_devices_ordered')
    @patch('xivo_dao.data_handler.device.dao.filter_list')
    @patch('xivo_dao.data_handler.device.dao.paginate_devices')
    @patch('xivo_dao.data_handler.device.dao.convert_devices_to_model')
    def test_search(self,
                    convert_devices_to_model,
                    paginate_devices,
                    filter_list,
                    find_devices_ordered):
        devices_ordered = find_devices_ordered.return_value = Mock()
        devices_filtered = filter_list.return_value = [Mock(), Mock()]
        devices_paginated = paginate_devices.return_value = Mock()
        models = convert_devices_to_model.return_value = Mock()
        order, direction, limit, skip, search = Mock(), Mock(), Mock(), Mock(), Mock()

        result = device_dao.search(order=order,
                                   direction=direction,
                                   limit=limit,
                                   skip=skip,
                                   search=search)

        find_devices_ordered.assert_called_once_with(order, direction)
        filter_list.assert_called_once_with(devices_ordered, search)
        paginate_devices.assert_called_once_with(devices_filtered, skip, limit)
        convert_devices_to_model.assert_called_once_with(devices_paginated)
        assert_that(result, all_of(has_property('total', 2),
                                   has_property('items', models)))

    def test_find_devices_ordered_no_order(self):
        with self.provd_managers() as (device_manager, _, _):
            order, direction = None, None

            device_dao.find_devices_ordered(order, direction)

            device_manager.find.assert_called_once_with()

    def test_find_devices_ordered_with_order_no_direction(self):
        with self.provd_managers() as (device_manager, _, _):
            order, direction = Mock(), None

            device_dao.find_devices_ordered(order, direction)

            device_manager.find.assert_called_once_with(sort=(order, 1))

    def test_find_devices_ordered_with_order_and_direction_asc(self):
        with self.provd_managers() as (device_manager, _, _):
            order, direction = Mock(), 'asc'

            device_dao.find_devices_ordered(order, direction)

            device_manager.find.assert_called_once_with(sort=(order, 1))

    def test_find_devices_ordered_with_order_and_direction_desc(self):
        with self.provd_managers() as (device_manager, _, _):
            order, direction = Mock(), 'desc'

            device_dao.find_devices_ordered(order, direction)

            device_manager.find.assert_called_once_with(sort=(order, -1))

    def test_find_devices_ordered_with_direction_and_no_order(self):
        with self.provd_managers() as (device_manager, _, _):
            order, direction = None, Mock()

            self.assertRaises(InputError, device_dao.find_devices_ordered, order, direction)

            assert_that(device_manager.find.call_count, equal_to(0))

    def test_paginate_devices_no_pagination(self):
        devices = [device1, device2, device3] = [Mock(), Mock(), Mock()]
        skip, limit = 0, None

        result = device_dao.paginate_devices(devices, skip, limit)

        assert_that(result, contains(*devices))

    def test_paginate_devices_with_skip(self):
        devices = [device1, device2, device3] = [Mock(), Mock(), Mock()]
        skip, limit = 1, None

        result = device_dao.paginate_devices(devices, skip, limit)

        assert_that(result, contains(device2, device3))

    def test_paginate_devices_with_limit(self):
        devices = [device1, device2, device3] = [Mock(), Mock(), Mock()]
        skip, limit = 0, 2

        result = device_dao.paginate_devices(devices, skip, limit)

        assert_that(result, contains(device1, device2))

    def test_paginate_devices_with_skip_and_limit(self):
        devices = [device1, device2, device3] = [Mock(), Mock(), Mock()]
        skip, limit = 1, 1

        result = device_dao.paginate_devices(devices, skip, limit)

        assert_that(result, contains(device2))

    @patch('xivo_dao.data_handler.device.provd_converter.to_model')
    def test_convert_devices_to_model(self, to_model):
        with self.provd_managers() as (_, config_manager, _):
            devices = [device1, device2] = [{'config': self.config_id},
                                            {}]
            config1 = config_manager.get.return_value = Mock()
            models = to_model.side_effect = [Mock(), Mock()]

            result = device_dao.convert_devices_to_model(devices)

            to_model.assert_any_call(device1, config1)
            to_model.assert_any_call(device2, None)
            assert_that(result, contains(*models))


class TestDeviceDaoFilterList(TestDeviceDao):

    def test_filter_list_no_search(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = None

        result = device_dao.filter_list(devices, search)

        assert_that(result, equal_to(expected))

    def test_filter_list_empty_list(self):
        devices = []
        expected = []
        search = 'toto'

        result = device_dao.filter_list(devices, search)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_wrong_search(self):
        devices = [self.provd_device]
        expected = []
        search = 'toto'

        result = device_dao.filter_list(devices, search)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_right_search(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = self.deviceid[0:5]

        result = device_dao.filter_list(devices, search)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_uppercase_search(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = self.deviceid.upper()

        result = device_dao.filter_list(devices, search)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_trailing_spaces(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = ' %s ' % self.deviceid

        result = device_dao.filter_list(devices, search)
        assert_that(result, equal_to(expected))


class TestDeviceDaoCreate(TestDeviceDao):

    @patch('xivo_dao.data_handler.device.provd_converter.to_source')
    @patch('xivo_dao.data_handler.device.dao.generate_device_id')
    def test_create_device(self, generate_device_id, provd_to_source):
        device_id = 'abcd1234'
        device = Device()

        provd_device = Mock()
        provd_config = Mock()

        generate_device_id.return_value = device_id
        provd_to_source.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            result = device_dao.create(device)

            generate_device_id.assert_called_once_with()
            provd_to_source.assert_called_once_with(device)
            device_manager.update.assert_called_once_with(provd_device)
            config_manager.add.assert_called_once_with(provd_config)

            assert_that(result.id, equal_to(device_id))

    @patch('xivo_dao.data_handler.device.provd_converter.to_source')
    @patch('xivo_dao.data_handler.device.dao.generate_device_id')
    def test_create_with_device_manager_error(self, generate_device_id, provd_to_source):
        device_id = 'abcd1234'
        device = Device()

        provd_device = Mock()
        provd_config = Mock()

        generate_device_id.return_value = device_id
        provd_to_source.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.update.side_effect = Exception()

            self.assertRaises(DataError, device_dao.create, device)

            assert_that(config_manager.add.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.device.provd_converter.to_source')
    @patch('xivo_dao.data_handler.device.dao.generate_device_id')
    def test_create_with_config_manager_error(self, generate_device_id, provd_to_source):
        device_id = 'abcd1234'
        device = Device()

        provd_device = Mock()
        provd_config = Mock()

        generate_device_id.return_value = device_id
        provd_to_source.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            config_manager.add.side_effect = Exception()

            self.assertRaises(DataError, device_dao.create, device)
            device_manager.remove.assert_called_once_with(device_id)

    def test_generate_device_id(self):
        device_id = 'abc1234'

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.add.return_value = device_id

            result = device_dao.generate_device_id()

            self.assertEquals(result, device_id)
            device_manager.add.assert_called_once_with({})

    def test_generate_device_id_with_error(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.add.side_effect = Exception()

            self.assertRaises(DataError, device_dao.generate_device_id)
            device_manager.add.assert_called_once_with({})


class TestDeviceDaoEdit(TestDeviceDao):

    @patch('xivo_dao.data_handler.device.provd_converter.build_edit')
    def test_edit(self, provd_build_edit):
        device_id = 'abc1234'
        config_id = 'def5678'
        device = Device(id=device_id)

        provd_device = {'id': device_id, 'config': config_id}
        provd_config = Mock()

        provd_build_edit.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device
            config_manager.get.return_value = provd_config

            device_dao.edit(device)

            device_manager.get.assert_called_once_with(device_id)
            config_manager.get.assert_called_once_with(config_id)
            provd_build_edit.assert_called_once_with(device, provd_device, provd_config)
            device_manager.update.assert_called_once_with(provd_device)
            config_manager.update.assert_called_once_with(provd_config)

    @patch('xivo_dao.data_handler.device.provd_converter.build_edit')
    def test_edit_only_device(self, provd_build_edit):
        device_id = 'abc1234'
        device = Device(id=device_id)

        provd_device = {'id': device_id}
        provd_config = None

        provd_build_edit.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device

            device_dao.edit(device)

            device_manager.get.assert_called_once_with(device_id)
            provd_build_edit.assert_called_once_with(device, provd_device, provd_config)
            device_manager.update.assert_called_once_with(provd_device)

            assert_that(config_manager.get.call_count, equal_to(0))
            assert_that(config_manager.update.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.device.provd_converter.build_edit')
    def test_edit_with_error_on_config_update(self, provd_build_edit):
        device_id = 'abc1234'
        config_id = 'def456'
        device = Device(id=device_id)

        provd_device = {'id': device_id, 'config': config_id}
        provd_config = Mock()

        provd_build_edit.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device
            config_manager.get.return_value = provd_config
            config_manager.update.side_effect = Exception

            self.assertRaises(DataError, device_dao.edit, device)

    @patch('xivo_dao.data_handler.device.provd_converter.build_edit')
    def test_edit_with_error_on_device_update(self, provd_build_edit):
        device_id = 'abc1234'
        device = Device(id=device_id)

        provd_build_edit.return_value = ({}, {})

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = {}
            config_manager.get.return_value = {}
            device_manager.update.side_effect = Exception

            self.assertRaises(DataError, device_dao.edit, device)


class TestDeviceDaoMacExists(TestDeviceDao):

    def test_mac_exists_no_mac(self):
        mac = 'FF:FF:FF:FF:FF'

        with self.provd_managers() as (device_manager, _, _):
            device_manager.find.return_value = []

            result = device_dao.mac_exists(mac)

            assert_that(result, equal_to(False))
            device_manager.find.assert_called_once_with({'mac': mac.lower()})

    def test_mac_exists_with_a_mac(self):
        mac = 'FF:FF:FF:FF:FF'

        with self.provd_managers() as (device_manager, _, _):
            device_manager.find.return_value = [{u'added': u'auto',
                                                u'config': u'cb20ee7c27e2483ba737e8061b40113d',
                                                u'configured': True,
                                                u'id': u'cb20ee7c27e2483ba737e8061b40113d',
                                                u'ip': u'10.0.0.1',
                                                u'mac': u'FF:FF:FF:FF:FF:FF',
                                                u'model': u'820',
                                                u'plugin': u'xivo-snom-8.7.3.19',
                                                u'vendor': u'Snom',
                                                u'version': u'8.7.3.19'}]

            result = device_dao.mac_exists(mac)

            assert_that(result, equal_to(True))
            device_manager.find.assert_called_once_with({'mac': mac.lower()})


class TestDeviceDaoPluginExists(TestDeviceDao):

    def test_plugin_exists_no_plugin(self):
        plugin = 'null'

        with self.provd_managers() as (_, _, plugin_manager):
            plugin_manager.plugins.return_value = []

            result = device_dao.plugin_exists(plugin)

            assert_that(result, equal_to(False))
            plugin_manager.plugins.assert_called_once_with()

    def test_plugin_exists_with_a_plugin_installed(self):
        plugin = 'null'

        with self.provd_managers() as (_, _, plugin_manager):
            plugin_manager.plugins.return_value = ['null']

            result = device_dao.plugin_exists(plugin)

            assert_that(result, equal_to(True))
            plugin_manager.plugins.assert_called_once_with()


class TestDeviceDaoTemplateExists(TestDeviceDao):

    def test_template_id_exists_no_template(self):
        template_id = 'abcd1234'

        with self.provd_managers() as (_, config_manager, _):
            config_manager.find.return_value = []

            result = device_dao.template_id_exists(template_id)

            assert_that(result, equal_to(False))
            config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})

    def test_template_id_exists_with_a_template(self):
        template_id = 'abcd1234'

        with self.provd_managers() as (_, config_manager, _):
            config_manager.find.return_value = [{
                u'X_type': u'device',
                u'deletable': True,
                u'id': template_id,
                u'label': u'testtemplate',
                u'parent_ids': [],
                u'raw_config': {}}]

            result = device_dao.template_id_exists(template_id)

            assert_that(result, equal_to(True))
            config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})


class TestDeviceDaoDelete(TestDeviceDao):
    def test_delete(self):
        device_id = 'abc1234'
        device = Device(id=device_id)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_dao.delete(device)

            device_manager.remove.assert_called_once_with(device_id)
            config_manager.remove.assert_called_once_with(device_id)

    def test_delete_not_exist(self):
        device = Device(id='abcd')

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.remove.side_effect = HTTPError('', 404, '', '', StringIO(''))

            self.assertRaises(NotFoundError, device_dao.delete, device)
            device_manager.remove.assert_called_once_with(device.id)
            self.assertEquals(config_manager.remove.call_count, 0)

    def test_delete_with_error(self):
        device = Device(id='abcd')

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.remove.side_effect = Exception

            self.assertRaises(DataError, device_dao.delete, device)
            device_manager.remove.assert_called_once_with(device.id)
            self.assertEquals(config_manager.remove.call_count, 0)
