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

from hamcrest import *
from mock import Mock, patch
from urllib2 import HTTPError
from StringIO import StringIO
from contextlib import contextmanager

from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.exception import ElementDeletionError, ElementCreationError, \
    ElementNotExistsError, ElementEditionError


class TestDeviceDao(DAOTestCase):

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

    def test_get_no_device(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.side_effect = HTTPError('', 404, '', '', StringIO(''))

            self.assertRaises(ElementNotExistsError, device_dao.get, self.deviceid)
            device_manager.get.assert_called_once_with(self.deviceid)

    def test_total(self):
        total = 2

        devices = [Mock(), Mock()]

        with self.provd_managers() as (device_manager, _, _):
            device_manager.find.return_value = devices

            result = device_dao.total()
            assert_that(result, equal_to(total))
            device_manager.find.assert_called_once_with(fields=['id'])

    def test_get_no_template(self):
        properties = dict(self.device_properties)
        del properties['template_id']
        del properties['status']

        provd_device = dict(self.provd_device)
        del provd_device['config']

        expected_device = Device(**properties)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = provd_device

            device = device_dao.get(expected_device.id)

            assert_that(device, equal_to(expected_device))
            device_manager.get.assert_called_once_with(expected_device.id)
            assert_that(config_manager.get.call_count, equal_to(0))

    def test_get(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = self.provd_device
            config_manager.get.return_value = self.provd_config

            device = device_dao.get(self.deviceid)

            assert_that(device, equal_to(self.expected_device))
            device_manager.get.assert_called_once_with(self.deviceid)
            config_manager.get.assert_called_once_with(self.deviceid)

    def test_get_custom_template(self):
        properties = dict(self.device_properties)
        properties['template_id'] = 'mytemplate'

        expected_device = Device(**properties)

        provd_config = dict(self.provd_config)
        provd_config['configdevice'] = 'mytemplate'
        provd_config['parent_ids'].remove('defaultconfigdevice')
        provd_config['parent_ids'].append('mytemplate')

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = self.provd_device
            config_manager.get.return_value = provd_config

            device = device_dao.get(expected_device.id)

            print device.to_data_dict()
            print expected_device.to_data_dict()
            assert_that(device, equal_to(expected_device))
            device_manager.get.assert_called_once_with(expected_device.id)
            config_manager.get.assert_called_once_with(self.deviceid)

    def test_find_not_found(self):
        device_id = 'abcd'

        with self.provd_managers() as (device_manager, _, _):
            device_manager.find.return_value = []

            result = device_dao.find(device_id)
            device_manager.find.assert_called_once_with({'id': device_id})

            assert_that(result, none())

    def test_find_found(self):
        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = [self.provd_device]
            config_manager.get.return_value = self.provd_config

            result = device_dao.find(self.deviceid)

            assert_that(result, equal_to(self.expected_device))
            device_manager.find.assert_called_once_with({'id': self.deviceid})

    def test_find_all_no_devices(self):
        expected = []

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = []

            result = device_dao.find_all()

            assert_that(result, equal_to(expected))
            device_manager.find.assert_called_once_with()

    def test_find_all_with_parameters(self):
        expected = [self.expected_device]

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = [self.provd_device]
            config_manager.get.return_value = self.provd_config

            result = device_dao.find_all(order='ip', direction='desc', limit=1, skip=1)

            assert_that(result, equal_to(expected))
            device_manager.find.assert_called_once_with(sort=('ip', -1), limit=1, skip=1)

    def test_find_all_with_sort(self):
        expected = [self.expected_device]

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = [self.provd_device]
            config_manager.get.return_value = self.provd_config

            result = device_dao.find_all(order='ip')

            assert_that(result, equal_to(expected))
            device_manager.find.assert_called_once_with(sort=('ip', 1))

    @patch('xivo_dao.data_handler.device.dao.filter_list')
    def test_find_all_with_search(self, filter_list):
        expected = []
        search_term = 'search'

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = [self.provd_device]
            config_manager.get.return_value = self.provd_config
            filter_list.return_value = []

            result = device_dao.find_all(search=search_term)

            assert_that(result, equal_to(expected))
            filter_list.assert_called_once_with(search_term, [self.provd_device])
            device_manager.find.assert_called_once_with()

    def test_find_all_with_sort_and_order(self):
        expected = [self.expected_device]

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = [self.provd_device]
            config_manager.get.return_value = self.provd_config

            result = device_dao.find_all(order='ip', direction='asc')

            assert_that(result, equal_to(expected))
            device_manager.find.assert_called_once_with(sort=('ip', 1))

    def test_find_all(self):
        device1 = {
            'id': 'id1',
            'plugin': 'plugin1',
            'ip': 'ip1',
            'mac': 'mac1',
            'vendor': 'vendor1',
            'model': 'model1',
            'version': 'version1',
            'description': 'description1',
            'template_id': 'defaultconfigdevice',
            'status': 'configured'
        }

        device2 = {
            'id': 'id2',
            'plugin': 'plugin2',
            'ip': 'ip2',
            'mac': 'mac2',
            'vendor': 'vendor2',
            'model': 'model2',
            'version': 'version2',
            'description': 'description2',
            'template_id': 'defaultconfigdevice',
            'status': 'configured'
        }

        provd_device1 = {
            u'added': u'auto',
            u'configured': True,
            u'config': 'config1',
            u'id': 'id1',
            u'ip': 'ip1',
            u'mac': 'mac1',
            u'model': 'model1',
            u'plugin': 'plugin1',
            u'vendor': 'vendor1',
            u'version': 'version1',
            u'description': 'description1',
        }

        provd_device2 = {
            u'added': u'auto',
            u'configured': True,
            u'config': 'config2',
            u'id': 'id2',
            u'ip': 'ip2',
            u'mac': 'mac2',
            u'model': 'model2',
            u'plugin': 'plugin2',
            u'vendor': 'vendor2',
            u'version': 'version2',
            u'description': 'description2',
        }

        expected_device1 = Device(**device1)
        expected_device2 = Device(**device2)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.find.return_value = [provd_device1, provd_device2]
            config_manager.get.return_value = self.provd_config

            result = device_dao.find_all()

            assert_that(result, has_items(expected_device1, expected_device2))

            device_manager.find.assert_called_once_with()
            config_manager.get.assert_any_call(provd_device1['config'])
            config_manager.get.assert_any_call(provd_device2['config'])

    def test_filter_list_empty_list(self):
        devices = []
        expected = []
        search = 'toto'

        result = device_dao.filter_list(search, devices)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_wrong_search(self):
        devices = [self.provd_device]
        expected = []
        search = 'toto'

        result = device_dao.filter_list(search, devices)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_right_search(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = self.deviceid[0:5]

        result = device_dao.filter_list(search, devices)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_uppercase_search(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = self.deviceid.upper()

        result = device_dao.filter_list(search, devices)
        assert_that(result, equal_to(expected))

    def test_filter_list_one_device_trailing_spaces(self):
        devices = [self.provd_device]
        expected = [self.provd_device]
        search = ' %s ' % self.deviceid

        result = device_dao.filter_list(search, devices)
        assert_that(result, equal_to(expected))

    @patch('xivo_dao.data_handler.device.provd_builder.build_create')
    @patch('xivo_dao.data_handler.device.dao.generate_device_id')
    def test_create_device(self, generate_device_id, provd_build_create):
        device_id = 'abcd1234'
        device = Device()

        provd_device = Mock()
        provd_config = Mock()

        generate_device_id.return_value = device_id
        provd_build_create.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            result = device_dao.create(device)

            generate_device_id.assert_called_once_with()
            provd_build_create.assert_called_once_with(device)
            device_manager.update.assert_called_once_with(provd_device)
            config_manager.add.assert_called_once_with(provd_config)

            assert_that(result.id, equal_to(device_id))

    @patch('xivo_dao.data_handler.device.provd_builder.build_create')
    @patch('xivo_dao.data_handler.device.dao.generate_device_id')
    def test_create_with_device_manager_error(self, generate_device_id, provd_build_create):
        device_id = 'abcd1234'
        device = Device()

        provd_device = Mock()
        provd_config = Mock()

        generate_device_id.return_value = device_id
        provd_build_create.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.update.side_effect = Exception()

            self.assertRaises(ElementCreationError, device_dao.create, device)

            assert_that(config_manager.add.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.device.provd_builder.build_create')
    @patch('xivo_dao.data_handler.device.dao.generate_device_id')
    def test_create_with_config_manager_error(self, generate_device_id, provd_build_create):
        device_id = 'abcd1234'
        device = Device()

        provd_device = Mock()
        provd_config = Mock()

        generate_device_id.return_value = device_id
        provd_build_create.return_value = (provd_device, provd_config)

        with self.provd_managers() as (device_manager, config_manager, _):
            config_manager.add.side_effect = Exception()

            self.assertRaises(ElementCreationError, device_dao.create, device)
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

            self.assertRaises(ElementCreationError, device_dao.generate_device_id)
            device_manager.add.assert_called_once_with({})

    @patch('xivo_dao.data_handler.device.provd_builder.build_edit')
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

    @patch('xivo_dao.data_handler.device.provd_builder.build_edit')
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

    @patch('xivo_dao.data_handler.device.provd_builder.build_edit')
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

            self.assertRaises(ElementEditionError, device_dao.edit, device)

    @patch('xivo_dao.data_handler.device.provd_builder.build_edit')
    def test_edit_with_error_on_device_update(self, provd_build_edit):
        device_id = 'abc1234'
        device = Device(id=device_id)

        provd_build_edit.return_value = ({}, {})

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.get.return_value = {}
            config_manager.get.return_value = {}
            device_manager.update.side_effect = Exception

            self.assertRaises(ElementEditionError, device_dao.edit, device)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_mac_exists_no_mac(self, mock_device_manager):
        mac = 'FF:FF:FF:FF:FF'

        with self.provd_managers() as (device_manager, _, _):
            device_manager.find.return_value = []

            result = device_dao.mac_exists(mac)

            assert_that(result, equal_to(False))
            device_manager.find.assert_called_once_with({'mac': mac})

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_mac_exists_with_a_mac(self, mock_device_manager):
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
            device_manager.find.assert_called_once_with({'mac': mac})

    @patch('xivo_dao.helpers.provd_connector.plugin_manager')
    def test_plugin_exists_no_plugin(self, mock_plugin_manager):
        plugin = 'null'

        with self.provd_managers() as (_, _, plugin_manager):
            plugin_manager.plugins.return_value = []

            result = device_dao.plugin_exists(plugin)

            assert_that(result, equal_to(False))
            plugin_manager.plugins.assert_called_once_with()

    @patch('xivo_dao.helpers.provd_connector.plugin_manager')
    def test_plugin_exists_with_a_plugin_installed(self, mock_plugin_manager):
        plugin = 'null'

        with self.provd_managers() as (_, _, plugin_manager):
            plugin_manager.plugins.return_value = ['null']

            result = device_dao.plugin_exists(plugin)

            assert_that(result, equal_to(True))
            plugin_manager.plugins.assert_called_once_with()

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_template_id_exists_no_template(self, mock_config_manager):
        template_id = 'abcd1234'

        with self.provd_managers() as (_, config_manager, _):
            config_manager.find.return_value = []

            result = device_dao.template_id_exists(template_id)

            assert_that(result, equal_to(False))
            config_manager.find.assert_called_once_with({'X_type': 'device', 'id': template_id})

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_template_id_exists_with_a_template(self, mock_config_manager):
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

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_delete(self, mock_config_manager, mock_device_manager):
        device_id = 'abc1234'
        device = Device(id=device_id)

        with self.provd_managers() as (device_manager, config_manager, _):
            device_dao.delete(device)

            device_manager.remove.assert_called_once_with(device_id)
            config_manager.remove.assert_called_once_with(device_id)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_delete_not_exist(self, mock_config_manager, mock_device_manager):
        device = Device(id='abcd')

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.remove.side_effect = HTTPError('', 404, '', '', StringIO(''))

            self.assertRaises(ElementNotExistsError, device_dao.delete, device)
            device_manager.remove.assert_called_once_with(device.id)
            self.assertEquals(config_manager.remove.call_count, 0)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_delete_with_error(self, mock_config_manager, mock_device_manager):
        device = Device(id='abcd')

        with self.provd_managers() as (device_manager, config_manager, _):
            device_manager.remove.side_effect = Exception

            self.assertRaises(ElementDeletionError, device_dao.delete, device)
            device_manager.remove.assert_called_once_with(device.id)
            self.assertEquals(config_manager.remove.call_count, 0)
